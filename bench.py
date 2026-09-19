"""Benchmark tool: chunk data/thu-vien/*.md, load into EmbeddingStore, run the 5 group queries.

Run:
    python bench.py                          # one strategy (default: heading), full top-3 output
    python bench.py --strategy recursive     # another: fixed|sentence|recursive|heading
    python bench.py --all --out ket_qua_benchmark.txt   # all strategies + summary, saved to a file

Each member only changes the CHUNKER line in main(); everything else stays the same so that
results are comparable. Chunking happens here (outside the store): 1 chunk = 1 Document.

Two levels of grading (see docs/SCORING.md):
  - doc-level (naive)    : the gold document appears in the top-3.
  - content-level (real) : a retrieved chunk actually contains one of the `evidence` strings.
Score per query: 2 = evidence chunk is top-1, 1 = evidence chunk is top-2/3, 0 = absent.
The agent's own answer is not judged here (no real LLM is called): a score assumes the agent
answers correctly whenever the retrieved context contains the evidence.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    HeadingChunker,
    LocalEmbedder,
    RecursiveChunker,
    SemanticChunker,
    SentenceChunker,
    SlidingSentenceChunker,
    _mock_embed,
)

DATA_DIR = Path("data/thu-vien")
STRATEGIES = ["fixed", "sentence", "recursive", "heading", "semantic", "sliding"]

# Shared benchmark (same 5 queries as REPORT_NHOM section 3).
# `evidence` = substrings; a retrieved chunk containing ANY of them counts as relevant.
# `filter`   = metadata_filter used for the "with filter" run (None = no filter needed).
QUERIES = [
    {
        "q": "Mượn sách về nhà ở thư viện HUIT được tối đa mấy tài liệu và trong bao nhiêu ngày?",
        "filter": {"audience": "student"},
        "evidence": ["Số ngày mượn: 10", "Thời gian được mượn: 10 ngày"],
        "gold_doc": "huit-library-student",
        "gold_audience": "student",
    },
    {
        "q": "Quy trình mượn tài liệu về nhà ở thư viện Học viện Ngoại giao gồm những bước nào?",
        "filter": None,
        "evidence": ["B1: Trình thẻ thư viện", "B5: Đưa phiếu yêu cầu"],
        "gold_doc": "dav-library-borrowing",
        "gold_audience": "all",
    },
    {
        "q": "Muốn được sử dụng thư viện HUIT thì cần những điều kiện gì?",
        "filter": None,
        "evidence": ["Thứ nhất: Có thẻ thư viện"],
        "gold_doc": "huit-library-faq",
        "gold_audience": "all",
    },
    {
        "q": "Trả sách trễ hạn ở thư viện HUIT bị phạt bao nhiêu tiền mỗi ngày?",
        "filter": None,
        "evidence": ["1.000đ/tài liệu/ngày"],
        "gold_doc": "huit-library-faq",
        "gold_audience": "all",
    },
    {
        "q": "Thư viện PTIT cho mượn về nhà tối đa mấy cuốn, thời hạn mượn là bao lâu?",
        "filter": {"audience": "student"},
        "evidence": ["Số lượng tài liệu: 02 cuốn", "tối đa là 08 cuốn"],
        "gold_doc": "ptit-library-student",
        "gold_audience": "student",
    },
]
def make_chunker(strategy: str, chunk_size: int, embedder=None):
    return {
        "fixed": lambda: FixedSizeChunker(chunk_size=chunk_size, overlap=min(50, chunk_size // 4)),
        "sentence": lambda: SentenceChunker(max_sentences_per_chunk=3),
        "recursive": lambda: RecursiveChunker(chunk_size=chunk_size),
        "heading": lambda: HeadingChunker(chunk_size=chunk_size),
        "semantic": lambda: SemanticChunker(embedding_fn=embedder, chunk_size=chunk_size),
        "sliding": lambda: SlidingSentenceChunker(chunk_size=min(300, chunk_size), overlap_units=1),
    }[strategy]()


def parse_markdown(path: Path) -> tuple[dict, str]:
    """Split a .md file into (frontmatter metadata, body)."""
    _, front, body = path.read_text(encoding="utf-8").split("---", 2)
    raw_pairs = re.findall(r"^(\w+):\s*(.+)$", front, re.M)
    metadata = {k: v.strip().strip('"\'') for k, v in raw_pairs}
    return metadata, body.strip()


def build_documents(chunker) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, body = parse_markdown(path)
        for i, chunk in enumerate(chunker.chunk(body)):
            docs.append(
                Document(
                    id=f"{path.stem}#{i}",
                    content=chunk,
                    # frontmatter spread into every chunk so search_with_filter has something to filter on
                    metadata={**metadata, "doc_id": path.stem, "chunk_index": i},
                )
            )
    return docs


class CachedEmbedder:
    """Memoise embeddings by content so re-embedding identical text (across strategies) is free."""

    def __init__(self, inner) -> None:
        self.inner = inner
        self._backend_name = getattr(inner, "_backend_name", inner.__class__.__name__)
        self._cache: dict[str, list[float]] = {}

    def __call__(self, text: str) -> list[float]:
        if text not in self._cache:
            self._cache[text] = self.inner(text)
        return self._cache[text]


def make_embedder(provider: str) -> CachedEmbedder:
    if provider == "local":
        try:
            return CachedEmbedder(LocalEmbedder())
        except (ImportError, ModuleNotFoundError):
            print("Notice: sentence-transformers not installed. Falling back to mock embedder.\n")
            return CachedEmbedder(_mock_embed)
    return CachedEmbedder(_mock_embed)


def grade(results: list[dict], item: dict) -> dict:
    """Grade one top-k result list at both levels."""
    doc_hit = any(r["metadata"]["doc_id"] == item["gold_doc"] for r in results)
    content_rank = next(
        (rank for rank, r in enumerate(results, start=1) if any(e in r["content"] for e in item["evidence"])),
        None,
    )
    score = 0 if content_rank is None else (2 if content_rank == 1 else 1)
    top1_aud = results[0]["metadata"]["audience"] if results else "-"
    return {
        "doc_hit": doc_hit,
        "content_rank": content_rank,
        "score": score,
        "top1_audience": top1_aud,
        "top1_audience_ok": top1_aud == item["gold_audience"],
    }
def format_results(results: list[dict], item: dict) -> list[str]:
    lines = []
    for rank, r in enumerate(results, start=1):
        ok = any(e in r["content"] for e in item["evidence"])
        preview = r["content"].replace("\n", " ")[:100]
        lines.append(
            f"     {rank}. {'✓' if ok else '✗'} score={r['score']:.3f} doc_id={r['metadata']['doc_id']} "
            f"aud={r['metadata']['audience']} chunk={r['id']} | {preview}"
        )
    return lines
def run_strategy(strategy: str, chunk_size: int, top_k: int, embedder, chunker=None) -> tuple[list[str], dict]:
    """Run all 5 queries with one strategy. Returns (text lines, {query index -> grades})."""
    chunker = chunker or make_chunker(strategy, chunk_size, embedder=embedder)
    docs = build_documents(chunker)
    store = EmbeddingStore(collection_name=f"bench_{strategy}", embedding_fn=embedder)
    store.add_documents(docs)

    lines = [
        f"### strategy={strategy} chunk_size={chunk_size} embedder={embedder._backend_name}",
        f"Loaded {len({d.metadata['doc_id'] for d in docs})} files -> {store.get_collection_size()} chunks "
        f"(avg {sum(len(d.content) for d in docs) / max(1, len(docs)):.0f} chars)",
        "",
    ]
    grades: dict = {}
    for n, item in enumerate(QUERIES, start=1):
        lines += [f"Q{n}: {item['q']}", f"   gold_doc={item['gold_doc']}  evidence={item['evidence']}"]
        no_filter = store.search_with_filter(item["q"], top_k=top_k, metadata_filter=None)
        grades[n] = {"no_filter": grade(no_filter, item)}
        lines += ["   [không filter]"] + format_results(no_filter, item)
        if item["filter"]:
            filtered = store.search_with_filter(item["q"], top_k=top_k, metadata_filter=item["filter"])
            grades[n]["filter"] = grade(filtered, item)
            lines += [f"   [filter {item['filter']}]"] + format_results(filtered, item)
        lines.append("")
    return lines, grades


def summary_lines(strategy: str, grades: dict) -> list[str]:
    lines = [f"Tóm tắt strategy={strategy} (doc-level = gold doc trong top-3; content-level = chunk chứa đáp án)"]
    total = 0
    for n, g in grades.items():
        base = g["no_filter"]
        best = g.get("filter", base)  # score used for the group table: the filtered run when a filter is defined
        total += best["score"]
        text = (f"  Q{n}: không filter -> doc-level {'có' if base['doc_hit'] else 'không'}, "
                f"content-level rank={base['content_rank']}, điểm {base['score']}, audience top-1={base['top1_audience']}")
        if "filter" in g:
            f = g["filter"]
            text += (f" | có filter -> doc-level {'có' if f['doc_hit'] else 'không'}, "
                     f"content-level rank={f['content_rank']}, điểm {f['score']}")
        lines.append(text)
    lines.append(f"  Tổng điểm truy xuất (dùng kết quả có filter nếu câu có filter): {total}/10")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default=os.getenv("BENCH_STRATEGY", "sliding"), choices=STRATEGIES)
    parser.add_argument("--all", action="store_true", help="run every strategy and print a comparison")
    parser.add_argument("--out", help="also write the output to this file (UTF-8)")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--provider", default=os.getenv("EMBEDDING_PROVIDER", "local"), choices=["local", "mock"])
    args = parser.parse_args()

    embedder = make_embedder(args.provider)
    output: list[str] = []
    all_grades: dict = {}

    if args.all:
        for strategy in STRATEGIES:
            lines, all_grades[strategy] = run_strategy(strategy, args.chunk_size, args.top_k, embedder)
            output += lines
    else:
        CHUNKER = make_chunker(args.strategy, args.chunk_size, embedder=embedder)  # <- Khuê's strategy is sliding
        lines, all_grades[args.strategy] = run_strategy(args.strategy, args.chunk_size, args.top_k, embedder, CHUNKER)
        output += lines


    output.append("=" * 100)
    for strategy, grades in all_grades.items():
        output += summary_lines(strategy, grades) + [""]

    if args.all:
        output.append("So sánh doc-level (ngây thơ) và content-level (thật) trên cùng kết quả, mọi câu, mọi lần chạy:")
        for strategy, grades in all_grades.items():
            runs = [g[mode] for g in grades.values() for mode in ("no_filter", "filter") if mode in g]
            doc_hits = sum(r["doc_hit"] for r in runs)
            content_hits = sum(r["content_rank"] is not None for r in runs)
            output.append(f"  {strategy:9}: doc-level {doc_hits}/{len(runs)} | content-level {content_hits}/{len(runs)}")

    text = "\n".join(output)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"\n(saved to {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())


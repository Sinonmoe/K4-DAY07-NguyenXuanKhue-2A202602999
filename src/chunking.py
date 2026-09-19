from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Split on sentence boundaries: ". ", "! ", "? ", or ".\n"
        pattern = r'(?<=\. )|(?<=! )|(?<=\? )|(?<=\.\n)'
        raw_sentences = re.split(pattern, text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = " ".join(group).strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        if sep not in current_text:
            return self._split(current_text, next_seps)

        splits = current_text.split(sep)
        pieces: list[str] = []
        for s in splits:
            if len(s) > self.chunk_size:
                pieces.extend(self._split(s, next_seps))
            else:
                pieces.append(s)

        chunks: list[str] = []
        current_chunk = ""
        for piece in pieces:
            if not current_chunk:
                current_chunk = piece
            elif len(current_chunk) + len(sep) + len(piece) <= self.chunk_size:
                current_chunk += sep + piece
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = piece
        if current_chunk:
            chunks.append(current_chunk)

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = _dot(vec_a, vec_b)
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        overlap = max(0, min(50, chunk_size // 10))
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=overlap).chunk(text)
        sentences = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        strategies = {
            "fixed_size": fixed,
            "by_sentences": sentences,
            "recursive": recursive,
        }

        result = {}
        for name, chunks in strategies.items():
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            result[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return result


def _split_units(text: str) -> list[str]:
    """Split text into small units: every non-empty line, then sentences inside each line."""
    units: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            units.extend(s for s in re.split(r"(?<=[.!?])\s+", line) if s)
    return units


class HeadingChunker:
    """
    Split a Markdown document at its headings: one section = one chunk.

    Each chunk is prefixed with its heading path (e.g. "Nội quy > 2.2 Phòng đọc > Điều 13"),
    so a chunk never loses "which section is this?". A section longer than chunk_size is
    handed to RecursiveChunker and the heading path is re-attached to every sub-chunk.
    Headings with no body of their own only contribute to the path of the sections below.
    """

    HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def _sections(self, text: str) -> list[tuple[list[str], str]]:
        sections: list[tuple[list[str], str]] = []
        stack: list[tuple[int, str]] = []
        body: list[str] = []
        path: list[str] = []

        def flush() -> None:
            content = "\n".join(body).strip()
            if content:
                sections.append((list(path), content))
            body.clear()

        for line in text.splitlines():
            match = self.HEADING.match(line)
            if match:
                flush()
                level, title = len(match.group(1)), match.group(2).strip()
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, title))
                path[:] = [heading for _, heading in stack]
            else:
                body.append(line)
        flush()
        return sections

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        chunks: list[str] = []
        for path, body in self._sections(text):
            prefix = " > ".join(path)
            whole = f"{prefix}\n{body}" if prefix else body
            if len(whole) <= self.chunk_size:
                chunks.append(whole)
                continue
            room = max(50, self.chunk_size - len(prefix) - 1)
            for piece in RecursiveChunker(chunk_size=room).chunk(body):
                chunks.append(f"{prefix}\n{piece}" if prefix else piece)
        return chunks


class SemanticChunker:
    """
    Split text where the meaning changes, independent of headings.

    Every unit (line / sentence) is embedded; a chunk boundary is placed between two
    neighbouring units when their cosine similarity drops below mean - breakpoint_std * std
    of all neighbouring similarities. A chunk is also closed when it would exceed chunk_size,
    and no boundary is placed while the current chunk is shorter than min_chunk_chars.
    """

    def __init__(
        self,
        embedding_fn,
        chunk_size: int = 500,
        breakpoint_std: float = 0.5,
        min_chunk_chars: int = 80,
    ) -> None:
        self.embedding_fn = embedding_fn
        self.chunk_size = chunk_size
        self.breakpoint_std = breakpoint_std
        self.min_chunk_chars = min_chunk_chars

    def chunk(self, text: str) -> list[str]:
        units = _split_units(text) if text else []
        if not units:
            return []
        if len(units) == 1:
            return [units[0]]

        vectors = [self.embedding_fn(unit) for unit in units]
        sims = [compute_similarity(vectors[i], vectors[i + 1]) for i in range(len(units) - 1)]
        mean = sum(sims) / len(sims)
        std = math.sqrt(sum((s - mean) ** 2 for s in sims) / len(sims))
        threshold = mean - self.breakpoint_std * std

        chunks: list[str] = []
        current = [units[0]]
        length = len(units[0])
        for i in range(1, len(units)):
            too_long = length + 1 + len(units[i]) > self.chunk_size
            topic_shift = sims[i - 1] < threshold and length >= self.min_chunk_chars
            if too_long or topic_shift:
                chunks.append("\n".join(current))
                current, length = [units[i]], len(units[i])
            else:
                current.append(units[i])
                length += 1 + len(units[i])
        chunks.append("\n".join(current))
        return chunks


class SlidingSentenceChunker:
    """
    Small overlapping chunks built from consecutive sentences, inside each Markdown section.

    Each chunk holds consecutive units up to chunk_size characters (default 300, which fits the
    128-token limit of the multilingual MiniLM model); the next chunk restarts overlap_units units
    before the end of the previous one. The section's heading path is prepended to every chunk.
    """

    def __init__(self, chunk_size: int = 300, overlap_units: int = 1) -> None:
        self.chunk_size = chunk_size
        self.overlap_units = max(0, overlap_units)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        chunks: list[str] = []
        for path, body in HeadingChunker()._sections(text):
            prefix = " > ".join(path)
            head = f"{prefix}\n" if prefix else ""
            room = max(50, self.chunk_size - len(head))
            units: list[str] = []
            for unit in _split_units(body):
                # A single unit longer than the room is cut by RecursiveChunker first.
                units.extend(RecursiveChunker(chunk_size=room).chunk(unit) if len(unit) > room else [unit])

            i = 0
            while i < len(units):
                current, length, j = [], 0, i
                while j < len(units) and (not current or length + 1 + len(units[j]) <= room):
                    current.append(units[j])
                    length += len(units[j]) + (1 if len(current) > 1 else 0)
                    j += 1
                chunks.append(head + " ".join(current))
                if j >= len(units):
                    break
                i = max(j - self.overlap_units, i + 1)  # always move forward
        return chunks




# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Opera
**Thành viên:** Nguyễn Duy Phong, Tạ Duy Lâm, Nguyễn Xuân Khuê
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và dịch vụ thư viện đại học (thuộc chủ đề L3A: dịch vụ/quy định đại học), gồm nội quy, mượn trả, gia hạn, phạt quá hạn, đền bù tài liệu và giờ mở cửa.

**Tại sao nhóm chọn chủ đề này?**
> Thư viện là mảng có nhiều câu hỏi thực tế (mượn được bao nhiêu cuốn, bao nhiêu ngày, phạt bao nhiêu) và cùng một câu hỏi thường có đáp án khác nhau theo đối tượng: hạn mức của sinh viên khác giảng viên, ví dụ ở HUIT sinh viên mượn 10 ngày còn giảng viên 180 ngày. Vì vậy metadata `audience` có việc thật để lọc. Các nội quy lại có cấu trúc Điều/Mục đánh số, nên chunk theo tiêu đề được, và câu trả lời chuẩn trích được nguyên văn từ tài liệu.

### Danh sách tài liệu (Data Inventory)

Số ký tự tính trên phần nội dung đã làm sạch, không gồm frontmatter. Toàn bộ tài liệu lấy ngày 2026-09-19 từ 4 URL của 3 trường (PTIT, HUIT, Học viện Ngoại giao). PTIT, HUIT (trang quy định) và DAV mỗi nguồn được tách thành 3 file theo audience (chung, sinh viên, giảng viên); FAQ của HUIT giữ nguyên 1 file.

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `ptit-library-rules`: Nội quy thư viện PTIT, quy định chung | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / 817/QĐ-TTTV (14/10/2009) | 6.459 | audience=all, department=library, category=library, institution=ptit |
| 2 | `ptit-library-student`: Nội quy thư viện PTIT, hạn mức mượn của học viên và sinh viên | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / 817/QĐ-TTTV (14/10/2009) | 1.204 | audience=student, department=library, category=library, institution=ptit |
| 3 | `ptit-library-faculty`: Nội quy thư viện PTIT, hạn mức mượn của cán bộ và giảng viên | https://lib.ptit.edu.vn/noi-quy-thu-vien/ | 2026-09-19 / 817/QĐ-TTTV (14/10/2009) | 848 | audience=faculty, department=library, category=library, institution=ptit |
| 4 | `huit-library-rules`: Quy định sử dụng thư viện HUIT, quy định chung | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / not-stated | 12.840 | audience=all, department=library, category=library, institution=huit |
| 5 | `huit-library-student`: Quy định sử dụng thư viện HUIT, đối với sinh viên và học viên | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / not-stated | 1.982 | audience=student, department=library, category=library, institution=huit |
| 6 | `huit-library-faculty`: Quy định sử dụng thư viện HUIT, đối với giảng viên và viên chức | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 / not-stated | 1.469 | audience=faculty, department=library, category=library, institution=huit |
| 7 | `huit-library-faq`: Những câu hỏi thường gặp thư viện HUIT | https://thuvien.huit.edu.vn/Page/nhung-cau-hoi-thuong-gap | 2026-09-19 / not-stated | 12.990 | audience=all, department=library, category=library, institution=huit |
| 8 | `dav-library-borrowing`: Quy trình mượn trả tài liệu Học viện Ngoại giao, quy định chung | https://dav.edu.vn/quy-trinh-muon-tra-tai-lieu-4965/ | 2026-09-19 / not-stated | 4.596 | audience=all, department=library, category=library, institution=dav |
| 9 | `dav-library-student`: Quy trình mượn trả tài liệu Học viện Ngoại giao, hạn mức và lịch mượn của sinh viên và học viên | https://dav.edu.vn/quy-trinh-muon-tra-tai-lieu-4965/ | 2026-09-19 / not-stated | 1.400 | audience=student, department=library, category=library, institution=dav |
| 10 | `dav-library-faculty`: Quy trình mượn trả tài liệu Học viện Ngoại giao, hạn mức và lịch mượn của cán bộ và giảng viên | https://dav.edu.vn/quy-trinh-muon-tra-tai-lieu-4965/ | 2026-09-19 / not-stated | 1.211 | audience=faculty, department=library, category=library, institution=dav |

Tổng: 10 file, 44.999 ký tự. Phân bố `audience`: all 4, student 3, faculty 3. Ba cặp student/faculty (PTIT, HUIT, DAV) là nơi filter `audience` có tác dụng rõ nhất, vì cùng một câu hỏi về hạn mức mượn sách có đáp án khác nhau: sinh viên PTIT mượn 02 cuốn trong 07 ngày ở phòng đọc kho mở còn cán bộ, giảng viên mượn 03 cuốn trong 15 ngày; sinh viên HUIT mượn 10 ngày, giảng viên 180 ngày; ở DAV, giảng viên và cán bộ mượn tối đa 4 tài liệu còn sinh viên mượn 2 đến 3 tài liệu tùy đối tượng.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. Các trang đều mở công khai, thu thập bằng `scripts/fetch_public_pages.py` (kiểm tra robots.txt, giãn cách 10 giây). Có một nguồn ban đầu (trang quy chế đào tạo của FPT) bị robots.txt chặn nên đã bỏ, không dùng nguồn đó. Corpus chỉ chứa thông tin liên hệ của đơn vị (email, hotline thư viện), không có thông tin cá nhân.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. Số hiệu văn bản chỉ ghi khi trang nguồn nêu rõ (3/10 file, đều của PTIT: 817/QĐ-TTTV); 7 file còn lại ghi `not-stated`, không tự đặt số hiệu.

**Hạn chế đã biết của tập tài liệu:**
- Tài liệu lấy từ 3 trường khác nhau nên các giá trị (số ngày mượn, mức phạt) không so sánh trực tiếp giữa các trường được; metadata `institution` dùng để tách chúng.
- Hai trang của cùng trường HUIT mâu thuẫn nhau về gia hạn của sinh viên: trang "Quy định sử dụng thư viện" ghi gia hạn 1 lần (10 ngày), còn trang FAQ (câu 6) ghi mỗi lần gia hạn 10 ngày và không hạn chế số lần nếu sách còn trong kho. Nhóm giữ nguyên cả hai và tránh dùng điểm này làm câu hỏi đánh giá. Cả hai trang đều thống nhất mượn tối đa 3 tài liệu trong 10 ngày.
- Bảng hạn mức của DAV bị vỡ thành các dòng rời khi trích xuất; nhóm dựng lại thành bảng theo đúng thứ tự cột của nguồn. Dòng "Giảng viên thỉnh giảng, Sinh viên các khóa" là một dòng chung trong nguồn nên xuất hiện ở cả file student và file faculty.
- Trang FAQ của HUIT bị mất một số chữ cái đầu từ khi trích xuất (ví dụ "hực hiện"); nhóm đã khôi phục thành từ đúng và ghi chú trong file. FAQ giữ `audience=all` dù câu 6, 10, 15 nói về sinh viên, học viên.
- Nội dung được làm sạch bằng tay từ bản thô của crawler và đã đối chiếu từng câu với nguồn: không có con số nào trong file sạch mà bản thô không có. Mục 11.b của trang quy định HUIT trống trong nguồn và đã được ghi chú ngay trong file.
- Toàn bộ `category` đều là `library` nên trường này ít giá trị lọc trong corpus hiện tại; trường lọc hữu ích nhất là `audience` và `institution`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string, duy nhất, trùng tên file | `huit-library-student` | Định danh tài liệu; dùng để kiểm tra chunk trả về thuộc file nào và khớp `sources.csv`. |
| `title` | string | `Nội quy thư viện PTIT (quy định chung)` | Hiển thị nguồn khi trả lời và giúp người đọc kiểm chứng. |
| `source_url` | string (URL) | `https://lib.ptit.edu.vn/noi-quy-thu-vien/` | Truy vết về trang gốc, phục vụ trích dẫn và minh bạch nguồn. |
| `retrieved_at` | date `YYYY-MM-DD` | `2026-09-19` | Biết dữ liệu lấy khi nào; cần khi quy định thay đổi. |
| `document_version` | string | `817/QĐ-TTTV` hoặc `not-stated` | Phân biệt phiên bản văn bản; `not-stated` khi nguồn không nêu số hiệu. |
| `audience` | enum: `student` / `faculty` / `staff` / `all` | `student` | Trường lọc chính: `metadata_filter={"audience": "student"}` loại hạn mức của giảng viên khỏi top-k (ví dụ HUIT 10 ngày và 180 ngày). |
| `department` | string | `library` | Lọc theo đơn vị phụ trách; toàn corpus cùng một giá trị nên hữu ích khi mở rộng sang mảng khác. |
| `category` | string | `library` | Lọc theo mảng dịch vụ; hiện chỉ có một giá trị nhưng giữ để corpus có thể mở rộng (học phí, ký túc xá...). |
| `language` | string | `vi` | Lọc theo ngôn ngữ; toàn bộ corpus tiếng Việt, hữu ích nếu sau này mở rộng thêm nguồn tiếng Anh. |
| `institution` | string | `ptit`, `huit`, `dav` | Tách quy định theo trường, vì mỗi trường có số liệu khác nhau, tránh trộn đáp án giữa các trường. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=500)` trên 3 tài liệu, chỉ lấy phần thân (đã bỏ frontmatter YAML):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `ptit-library-rules` (6.459 ký tự) | FixedSizeChunker (`fixed_size`) | 15 | 477 | Kém: 13/15 chunk kết thúc giữa câu hoặc giữa từ, không theo ranh giới Điều. |
| | SentenceChunker (`by_sentences`) | 22 | 291 | Vừa: chunk luôn kết thúc ở cuối câu nhưng gom 3 câu bất kể thuộc Điều nào và không mang tiêu đề mục. |
| | RecursiveChunker (`recursive`) | 17 | 378 | Khá: cắt theo đoạn/dòng nên thường giữ trọn một Điều, nhưng tiêu đề mục vẫn tách khỏi phần thân. |
| `huit-library-faq` (12.990 ký tự) | FixedSizeChunker (`fixed_size`) | 29 | 496 | Kém: 26/29 chunk bị cắt giữa câu, một câu trả lời FAQ dễ bị chẻ đôi. |
| | SentenceChunker (`by_sentences`) | 32 | 404 | Vừa: có chunk dài tới 1.777 ký tự vì các gạch đầu dòng không có dấu kết câu bị dồn thành một "câu". |
| | RecursiveChunker (`recursive`) | 36 | 359 | Khá: giữ nguyên từng gạch đầu dòng và đoạn; câu hỏi và câu trả lời có thể rơi vào hai chunk khác nhau. |
| `dav-library-borrowing` (4.596 ký tự) | FixedSizeChunker (`fixed_size`) | 11 | 463 | Kém: 10/11 chunk bị cắt giữa câu; quy trình B1 đến B8 bị cắt ngang một bước. |
| | SentenceChunker (`by_sentences`) | 18 | 253 | Vừa: chia quy trình B1 đến B8 thành 3 chunk ở ranh giới bước, nhưng chunk nhỏ và không có tiêu đề "7. Quy trình mượn tài liệu". |
| | RecursiveChunker (`recursive`) | 12 | 381 | Khá: B1 đến B5 và B6 đến B8 nằm ở hai chunk liền kề, mỗi bước còn nguyên vẹn. |

Để so sánh, chunker theo tiêu đề (`HeadingChunker`, chunk_size=500) tạo 29, 46 và 18 chunk cho ba tài liệu trên; mỗi chunk mang theo đường dẫn tiêu đề (ví dụ "Nội quy thư viện PTIT > 2. Nội quy phòng đọc > Điều 13").

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Tạ Duy Lâm**
- **Loại chiến lược:** custom, `HeadingChunker` (chunk theo tiêu đề/mục Markdown, chunk_size=500).
- **Mô tả & lý do chọn cho chủ đề này:** Nội quy thư viện đã được chia sẵn thành Điều/Mục, mỗi mục là một đơn vị ngữ nghĩa trọn vẹn (ví dụ "Điều 13", "5. Quy định mượn/trả tài liệu"), nên tách trước mỗi dòng heading và coi mỗi section là một chunk. Mỗi chunk được gắn đường dẫn tiêu đề (ví dụ "Nội quy thư viện PTIT > 2. Nội quy phòng đọc > Điều 13") để chunk không mất ngữ cảnh "đây là mục nói về gì"; section nào dài hơn ngưỡng thì hạ xuống `RecursiveChunker` và gắn lại đường dẫn tiêu đề cho từng mảnh con. Heading không có phần thân chỉ đóng góp vào đường dẫn của các mục con.
- **Code snippet (nếu custom):**
```python
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
```

**Thành viên 2 — Nguyễn Duy Phong**
- **Loại chiến lược:** custom, chunk theo ngữ nghĩa (semantic chunking), độc lập với tiêu đề.
- **Mô tả & lý do chọn:** Tách văn bản thành câu, embed từng câu bằng cùng model đang dùng, rồi chỉ cắt chunk ở chỗ độ giống (cosine) giữa hai câu liền kề tụt xuống dưới một ngưỡng (ví dụ thấp hơn mức trung bình trừ một độ lệch chuẩn), đồng thời khống chế chunk không dài quá khoảng 500 ký tự. Lý do chọn: `heading` phụ thuộc vào việc tài liệu có tiêu đề sạch; semantic chunking không cần tiêu đề nên cũng dùng được cho các đoạn dài không có heading (ví dụ mục 1 của HUIT gồm 16 gạch đầu dòng a đến p) và cho các nguồn ngoài Markdown. Giả thuyết cần kiểm chứng: các bước liền nhau của một quy trình (câu 2, B1 đến B8 của DAV) có nghĩa gần nhau nên sẽ nằm chung chunk hơn so với `heading` đang tách thành 3 chunk; rủi ro là các câu số liệu ngắn ("Số ngày mượn: 10") ít mang nghĩa nên bị gộp nhầm sang chunk khác.
- **Cách chạy:** `SemanticChunker` nằm trong `src/chunking.py` và đã được nối vào `bench.py` (chỉ đổi dòng chọn chunker): `python bench.py --strategy semantic`. Ngưỡng cắt = trung bình độ giống trừ 0,5 độ lệch chuẩn, chunk tối đa 500 ký tự, tối thiểu 80 ký tự trước khi cho phép cắt.
- **Code snippet (nếu custom):**
```python
def _split_units(text: str) -> list[str]:
    """Split text into small units: every non-empty line, then sentences inside each line."""
    units: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            units.extend(s for s in re.split(r"(?<=[.!?])\s+", line) if s)
    return units


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
```
- **Kết quả:** 171 chunk (trung bình 260 ký tự), 5/10 điểm truy xuất. Câu 4 và câu 5 đạt 2 điểm (chunk đúng ở hạng 1; câu 5 không lọc cũng đã đúng đối tượng), câu 1 được 1 điểm (hạng 3 khi có filter), câu 2 và câu 3 được 0 điểm. Câu 2 hỏng vì các chunk semantic không mang đường dẫn tiêu đề: top-3 là phần mở đầu của `dav-library-student`, `dav-library-faculty` (có nhắc tên "Học viện Ngoại giao" và "mượn trả tài liệu") chứ không phải chunk chứa các bước B1 đến B8. Giả thuyết ban đầu (các bước liền nhau sẽ nằm chung chunk) chưa được kiểm chứng vì chunk chứa quy trình không lọt top-3. (Kết quả chạy bằng `bench.py` chung, cùng embedding và cùng 5 câu, do Lâm chạy thay; Phong có thể chạy lại bằng lệnh trên để xác nhận.)

**Thành viên 3 — Nguyễn Xuân Khuê**
- **Loại chiến lược:** custom, chunk nhỏ có chồng lấn theo câu (sentence-window với overlap), gắn đường dẫn tiêu đề.
- **Mô tả & lý do chọn:** Chia mỗi mục thành các chunk nhỏ khoảng 300 ký tự, gồm vài câu liên tiếp, hai chunk kề nhau chồng lấn 1 câu, và gắn đường dẫn tiêu đề của mục vào đầu mỗi chunk như `heading`. Lý do chọn: model `paraphrase-multilingual-MiniLM-L12-v2` chỉ đọc tối đa 128 token nên chunk gần 500 ký tự có thể bị cắt đuôi khi embed, và chunk nhỏ làm điểm tương đồng tập trung hơn vào một ý; overlap giữ lại thông tin nằm ở ranh giới giữa hai chunk (như quy trình B1 đến B8 của DAV, đang bị `heading` chia ở B3/B4 và B6/B7). Giả thuyết cần kiểm chứng: cải thiện câu 2 và có thể cứu câu 3 (failure case) vì chunk FAQ chứa đáp án sẽ ngắn và ít bị pha loãng; đánh đổi là số chunk tăng (từ 165 lên khoảng 250 đến 300), tốn thêm chi phí embedding và top-3 có thể chứa nhiều chunk trùng nội dung của cùng một mục.
- **Cách chạy:** `SlidingSentenceChunker` nằm trong `src/chunking.py` và đã được nối vào `bench.py` (chỉ đổi dòng chọn chunker): `python bench.py --strategy sliding`. Chunk tối đa 300 ký tự (gồm cả đường dẫn tiêu đề), overlap 1 câu.
- **Code snippet (nếu custom):**
```python
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
```
- **Kết quả:** 370 chunk (trung bình 249 ký tự), 6/10 điểm truy xuất. Câu 1 và câu 4 đạt 2 điểm, câu 2 và câu 5 được 1 điểm (câu 2: hạng 2; câu 5: hạng 2 khi có filter, hạng 3 khi không lọc), câu 3 được 0 điểm. Số chunk gấp hơn 2 lần `heading` (370 so với 165). Giả thuyết cứu được câu 3 không đúng: chunk đúng xếp hạng 35/370, tệ hơn `heading` (23/165) và `fixed` (5/104). (Kết quả chạy bằng `bench.py` chung, cùng embedding và cùng 5 câu, do Lâm chạy thay; Khuê có thể chạy lại bằng lệnh trên để xác nhận.)

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tạ Duy Lâm | `HeadingChunker` (theo tiêu đề) | 7/10 điểm truy xuất (4/5 câu có chunk chứa đáp án trong top-3; chưa tính câu trả lời của agent) | Đường dẫn tiêu đề giúp chunk khớp câu hỏi theo chủ đề mục; đúng ranh giới Điều nên ít cắt ngang một điều khoản. | Section dài bị chia thành nhiều chunk (quy trình 8 bước của DAV nằm ở 3 chunk); chunk nhỏ, giống nhau về chủ đề nên điểm sát nhau. |
| Nguyễn Duy Phong | Semantic chunking (theo độ giống giữa các câu liền kề) | 5/10 (171 chunk; 5/7 lượt có chunk chứa đáp án trong top-3) | Không cần tiêu đề; câu 5 không lọc vẫn xếp chunk sinh viên ở hạng 1; câu 4 ở hạng 1. | Chunk không mang đường dẫn tiêu đề nên câu 2 nhầm sang phần mở đầu của file khác (0 điểm); phải embed từng câu; kết quả phụ thuộc ngưỡng cắt. |
| Nguyễn Xuân Khuê | Chunk nhỏ chồng lấn theo câu (~300 ký tự, overlap 1 câu) kèm đường dẫn tiêu đề | 6/10 (370 chunk; 6/7 lượt có chunk chứa đáp án trong top-3) | Cứu được câu 2 (hạng 2) nhờ overlap; câu 1 và câu 4 ở hạng 1; chunk vừa giới hạn 128 token. | Số chunk nhiều gấp hơn 2 lần `heading`; câu 5 chỉ được 1 điểm (chunk đúng ở hạng 2-3); không cứu được câu 3 (hạng 35/370). |

Bên cạnh `heading`, `bench.py --all` chạy thêm năm chiến lược còn lại (ba chiến lược có sẵn của repo và hai chiến lược của Phong, Khuê) trên cùng bộ tài liệu, cùng 5 câu và cùng embedding `paraphrase-multilingual-MiniLM-L12-v2` (kết quả đầy đủ trong `ket_qua_benchmark.txt`). Điểm tính theo `docs/SCORING.md` ở mức nội dung (chunk có thật sự chứa đáp án hay không), dùng kết quả có filter với câu có filter, chưa tính câu trả lời của agent vì chưa gọi LLM thật:

| Chiến lược | Số chunk | Điểm truy xuất (/10) | Doc-level (gold doc trong top-3) | Content-level (chunk chứa đáp án) |
|-----------|----------|----------------------|-----------|----------|
| `fixed` (FixedSizeChunker, 500, overlap 50) | 104 | 4 | 5/7 lượt chạy | 5/7 |
| `sentence` (SentenceChunker, 3 câu) | 136 | 2 | 4/7 | 2/7 |
| `recursive` (RecursiveChunker, 500) | 125 | 4 | 5/7 | 5/7 |
| `heading` (HeadingChunker, 500) | 165 | 7 | 6/7 | 6/7 |
| `semantic` (SemanticChunker, 500) | 171 | 5 | 4/7 | 5/7 |
| `sliding` (SlidingSentenceChunker, 300, overlap 1) | 370 | 6 | 5/7 | 6/7 |

("7 lượt chạy" = 5 câu, trong đó 2 câu có filter được chạy hai lần.)

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `HeadingChunker` cho điểm cao nhất (7/10), tiếp theo là `sliding` (6), `semantic` (5), `fixed` và `recursive` (4), `sentence` (2). Văn bản quy định vốn được soạn theo mục nên chunk theo mục giữ trọn một điều khoản, và đường dẫn tiêu đề trong mỗi chunk giúp truy xuất khớp câu hỏi (tên trường, "Điều 22", "5. Quy định mượn/trả tài liệu"). Hai chiến lược có đường dẫn tiêu đề (`heading`, `sliding`) đứng đầu, còn `semantic` (không có tiêu đề) mất điểm ở câu 2, cho thấy nhãn ngữ cảnh quan trọng hơn cách cắt chính xác. `fixed` cắt ngang câu và ngang mục, `sentence` gom 3 câu bất kể mục nên chunk có số liệu ("02 cuốn") mất nhãn cho biết đó là của ai. Đây chỉ là kết quả của 5 câu hỏi, một embedder và một ngưỡng chunk_size, nên chênh lệch nhỏ (7 so với 6, hoặc 4 so với 4) chưa đủ kết luận; chênh lệch đáng tin nhất là `heading` so với `sentence`.

### Phân tích lỗi (Failure case)

**Câu hỏi hỏng:** Câu 3, "Muốn được sử dụng thư viện HUIT thì cần những điều kiện gì?". Cả 6 chiến lược đều được 0 điểm: top-3 không có chunk nào chứa đáp án. Hạng của chunk đúng (`huit-library-faq`, câu 5 "Để được sử dụng Thư viện cần điều kiện gì?") lần lượt là: `fixed` 5/104, `semantic` 5/171, `sentence` 7/136, `recursive` 11/125, `heading` 23/165, `sliding` 35/370. Ở mọi chiến lược, hạng 1 đều là chunk của `huit-library-rules` (điểm 0,80 đến 0,84), riêng `heading` cho chunk đúng điểm 0,734 so với 0,821 của hạng 1.

**Vì sao:** cosine đo mức giống nhau về chủ đề, không đo chunk nào thật sự trả lời câu hỏi. Câu hỏi nói về "sử dụng thư viện HUIT", nên các chunk mở đầu và chunk quy định chung của trang "Quy định sử dụng thư viện" giống hơn chunk FAQ dù chunk FAQ mới có đáp án ba điều kiện. Hai trang HUIT trùng chủ đề nên các chunk cạnh tranh nhau. Đáng chú ý là hai chiến lược tốt nhất ở các câu khác (`heading`, `sliding`) lại xếp chunk đúng thấp nhất ở câu này (hạng 23 và 35); nhiều khả năng do đường dẫn tiêu đề của chunk quy định chung ("Quy định sử dụng thư viện HUIT (quy định chung) > ...") chứa cụm từ trùng với câu hỏi nên làm tăng điểm của chunk sai (đây là suy đoán, chưa kiểm chứng riêng). Model `paraphrase-multilingual-MiniLM-L12-v2` chỉ đọc tối đa 128 token, nhưng chunk FAQ này dài khoảng 355 ký tự (khoảng 108 token) nên không phải bị cắt đuôi.

**Đề xuất sửa:** (1) kết hợp tìm kiếm từ khóa với vector (hybrid) hoặc rerank, vì chunk đúng chứa cụm "điều kiện" và "sử dụng thư viện" ngay trong tiêu đề; (2) tránh trùng nội dung giữa hai trang cùng trường, bỏ hoặc giảm trọng số trang quy định chung khi đã có FAQ; (3) thêm metadata theo mục (ví dụ `topic`) để lọc. Hai đề xuất đơn giản đã được thử và không đủ: giảm `chunk_size` xuống 300 ký tự (`sliding`) không cứu được (hạng 35/370), và tăng `top_k` cũng không đủ vì chunk đúng ở hạng 23 với `heading`. Các đề xuất (1) và (3) chưa thử.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mượn sách về nhà ở thư viện HUIT được tối đa mấy tài liệu và trong bao nhiêu ngày? **(dùng `metadata_filter={"audience": "student"}`)** | Sinh viên, học viên: tối đa 3 tài liệu, mượn trong 10 ngày. (Cùng trang, giảng viên và viên chức được mượn 3 tài liệu trong 180 ngày.) | `huit-library-student`, mục "5. Quy định mượn/trả tài liệu (đối với sinh viên)"; `huit-library-faq`, câu 6. |
| 2 | Quy trình mượn tài liệu về nhà ở thư viện Học viện Ngoại giao gồm những bước nào? | 8 bước: B1 trình thẻ thư viện cho thủ thư ở quầy lưu hành tầng 3; B2 tra mã tài liệu; B3 lấy phiếu yêu cầu mượn; B4 ghi đầy đủ thông tin trên phiếu; B5 đưa phiếu để thủ thư lấy tài liệu; B6 nhận và kiểm tra tình trạng tài liệu; B7 nếu muốn mượn về nhà thì đăng ký và làm theo hướng dẫn của thủ thư; B8 nhận lại thẻ thư viện. | `dav-library-borrowing`, mục "7. Quy trình mượn tài liệu". |
| 3 | Muốn được sử dụng thư viện HUIT thì cần những điều kiện gì? | Ba điều kiện: (1) có thẻ thư viện (thẻ giảng viên, viên chức, học viên, sinh viên, học sinh đồng thời là thẻ thư viện; người ngoài trường do Thư viện cấp); (2) tham gia lớp tập huấn sử dụng thư viện; (3) tuân thủ các quy định sử dụng thư viện. | `huit-library-faq`, câu 5 "Để được sử dụng Thư viện cần điều kiện gì?". |
| 4 | Trả sách trễ hạn ở thư viện HUIT bị phạt bao nhiêu tiền mỗi ngày? | Tài liệu mượn về nhà (nhãn màu trắng): 1.000đ/tài liệu/ngày; tài liệu mượn đọc trong ngày (nhãn màu cam): 5.000đ/tài liệu/ngày. | `huit-library-faq`, câu 7 "Nếu trả sách trễ hạn phải nộp phạt như thế nào?". |
| 5 | Thư viện PTIT cho mượn về nhà tối đa mấy cuốn, thời hạn mượn là bao lâu? **(dùng `metadata_filter={"audience": "student"}`)** | Học viên, sinh viên: ở phòng đọc kho mở mượn 02 cuốn trong 07 ngày (Điều 13); ở phòng mượn, sinh viên hệ chính quy mượn tối đa 08 cuốn trong 01 học kì (150 ngày), sinh viên hệ khác, học viên cao học và nghiên cứu sinh mượn 05 cuốn trong 150 ngày và phải ký cược tiền (Điều 22). (Cán bộ, giảng viên: 03 cuốn, 15 ngày ở kho mở và 07 cuốn, 60 ngày ở phòng mượn.) | `ptit-library-student`, Điều 13 và Điều 22 (phần dành cho học viên, sinh viên). |

Bộ câu hỏi gồm 3 câu tra số liệu (1, 4, 5), 1 câu hỏi quy trình (2) và 1 câu hỏi điều kiện dạng liệt kê (3). Hai câu 1 và 5 không nêu rõ người hỏi là ai trong khi corpus có cặp tài liệu cùng chủ đề nhưng khác đối tượng và khác đáp án (`*-student` và `*-faculty`), nên dùng `metadata_filter={"audience": "student"}`. Câu 5 là câu thể hiện rõ nhất: khi chạy `bench.py` với chunker theo tiêu đề và embedding `paraphrase-multilingual-MiniLM-L12-v2`, không lọc thì chunk đứng đầu là `ptit-library-faculty` (score 0,839, hạn mức của cán bộ, giảng viên), còn lọc `audience=student` thì chỉ còn chunk của sinh viên. Câu 1 yếu hơn: không lọc, chunk của giảng viên (180 ngày) chỉ xuất hiện ở hạng 4 trong 5 kết quả đầu và không lọt top-3. Gold answer đều trích được nguyên văn từ tài liệu trong nhóm, không suy đoán. Nhóm cố ý không hỏi về gia hạn của sinh viên HUIT vì hai trang nguồn của HUIT mâu thuẫn nhau ở điểm này.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mượn sách về nhà ở thư viện HUIT được tối đa mấy tài liệu và trong bao nhiêu ngày? | `heading`, `sliding` (chunk đúng ở hạng 1, 2 điểm) | Có với cả 6 chiến lược khi lọc `audience=student` (`fixed`, `recursive`, `semantic` ở hạng 3, `sentence` ở hạng 2) | Chunk FAQ (`audience=all`) cũng chứa đáp án 10 ngày, nên `recursive` không lọc đạt hạng 1 (2 điểm) nhưng lọc thì tụt xuống hạng 3 (1 điểm); filter cũng kéo vào hai chunk PTIT không liên quan. |
| 2 | Quy trình mượn tài liệu về nhà ở thư viện Học viện Ngoại giao gồm những bước nào? | `sliding` (hạng 2) và `heading` (hạng 3), đều 1 điểm | Chỉ `heading` và `sliding`; `fixed`, `recursive` có chunk của đúng tài liệu DAV nhưng không chứa bước nào; `sentence` và `semantic` không lấy được chunk nào của `dav-library-borrowing` (`semantic` lấy nhầm phần mở đầu của `dav-library-student` và `dav-library-faculty`) | Quy trình 8 bước bị chia thành nhiều chunk (`heading`: B1-B3, B4-B6, B7-B8), nên top-3 chỉ có một phần các bước; `semantic` nhầm sang phần mở đầu của `dav-library-student` và `dav-library-faculty`. |
| 3 | Muốn được sử dụng thư viện HUIT thì cần những điều kiện gì? | Không có | Không (0 điểm với cả 6 chiến lược) | Failure case, xem "Phân tích lỗi" ở mục 2. |
| 4 | Trả sách trễ hạn ở thư viện HUIT bị phạt bao nhiêu tiền mỗi ngày? | `heading`, `semantic`, `sliding` (hạng 1, 2 điểm) | Có với cả 6 chiến lược (`fixed`, `sentence`, `recursive` ở hạng 2) | Tiêu đề câu 7 của FAQ ("Nếu trả sách trễ hạn phải nộp phạt...") khớp trực tiếp với câu hỏi. |
| 5 | Thư viện PTIT cho mượn về nhà tối đa mấy cuốn, thời hạn mượn là bao lâu? | `fixed`, `recursive`, `heading`, `semantic` (hạng 1, 2 điểm, có filter) | Có với 5/6 chiến lược khi lọc `audience=student` (`sliding` ở hạng 2); `sentence` không (0 điểm dù có filter) | Không lọc: chunk đứng đầu là của `ptit-library-faculty` (03 cuốn, 15 ngày) với `fixed`, `recursive`, `heading` và `sliding`, tức sai đối tượng. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở câu 5: không lọc thì 4/6 chiến lược (`fixed`, `recursive`, `heading`, `sliding`) xếp chunk hạn mức của giảng viên (`ptit-library-faculty`) ở hạng 1, tức trả lời sai đối tượng; lọc `audience=student` đưa chunk đúng lên hạng 1 và tăng điểm từ 1 lên 2 ở `fixed`, `recursive`, `heading` (ở `sliding` chunk đúng chỉ từ hạng 3 lên hạng 2, vẫn 1 điểm). Câu 1 cho kết quả trái chiều: filter cứu `sentence` (0 lên 1 điểm) nhưng làm `recursive` tệ đi (hạng 1 xuống hạng 3, từ 2 xuống 1 điểm) vì loại chunk FAQ có `audience=all` chứa đúng đáp án. Đây là đánh đổi của filter cứng: tăng precision theo đối tượng nhưng loại luôn các tài liệu `all` chứa thông tin cần thiết, và bên trong nhóm `student` các trường khác vẫn lọt vào (hai chunk PTIT ở câu 1). Hai câu này thỏa yêu cầu của lab vì kết quả có và không có filter khác nhau (câu 5: hạng 1 khác đối tượng).

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Chấm hai mức cho kết quả khác nhau: `sentence` có gold doc trong top-3 ở 4/7 lượt (doc-level) nhưng chỉ 2/7 lượt có chunk thật sự chứa đáp án; ngược lại `semantic` (4/7 so với 5/7) và `sliding` (5/7 so với 6/7) có chunk đúng từ một tài liệu khác (FAQ) dù gold doc không nằm trong top-3. Chỉ kiểm `doc_id` vừa thổi phồng vừa bỏ sót kết quả.
> 2. Filter `audience` sửa được lỗi sai đối tượng (câu 5) nhưng có thể làm mất chunk đúng nằm trong tài liệu `audience=all` (câu 1 với `recursive`).
> 3. Failure case câu 3: cả 6 chiến lược đều 0 điểm; chunk có đáp án xếp hạng từ 5 đến 35 vì cosine đo độ giống chủ đề, không đo mật độ thông tin trả lời được, và chunk nhỏ (`sliding`) không cứu được.
> 4. Nhãn ngữ cảnh quan trọng hơn cách cắt: hai chiến lược có đường dẫn tiêu đề (`heading`, `sliding`) đạt 7 và 6 điểm, còn `semantic` không có tiêu đề bị nhầm ở câu 2.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng 10 tài liệu và 5 câu hỏi, chỉ đổi cách chunk đã làm điểm truy xuất thay đổi từ 2/10 (`sentence`) đến 7/10 (`heading`), nên cách chia tài liệu quan trọng ngang chọn embedding. Chunk theo mục thắng vì văn bản quy định đã được chia mục sẵn, nhưng nó không cứu được câu 3, tức là chia chunk tốt chưa đủ nếu xếp hạng vẫn chỉ dựa trên độ giống chủ đề. (Toàn bộ số liệu chạy bằng `bench.py` chung; kết quả của `semantic` (Phong) và `sliding` (Khuê) do Lâm chạy thay, hai bạn chạy lại bằng lệnh trong khối của mình để xác nhận.)

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Chọn nguồn ít trùng nội dung hơn (hai trang HUIT nói lại cùng quy định, làm chunk cạnh tranh nhau), gán `audience` mịn hơn cho các trang FAQ có cả nội dung sinh viên lẫn chung, và thêm metadata theo mục (ví dụ `topic=phạt`, `topic=thẻ thư viện`) để lọc hoặc rerank được. Ngoài ra nên thử hybrid search hoặc rerank và `chunk_size` nhỏ hơn cho embedding 128 token.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 (theo chunk chứa đáp án; chưa gồm câu trả lời của agent) |
| Thuyết trình (Demo) | chưa demo (tối đa 5) |
| **Tổng phần nhóm** | **29 / 35, chưa gồm điểm demo (tối đa 40)** |

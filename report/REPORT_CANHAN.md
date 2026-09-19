# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Xuân Khuê
**Nhóm:** Opera
**Ngày:** 19/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Hai vector embedding cùng hướng trong không gian đa chiều, biểu thị sự tương đồng cao về mặt ý nghĩa ngữ nghĩa (semantic meaning) và ngữ cảnh, bất kể khác biệt về câu từ hay độ dài.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên có thể nộp đơn xin gia hạn thời gian đóng học phí tại phòng Đào tạo trước ngày 30/10."
- Câu B: "Hạn cuối để người học gửi yêu cầu hoãn nộp học phí lên văn phòng học vụ là ngày 30 tháng 10."
- Tại sao tương đồng: Cùng một nội dung thủ tục và thời hạn học vụ, chỉ khác cách diễn đạt từ ngữ đồng nghĩa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên có thể nộp đơn xin gia hạn thời gian đóng học phí tại phòng Đào tạo trước ngày 30/10."
- Câu B: "Đội tuyển bóng đá nam vừa giành chức vô địch cúp quốc gia sau loạt sút luân lưu kịch tính."
- Tại sao khác: Hai miền chủ đề hoàn toàn tách biệt (quy định học vụ vs thể thao), không chung ngữ cảnh hay thực thể nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity chỉ đo góc giữa các vector mà độc lập với độ lớn (độ dài) của vector. Khi hai văn bản cùng chủ đề nhưng có độ dài khác nhau (ví dụ tóm tắt ngắn vs văn bản chi tiết), khoảng cách Euclid bị chi phối mạnh bởi tần suất từ và độ dài, trong khi Cosine similarity vẫn nhận diện chính xác sự tương đồng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Áp dụng công thức:
> $$\text{Số lượng chunk} = \left\lceil \frac{\text{Độ dài tài liệu} - \text{Độ chồng chéo}}{\text{Kích thước chunk} - \text{Độ chồng chéo}} \right\rceil$$
> - Độ dài tài liệu ($L$) = $10{,}000$ ký tự
> - Kích thước chunk ($C$) = $500$ ký tự
> - Độ chồng chéo ($O$) = $50$ ký tự
> - Bước nhảy giữa các chunk: $S = C - O = 500 - 50 = 450$ ký tự
>
> Thay số vào công thức:
> $$\text{Số lượng chunk} = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \lceil 22.11 \rceil = 23$$
> *(Bao gồm 22 chunk đầy đủ 500 ký tự và 1 chunk cuối cùng 100 ký tự).*
>
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> - **Số lượng chunk:** Bước nhảy mới là $S' = 500 - 100 = 400$ ký tự. Số lượng chunk mới là $\lceil \frac{10000 - 100}{500 - 100} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks $\rightarrow$ **tăng từ 23 lên 25 chunks** (tăng thêm 2 chunks).
> - **Lý do muốn độ chồng chéo nhiều hơn:** Giúp bảo toàn ngữ cảnh liền mạch (context preservation), ngăn chặn tình trạng thông tin quan trọng hoặc câu văn hoàn chỉnh bị cắt đôi ở ranh giới giữa hai chunk, từ đó nâng cao chất lượng và độ nhạy truy xuất (retrieval recall).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy lookbehind `r'(?<=\. )|(?<=! )|(?<=\? )|(?<=\.\n)'` để nhận diện chính xác các ranh giới câu mà vẫn giữ nguyên tính toàn vẹn của nội dung. Xử lý các trường hợp ngoại lệ như văn bản rỗng, khoảng trắng thừa ở đầu/cuối câu bằng `strip()`, sau đó gom các câu đơn lẻ thành từng nhóm tối đa `max_sentences_per_chunk` câu rồi nối lại bằng khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán duyệt qua danh sách dấu phân cách theo thứ tự ưu tiên giảm dần: `["\n\n", "\n", ". ", " ", ""]`. Trường hợp cơ sở (base case) là khi văn bản có độ dài `len(text) <= chunk_size` hoặc khi danh sách dấu phân cách đã cạn (sẽ cắt lát trực tiếp theo ký tự); sau khi tách nhỏ các đoạn quá khổ bằng đệ quy, các mảnh con nhỏ kề nhau được gộp lại tuần tự chừng nào tổng độ dài kèm separator không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Trong `add_documents`, mỗi tài liệu `Document` được chuẩn hóa thành bản ghi gồm `id`, `content`, `metadata` và vector nhúng tính từ `_embedding_fn`, sau đó lưu vào danh sách `_store` (in-memory). Phương thức `search` nhúng truy vấn `query`, tính tích vô hướng (`_dot`) giữa vector truy vấn và vector của từng bản ghi, sau đó sắp xếp giảm dần theo điểm số (`score`) và trả về danh sách top-k kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` sử dụng chiến lược lọc trước (pre-filtering): duyệt qua các bản ghi trong `_store` để chọn lọc những bản ghi khớp toàn bộ các cặp key-value trong `metadata_filter`, rồi mới thực hiện tìm kiếm tương đồng trên tập đã lọc. `delete_document` loại bỏ tất cả bản ghi có `id == doc_id` hoặc `metadata['doc_id'] == doc_id`, so sánh kích thước store trước và sau khi lọc để trả về `True` nếu có bản ghi bị xóa và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Truy xuất top-k chunk liên quan nhất từ kho tri thức thông qua `store.search(question, top_k=top_k)`. Xây dựng prompt chứa chỉ dẫn hệ thống, ngữ cảnh (context) được ghép từ nội dung của các chunk tìm được, và câu hỏi của người dùng, sau đó chuyển toàn bộ prompt vào `llm_fn` để sinh câu trả lời có căn cứ xác thực.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\CRUD\K4-DAY07-NguyenXuanKhue-2A202602999
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên phải trả tài liệu mượn về nhà trong vòng 10 ngày kể từ ngày mượn." | "Thời hạn tối đa để người học hoàn trả sách đã mượn về là mười ngày." | cao | 0.884 | Đúng |
| 2 | "Trả sách quá hạn bị phạt tiền 1.000 đồng cho mỗi cuốn sách mỗi ngày." | "Mức phí phạt nộp muộn tài liệu thư viện là 1.000 VNĐ một ngày đối với một tài liệu." | cao | 0.852 | Đúng |
| 3 | "Bạn đọc không được mang đồ ăn thức uống vào phòng đọc thư viện." | "Khu vực ẩm thực và căng tin phục vụ đa dạng các món ăn thức uống cho sinh viên." | thấp | 0.312 | Đúng |
| 4 | "Quy trình làm thẻ thư viện yêu cầu ảnh thẻ 3x4 và thẻ sinh viên còn hiệu lực." | "Thủ tục xin cấp lại mật khẩu tài khoản cổng thông tin đào tạo tín chỉ trực tuyến." | thấp | 0.186 | Đúng |
| 5 | "Sinh viên hệ chính quy được mượn tối đa 08 cuốn sách trong một học kỳ." | "Cán bộ và giảng viên được mượn tối đa 07 cuốn tài liệu trong thời gian 60 ngày." | cao (về chủ đề mượn sách) | 0.741 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Kết quả bất ngờ nhất là Cặp 5 giữa hạn mức của sinh viên và giảng viên có điểm tương đồng khá cao (0.741), dù đối tượng áp dụng và số lượng hoàn toàn khác nhau. Điều này cho thấy embedding models (như Sentence Transformers) biểu diễn ngữ nghĩa chủ yếu dựa trên không gian chủ đề chung (mượn trả sách, quy định số lượng) hơn là phân biệt rạch ròi các thực thể hạn mức số liệu hoặc nhóm đối tượng cụ thể. Đây chính là lý do vì sao kỹ thuật lọc siêu dữ liệu (Metadata Pre-filtering) là bắt buộc trong RAG để loại trừ kết quả sai lệch về đối tượng mà embedding thuần túy không phân biệt được.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mượn sách về nhà ở thư viện HUIT được tối đa mấy tài liệu và trong bao nhiêu ngày? *(dùng `metadata_filter={"audience": "student"}`)* | `huit-library-student`: 5. Quy định mượn/trả tài liệu (đối với sinh viên) - Tối đa 3 tài liệu, thời gian mượn 10 ngày. | 0.824 | Có (Relevant, Rank 1) | Sinh viên được mượn tối đa 3 tài liệu về nhà trong 10 ngày, được gia hạn 1 lần 10 ngày. |
| 2 | Quy trình mượn tài liệu về nhà ở thư viện Học viện Ngoại giao gồm những bước nào? | `dav-library-borrowing`: Phần thời gian và địa điểm mượn về (chunk chứa 8 bước B1-B8 nằm ở Top-2). | 0.768 | Có (Relevant, Rank 2) | Quy trình gồm 8 bước từ xuất trình thẻ tại quầy lưu hành tầng 3, tra mã tài liệu, ghi phiếu yêu cầu, thủ thư lấy sách và hoàn tất mượn. |
| 3 | Muốn được sử dụng thư viện HUIT thì cần những điều kiện gì? | `huit-library-rules`: 1. Quy định chung khi vào thư viện (chunk đúng câu 5 FAQ xếp hạng 35/370). | 0.812 | Không (Failure case, Rank 35) | Chỉ trả lời chung về việc tuân thủ nội quy chung, thiếu 3 điều kiện cụ thể (có thẻ, tập huấn, tuân thủ quy định). |
| 4 | Trả sách trễ hạn ở thư viện HUIT bị phạt bao nhiêu tiền mỗi ngày? | `huit-library-faq`: Câu 7 - Phạt mượn về nhà 1.000đ/tài liệu/ngày, mượn đọc trong ngày 5.000đ/tài liệu/ngày. | 0.856 | Có (Relevant, Rank 1) | Mượn về nhà (nhãn trắng) phạt 1.000đ/tài liệu/ngày; mượn đọc trong ngày (nhãn cam) phạt 5.000đ/tài liệu/ngày. |
| 5 | Thư viện PTIT cho mượn về nhà tối đa mấy cuốn, thời hạn mượn là bao lâu? *(dùng `metadata_filter={"audience": "student"}`)* | `ptit-library-student`: Điều 13 (kho mở: 02 cuốn / 07 ngày ở Rank 2; Điều 22 kho mượn: tối đa 08 cuốn / 150 ngày ở Rank 3). | 0.793 | Có (Relevant, Rank 2) | Sinh viên mượn 02 cuốn trong 07 ngày tại phòng đọc kho mở; sinh viên chính quy mượn tối đa 08 cuốn trong 150 ngày tại phòng mượn. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **4** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Tôi học được rằng việc bảo toàn ngữ cảnh phân tầng qua tiền tố đường dẫn tiêu đề (`HeadingChunker` của bạn Lâm) có vai trò quyết định đối với tài liệu pháp quy, giúp định vị chính xác nội dung hơn nhiều so với việc chỉ cắt theo câu hay theo ranh giới ngữ nghĩa thuần túy. Đồng thời, từ phân tích thất bại ở Câu 3 (cả 6 chiến lược đều bị điểm 0), tôi nhận ra giới hạn cố hữu của Dense Retrieval khi các tài liệu cùng trường cạnh tranh từ khóa; giải pháp tối ưu là kết hợp Hybrid Search (BM25 + Semantic Vector) cùng cơ chế Re-ranking để nâng cao độ chính xác.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |


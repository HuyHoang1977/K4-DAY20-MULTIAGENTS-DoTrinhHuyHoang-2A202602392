# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán **`subagents` đạt điểm trên tác vụ đánh giá ngang hoặc thấp hơn `baseline`**, không cải thiện có ý nghĩa. Căn cứ: (i) ở Phần 5, trên tác vụ học `subagents` cho 6/10 và 6/9 — y hệt `baseline` — trong khi tốn 2,2–3,7× token và 2–17× thời gian; (ii) phân loại lỗi ở Phần 4 cho thấy phần lớn lỗi là quy ước đầu ra (`rule_`) và đặc tả nằm ngay trong thư mục tác vụ, tức đều thuộc tầm tự nhiên của một tác tử đọc tệp rồi chạy lệnh, không đủ nặng để cắm búa; (iii) chi phí cố định của subagent rất lớn (mỗi lần giao là một lần gọi LLM mới, phải viết lại toàn bộ ngữ cảnh, không thừa hưởng hội thoại) trong khi điều kiện này không có `reviewer` chạy sau `implementer` để thu được lợi ích kiểm chứng. Tác vụ đánh giá là tác vụ một lượt như tác vụ học, nên không có lý do để lợi ích xuất hiện ở đây nếu không xuất hiện ở kia.
- H2 (skills-auto so với baseline): Dự đoán **`skills-auto` không cải thiện điểm trên tác vụ đánh giá; nhiều khả năng bằng hoặc thấp hơn `baseline`**. Căn cứ: (i) ngay trên tác vụ học ở Phần 3.4, `skills-auto` cho đúng điểm `baseline` (6/10, 5/8, 6/9) và không một check nào chuyển từ đỏ sang xanh; (ii) nguyên nhân đã tách được ở Phần 6 là tác tử **không mở skill** ở hai tác vụ (`skills_read = 0`) và **đọc nhưng chỉ làm một phần** ở tác vụ còn lại — tức là khoảng cách không nằm ở chất lượng nội dung skill; (iii) `04_curator.md` dẫn SkillsBench: skill do người biên soạn tăng trung bình khoảng 16 điểm phần trăm, còn skill do mô hình tự sinh **trung bình không có lợi**, và dẫn SkillEvolBench: lợi ích trên tác vụ học thường không chuyển sang tác vụ mới (quá khớp). Hai skill giữ lại đều được sinh từ phản hồi `detail` của **tác vụ học**, mà theo `05_skill_quality.md` quy ước của task học và task đánh giá không chắc trùng nhau.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán **điểm trên tác vụ đánh giá thấp hơn tác vụ học ở cả ba điều kiện, và khoảng cách không do điều kiện mà do độ khó của tác vụ**. Căn cứ: (i) cùng một bộ quy ước `rule_` xuất hiện ở cả hai vai trò, nhưng trên tác vụ học phần lớn lỗi còn lại tập trung ở nhóm nhỏ (code-learn trượt 4 check quy ước, data-learn 3, logs-learn 3) trong khi các check kỹ thuật (`parse_price_all_formats`, `north_q1_revenue`, ...) gần như luôn đạt — cho thấy tác vụ học phần lớn đã nằm trong tầm với của mô hình; (ii) `SKILLS_NOTE` và `SUBAGENTS_NOTE` chỉ là lời nhắc về quy trình, không cung cấp kiến thức nào về nội dung tác vụ, nên chúng không thể bù điểm cho độ khó của dữ liệu đầu vào mới; (iii) mọi điều kiện đều dùng cùng một system prompt dùng chung và cùng một mô hình, nên phần khác nhau giữa ba điều kiện là nhỏ so với phần khác nhau giữa hai vai trò. Nếu dự đoán đúng, bảng ở Phần 7 sẽ cho thấy cột `eval` thấp hơn cột `learn` một cách đồng đều, và khác biệt giữa ba điều kiện trên `eval` sẽ nằm trong nhiễu chạy lại (mỗi con số hiện là **một** lần chạy duy nhất).

## 3. Làm quen Deep Agents (Phần 0.3)

> Nguồn: `python scripts/tour.py` (chạy với model giả, 0 token). Trích nguyên văn mô tả công cụ.

### Câu 1: Tác tử mặc định có những công cụ nào? Công cụ nào cho phép chạy lệnh?

- **9 công cụ**, chia làm ba nhóm:
  - **Tệp (7):** `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`
  - **Shell (1):** `execute`
  - **Giao việc (1):** `task`
- Công cụ cho phép **chạy lệnh** là `execute`. Mô tả: *"Executes a shell command in an isolated sandbox and returns combined stdout/stderr with the exit code (truncated if very large)."* Lệnh chạy thật trên hệ điều hành, không phải trên bản sao ảo.
- Lưu ý ranh giới giữa `execute` và các công cụ tệp: mô tả `execute` yêu cầu *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."* Tức `execute` chỉ dành cho chạy chương trình (`python ...`), còn đọc/tìm kiếm thì dùng công cụ chuyên dụng.
- Ngoài ra: *"Only available on backends implementing SandboxBackendProtocol; otherwise it returns an error."* — `execute` phụ thuộc backend có khả năng chạy lệnh, đó là lý do `make_backend()` phải dựng `LocalShellBackend`.
- `task` chính là công cụ giao việc cho subagent, được thêm sẵn bởi framework (xem câu 2).

### Câu 2: Mô tả của `task` nói gì về subagent `general-purpose`? Subagent đó nhìn thấy ngữ cảnh nào?

Về `general-purpose`, mô tả `task` ghi:

> "general-purpose: General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks. When you are searching for a keyword or file and are not confident you will find the right match, use this agent to perform the search. **This agent has access to all tools as the main agent.**"

Về ngữ cảnh, mô tả nói subagent là **stateless**:

> "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."

Từ đó:

- `general-purpose` **không** được coi là kế thừa hội thoại: mô tả nói *"unless an agent type below says it inherits your conversation instead"*, và `general-purpose` không có ngoại lệ đó. Nó chỉ thấy **đúng nội dung prompt mà tác tử chính truyền vào tham số `description` của tool call**.
- Nó **không** thấy: lịch sử trò chuyện, kết quả các tool call trước đó của tác tử chính, và các lượt gọi LLM đã diễn ra trước đó. Muốn subagent biết gì thì phải viết vào prompt.
- Nó **có** toàn bộ công cụ của tác tử chính ("access to all tools"), nhưng **không có** system prompt của tác tử chính — cùng lý do `build_agent()` phải nối `PATHS_NOTE` vào `system_prompt` của từng subagent.
- Đầu ra là **một báo cáo cuối cùng**, và mô tả nhấn mạnh: *"The agent's report is not shown to the user; relay a summary yourself."* Tác tử chính phải tự kiểm chứng trước khi tin.
- Khi không có subagent chuyên biệt nào khác: *"When only general-purpose is available, use it for any complex, context-heavy task; it has the same capabilities as the main agent."*
- Mô tả cũng khuyến nghị chạy song song: *"Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls."*

### Câu 3: System prompt mặc định rỗng — trích một câu hướng dẫn hành vi từ `task` và một câu từ `execute`

`tour.py` in system prompt mặc định ra là `''` — rỗng. Nghĩa là **không có hướng dẫn nào ngoài mô tả công cụ**; toàn bộ hành vi định hình đến từ nguyên văn mô tả tool.

Từ mô tả **`task`**:

> "Tell the agent whether to create content, analyze, or only research, since it can't necessarily see the user's intent unless it inherits your conversation, as noted per agent type below."

Từ mô tả **`execute`**:

> "Chain commands with ';' or '&&' (use '&&' when a command depends on the previous); do not use newlines except inside quoted strings."

Nhận xét: vì system prompt rỗng, **mô tả công cụ chính là "system prompt" thực sự**. Điều này có hai hệ quả thực tế:

- Muốn thay đổi hành vi tác tử, không sửa được framework thì chỉ có hai đường: truyền `system_prompt` khi dựng agent (chính là `BASE_PROMPT` do lab cung cấp), hoặc sửa mô tả tool. Vì vậy `BASE_PROMPT`, `SKILLS_NOTE`, `SUBAGENTS_NOTE` được đánh dấu "CÓ SẴN, KHÔNG SỬA" — đó là điều kiện tiên quyết để các nhóm so sánh được với nhau.
- Hai câu trích ở trên cũng cho thấy mức độ khắt khe của framework: `execute` ràng buộc cả * cú pháp lệnh, còn `task` ràng buộc *cách diễn đạt yêu cầu* đối với subagent vì ngữ cảnh không được chia sẻ. Cả hai đều bắt model tự tuân thủ bằng mô tả, không có mã cưỡng chế.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Cơ sở: điều kiện `baseline`, ba tác vụ học (`code-learn`, `data-learn`, `logs-learn`). Tổng 13 check thất bại trên 27 check.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `tests_not_modified` | **G** – lỗi môi trường, không phải lỗi tác tử | `detail`: "the original files in tests/ must not be modified (new test files are allowed)". Vết: tác tử không hề sửa `tests/test_report.py`; nó chỉ tạo rồi xóa `workspace/tests/test_extra.py` (vết dòng 461–487). Nguyên nhân gốc: repo có `core.autocrlf=true`, nên fixture `tasks/code-learn/workspace/tests/test_report.py` bị checkout thành CRLF; sha256 = `efb5e765…`, còn `TEST_FILE_HASHES` ghi `79e05f4c…`. Chuẩn hoá CRLF→LF lại ra đúng `79e05f4c…` ⇒ check sai do dấu cuối dòng, không phải do tác tử. |
| code-learn | `rule_type_hints` | **E** | `detail`: "RULE: every public function (name not starting with '_') … has type annotations on all parameters and on the return value." Vết: `inventory/pricing.py` vẫn còn `def parse_price(text):` (không annotation) dù tác tử đã đọc file này. Quy ước này **không có trong đề**; đề chỉ nói "checked by Acme's review bot against the Acme Python team conventions". |
| code-learn | `rule_regression_tests` | **E** | `detail`: "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass." Vết: tác tử đã tự viết 3 test hồi quy vào `tests/test_extra.py`, chạy 9 test pass, rồi **xoá** file đó (vết dòng 483–487). Nghĩa là tác tử làm gần đúng việc cần làm nhưng không đoán ra *tên* `test_regressions.py`. |
| code-learn | `rule_changelog` | **E** | `detail`: "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets)." Vết: tác tử đã đọc `workspace/CHANGELOG.md` (thấy sẵn mục `## Unreleased`, vết dòng 299–308) nhưng không ghi gì. |
| data-learn | `rule_money_in_cents` | **E** | `detail`: "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)." Vết: câu trả lời cuối báo `north_q1_revenue: 3130.24` (đơn vị USD, không phải cent). |
| data-learn | `rule_meta_block` | **E** | `detail`: "RULE: answer.json has an object `meta` = {source, rows_in, rows_used}." Vết: tóm tắt cuối chỉ liệt kê 5 khóa theo đề, không hề nhắc khối `meta`. |
| data-learn | `rule_clean_csv` | **E** | `detail`: "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents …". Vết: chỉ ghi `answer.json`; không có `clean.csv`. |
| logs-learn | `rule_service_names` | **E** | `detail`: "RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service)." Vết: `errors.json` ghi `"service": "inventory-service"` (vết dòng 138). |
| logs-learn | `rule_sorted_errors` | **E** | `detail`: "RULE: `errors` is sorted by service, then by timestamp_utc, ascending." Vết: thứ tự trong tệp là `inventory-service, inventory-service, auth-service, auth-service, payment-service…` (vết dòng 137–184) – theo thứ tự dòng log, không sắp xếp. |
| logs-learn | `rule_schema_header` | **E** | `detail`: "RULE: the top-level object has \"schema_version\": 2 and \"generated_by\": \"log-triage\"." Vết: `errors.json` mở đầu bằng `{"errors": [` (vết dòng 134–136), không có hai khóa này. |

**Bằng chứng phủ định cho các nhóm A–D.** `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    17/18         0/9          165,373      0/3
```

17/18 check kỹ thuật đạt ở `baseline`. Cụ thể:

- **A (bỏ qua đặc tả):** không có bản ghi. Vết cho thấy cả ba tác tử đọc tài liệu định dạng *trước khi làm*: `logs-learn` đọc `workspace/README.md` về format log (vết dòng 35–48), `data-learn` đọc `workspace/README.md` về data dictionary (vết dòng 24–36), `code-learn` đọc `tests/test_report.py` và docstring của cả 3 hàm (`parse_price`, `apply_discount`, `low_stock`, `to_csv_row`) trước khi sửa. 5 check định dạng–giá trị biên của `code-learn` đều đạt.
- **B (không kiểm chứng):** không có bản ghi. `code-learn` chạy lại test 5 lần, lần cuối (`6 passed`) là *sau* chỉnh sửa cuối cùng; `logs-learn` đọc lại `errors.json` để đối chiếu với đề; `data-learn` đối chiếu số liệu bằng pandas trên dữ liệu thô.
- **C (vá triệu chứng):** không có bản ghi. Ba lỗi kỹ thuật đều được sửa ở nguyên nhân: `parse_price` bỏ dấu phân cách nghìn và xử lý ngoặc kép học kế toán; `apply_discount` chuyển sang `rounding=ROUND_HALF_UP` thay vì mặc định half-even; `low_stock` đổi `<=` thành `<` và thêm `sorted(key=str.lower)`. `csv_quoting_follows_docstring` cũng đạt dù không có test nào nhắc.
- **D (bỏ sót dữ liệu bẩn/định dạng):** không có bản ghi. `data-learn` phát hiện đủ bốn loại bẩn mà README mô tả và 5/5 check kỹ thuật đạt: 7 hàng trùng (`df.duplicated()` = 7), 8 đơn `-999` bị loại khỏi doanh thu, ba kiểu ngày (`YYYY-MM-DD`, `DD/MM/YYYY`, ISO+offset) và ba múi giờ (`Z`, `+07:00`, `-05:00`) đều chuẩn hoá về UTC trước khi so sánh Q1; `logs-learn` xử lý traceback nhiều dòng và dòng `-- last message repeated N times --` (6/6 check kỹ thuật đạt, kể cả `timestamps_utc` và `repeat_counts`).

**Nhận xét.** Nhóm **E chiếm đa số tuyệt đối: 9/13 lỗi (69%)**, và đúng 100% lỗi do tác tử tự gây ra. Toàn bộ 9 check `rule_*` của cả ba tác vụ đều trượt (0/9). Một lỗi nhóm E đặc trưng đã xuất hiện cả ở điều kiện `subagents` và ở điều kiện `baseline` trên tác vụ đánh giá, nên đây là đặc điểm của bài toán (quy ước ẩn), không phải tai nạn của một lần chạy. Đáng chú ý: cả ba tác vụ đều có câu "Your output is also checked by Acme's review bot against the Acme … conventions" – đây là tín hiệu duy nhất mà tác tử có, và tác tử đã bỏ qua nó ba lần.

**Một skill có phòng ngừa được nhóm E không?** Có, theo tiêu chí ở `guides/pseudocode/05_skill_quality.md` §3 (tên do quy ước Acme yêu cầu như `clean.csv`, `tests/test_regressions.py`, khóa `meta` được phép vì "chính là quy tắc"). Cấu trúc skill khả thi:

- `description` bắt đầu bằng "Use when …" và kích hoạt đúng lúc: *"khi đề bài có câu kiểu 'đầu ra cũng được bot review của Acme kiểm tra theo quy ước nhóm'"* – đây là điều kiện xuất hiện ở 3/3 tác vụ học. `description` quyết định skill có được đọc hay không, nên nó phải bám vào *dấu hiệu* này chứ không bám vào loại tác vụ.
- body là một checklist ngắn (mục 3 của `05_skill_quality.md` khuyến nghị 2–3 ý, ≤40 dòng): (i) tìm tệp quy ước sẵn có trong workspace và đọc trước (`CHANGELOG.md`, `README.md`); (ii) trước khi kết thúc, chạy một vòng đối chiếu danh sách "món ăn" của quy ước nhóm: annotation cho hàm công khai, tệp hồi quy với ≥3 test, mục changelog dạng `- fix(tên_hàm): …`, tiền tệ tính bằng cent, khối `meta`, khóa `schema_version`/`generated_by`, tên service chuẩn hoá, danh sách được sắp xếp; (iii) câu trả lời cuối phải khớp đúng tên tệp/khoá đã ghi ra đĩa.

Skill dạng này hoàn toàn là tri thức thủ tục (không chứa con số hay đáp án), nên không vi phạm ràng buộc "không rò rỉ". Rủi ro còn lại là **quá khớp**: 9 quy ước của ba tác vụ học được liệt kê thành một danh sách, trong khi check quy ước *mới* ở tác vụ đánh giá (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) không nằm trong danh sách đó. Kỳ vọng hợp lý là skill chuyển được phần "quét lại quy ước lúc kết thúc" (một *thói quen kiểm chứng*, tức nhóm B), chứ không chuyển được từng món cụ thể.

Ngoài ra cần lưu ý lỗi nhóm G: `tests_not_modified` là lỗi hạ tầng của lab (fixture CRLF trên Windows + hash cố định trong `tasks/code-learn/check.py`), không phải lỗi tác tử, và nó xuất hiện ở **mọi** lần chạy của `code-learn`/`code-eval` bất kể điều kiện — khi so sánh điểm phải loại nó ra hoặc chấp nhận nó như một hằng số chung cho cả hai vế.

## 5. Điều kiện `subagents` (Phần 2.3)

### Các subagent đã định nghĩa

`src/lab/subagents.py` định nghĩa 3 subagent:

| Tên | Vai trò | Lý do thiết kế |
|---|---|---|
| `explorer` | Đọc và báo cáo | "Investigate and report; never modify any file" – tách phần *tìm hiểu đặc tả* khỏi phần *sửa*, đồng thời bảo đảm nó không đụng `skills/`. Yêu cầu báo cáo "đường dẫn tương đối chính xác, định dạng thật, trích đoạn bằng chứng" và phải nói rõ **điều mình không tìm thấy**. |
| `implementer` | Thực hiện thay đổi | Mang các ràng buộc mà mô hình hay quên: "mọi đường dẫn tương đối với sandbox root", "chạy test/checker và sửa cái fail", "báo cáo phải liệt kê đúng đường dẫn + lệnh kiểm chứng + output", và "**đừng báo việc dở là hoàn tất**" – đúng vá nhóm F. |
| `reviewer` | Kiểm tra độc lập | Không sửa gì, chỉ kết luận từng yêu cầu "requirement → verdict → file:line", và "nếu mọi thứ đúng thì nói thẳng, đừng bịa vấn đề" – nhằm chống cả vá triệu chứng (C) lẫn cảnh báo giả. |

### `subagent_calls` ở từng tác vụ

| Tác vụ | `subagent_calls` | Có giao việc? | Nhận xét |
|---|---|---|---|
| `code-learn` | 4 | Có | 1× `explorer`, rồi 3× `general-purpose` (chạy pytest, đối chiếu, chạy lại pytest). |
| `logs-learn` | 3 | Có | 1× `explorer`, 2× `implementer`. |
| `data-learn` | 0 | **Không** | Lần chạy hỏng trước bước đầu tiên: `error = "RemoteProtocolError: Server disconnected without sending a response."`, `tool_calls = 0`, `trace.md` rỗng 0 dòng, 0/8 check. `subagent_calls = 0` ở đây **không phải quyết định của tác tử** mà là hệ quả của lỗi mạng; không dùng làm bằng chứng cho "tác tử chọn không giao". |

Hai nhận xét quan trọng:

1. **Ba subagent tự định nghĩa chỉ được dùng 2/7 lần gọi.** 5 lần gọi dùng `general-purpose` của framework, vốn không có system prompt nào (`build_agent` chỉ nối `PATHS_NOTE`), tức là mất đúng các ràng buộc ở trên. Việc tác tử chọn `general-purpose` cho việc "chạy pytest" là hợp lý vì đó là lệnh đơn giản, nhưng nó cho thấy mô tả/`description` của subagent tự viết chưa đủ hấp dẫn để được chọn.
2. **`explorer` bị giao việc đúng nhưng báo cáo sai một chi tiết.** Với `code-learn`, subagent báo "all tests passed successfully (8 passed)" trong khi `tests/test_report.py` chỉ có 6 test (vết `subagents/code-learn` dòng 93 và 192). Tác tử chính đã nhận báo cáo đó và không truy vết lại con số → minh hoạ rõ mối rủi ro của việc tin báo cáo subagent kể cả khi nó nghe rất thuyết phục.

### Lời giao việc có đủ quy tắc của đề không?

Không, ở các lần giao đầu tiên — và đây là hậu quả trực tiếp của việc subagent **stateless**:

| Lần giao | Nội dung lời giao | Thiếu gì |
|---|---|---|
| `code-learn` #1 (`explorer`) | "Explore the workspace repository to understand the project structure, locate the inventory package and test files, and inspect their content." | Không có: yêu cầu *"the docstrings are the specification"*, cấm sửa `tests/`, và cả câu "Acme's review bot against the Acme Python team conventions". |
| `logs-learn` #1 (`explorer`) | "…understand the log format, Acme log-triage conventions, and requirements for parsing workspace/app.log into workspace/errors.json." | Nói tới "Acme conventions" nhưng không nêu quy ước nào; lại bắt subagent đi tìm thứ vốn không tồn tại trong workspace. |
| `logs-learn` #2 (`implementer`) | "Write a Python script to parse workspace/app.log according to all specified rules, validate output format against the requested schema…" | Thiếu toàn bộ schema và 6 rule của đề. Hệ quả đo được: subagent sinh `errors.json` với `"count"`, `"extra_lines"`, timestamp **chưa chuyển UTC**, và nhân bản cả các bản lặp thay vì gộp vào `repeat_count` (vết dòng 156–177). |
| `logs-learn` #3 (`implementer`) | Lần này mới dán nguyên văn schema + 6 rule + yêu cầu kiểm tra múi giờ. | Đủ. Kết quả đúng ngay (`6/9`, đúng 6 check kỹ thuật). |

Tức là 3 lần giao đầu tiên đều **thiếu quy tắc**, và vết cho thấy cần đến lần giao thứ 4 mới làm đúng: một lượt giao việc tốn kém bị lãng phí vì lời giao không đủ thông tin. Ngược lại, `code-learn` #2–#4 và `logs-learn` #3 có **thừa** thông tin ở mức vô hại: lặp lại việc "chạy pytest" hai lần liên tiếp trên cùng một trạng thái kho, và còn dán nguyên văn đề vào lời giao `implementer` thay vì chỉ dẫn tới điểm cần sửa — đây là chi phí token lãng phí mà không đổi được kết quả (điểm `code-learn` giữ nguyên 6/10).

### Báo cáo của subagent có được kiểm tra trước khi dùng không?

Có, ở mức *đọc lại tệp*, nhưng không ở mức *đối chiếu với đề*:

- `logs-learn`: tác tử chính đọc lại `workspace/errors.json` 3 lần (sau khi subagent đổi định dạng, và cả sau lần sửa thứ hai), đọc cả `parse_logs.py` và `test_parse_logs.py` của subagent, rồi tự xoá 2 tệp tạm. Đây là kiểm chứng thực chất và nó đã bắt được lỗi định dạng của lần giao đầu.
- `code-learn`: tác tử chính đọc lại cả 3 tệp đã sửa (`pricing.py`, `export.py`, `report.py`) và giao một lượt chạy lại pytest. Tuy nhiên nó **không** đối chiếu báo cáo "8 passed" với thực tế 6 test, và không đối chiếu kết luận của subagent với các ràng buộc trong đề.
- Cả hai tác vụ: subagent `reviewer` – đúng vai trò kiểm tra độc lập – **không hề được gọi**. Đây là cơ hội bị bỏ lỡ đúng chỗ: vòng `implementer → reviewer` sẽ là nơi bắt được "8 passed" sai và các quy ước của Acme.

### Ảnh hưởng đến token và thời gian

| Tác vụ | baseline tokens / giây | subagents tokens / giây | Hệ số token |
|---|---|---|---|
| `code-learn` | 194,267 / 112,1 s | 337,578 / 210,5 s | ×1,74 |
| `logs-learn` | 72,166 / 15,5 s | 658,884 / 259,9 s | ×9,13 |
| `data-learn` | 229,688 / 80,8 s | 97,453 / 52,2 s (hỏng, không tạo được đầu ra) | không so sánh được |
| **Trung bình (`check_breakdown.py`)** | **165,373** | **364,638** | **×2,2** |

Nếu chỉ so hai cặp hợp lệ: trung bình 133,217 → 498,231 token (×3,7). Lưu ý trung bình 364,638 do `check_breakdown.py` in ra **có tính cả** lần chạy hỏng của `data-learn`; dù nó làm giảm trung bình của `subagents`, mà nếu thay bằng lần chạy hợp lệ (baseline 229,688) thì trung bình còn là 408,713 (×2,5). `logs-learn` là nơi đắt nhất: 658,884 token cho **cùng** kết quả 6/9 như baseline, vì một lượt giao thiếu schema đã phải trả hai lần bằng implementer, mỗi lượt lại tự sinh kèm một bộ test riêng.

**Kết luận về điều kiện `subagents` ở phần này:** với mô hình mạnh và tác vụ một lượt, đa tác tử **không mang lại điểm nào** (6/10 và 6/9 – y hệt baseline) trong khi tốn 2,2–3,7× token và 2–17× thời gian. Lý do có hệ thống, không phải ngẫu nhiên: việc đọc đặc tả và việc kiểm chứng đều đã nằm trong tầm tự nhiên của một tác tử đọc tệp và chạy lệnh, nên không có phần việc nào đủ nặng để cắm búa; trong khi chi phí cố định của subagent (mỗi lần giao là một lần gọi LLM mới với toàn bộ ngữ cảnh phải viết lại tay, không được thừa hưởng hội thoại) lại rất lớn. Điều kiện này chỉ đáng giá khi (i) lời giao việc luôn kèm đủ quy tắc của đề, và (ii) có một `reviewer` thật sự chạy sau `implementer`.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: **3** (lần đầu + 2 lần chạy lại, đúng giới hạn cho phép). Mỗi lần curator gọi mô hình đúng **một lần** và trả về 2 khối skill; validator loại phần còn lại.

  | Lần | Kết quả | Xử lý của nhóm |
  |---|---|---|
  | 1 | `maintain-codebase-integrity-and-type-hints` (hợp lệ); `adhere-to-output-rules-and-formatting` bị `validate_skill` chặn vì chứa marker `orders` | giữ 1 |
  | 2 | `record-fixes-and-add-regression-tests` (hợp lệ); `adhere-to-output-rules-and-formatting-specs` bị chặn vì marker `orders` | giữ 1 |
  | 3 | `adhere-to-strict-rules-and-schema`, `comprehensive-regression-testing-and-type-hints` (cả hai hợp lệ) | giữ 2 |

  **Đã xóa 2 skill** (không sửa tay nội dung): `maintain-codebase-integrity-and-type-hints` và `record-fixes-and-add-regression-tests`. Lý do: cả hai chỉ nói lại `code-learn`, cùng bốn quy tắc (không sửa test gốc, thêm type hint, viết test hồi quy, cập nhật changelog), và bị `comprehensive-regression-testing-and-type-hints` lặp lại gần như nguyên văn. Theo tiêu chí "Ngắn" ở `05_skill_quality.md` (2–3 ý chính, trùng lặp là dấu hiệu xấu), ba skill gần như trùng nhau làm loãng ngữ cảnh. Skill của lần chạy 3 chính xác hơn ở chỗ nêu đích danh quy ước Acme (`tests/test_regressions.py`, định dạng bullet `- fix(<hàm>): <mô tả>`), vốn được phép vì đó là chính quy tắc cần tuân thủ.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `adhere-to-strict-rules-and-schema` | **Tổng quát.** Nêu quy trình kiểm tra đầu ra theo loại lỗi (định dạng tiền, khóa bắt buộc, quy tắc đặt tên) chứ không nêu tên tệp hay con số của một tác vụ. Nó là skill duy nhất phủ được lỗi của `data-learn` và `logs-learn`. | **Đúng, không có hướng dẫn sai.** Khớp với `detail` của các check: `rule_money_in_cents` ("integer cents"), `rule_meta_block` (`meta`), `rule_schema_header` (`schema_version`, `generated_by`), `rule_service_names` (hạ chữ thường, `-`→`_`). Khuyến nghị "chạy script tự kiểm" là hợp lý. Rủi ro nhỏ: câu 6 chung chung ("re-read all requirements") có thể bị bỏ qua. | 9 dòng (thân 5 dòng) — rất ngắn, không thừa. `description` mở đầu bằng "WHEN PRODUCING OUTPUT FILES OR JSON OBJECTS", nêu đúng tình huống kích hoạt và đủ rộng. **`skills_read` = 0** ở cả `data-learn` và `logs-learn`: skill **không được mở ra**, dù đây là skill đáng lẽ phải áp dụng. |
| `comprehensive-regression-testing-and-type-hints` | **Tổng quát về mặt hình thức, hẹp về mặt nội dung.** Dùng `tests/test_regressions.py` và `CHANGELOG.md` là quy ước Acme nên được phép. Nhưng toàn bộ skill chỉ áp dụng cho tác vụ sửa code, không giúp được task data/log. | **Đúng.** Khớp `detail` của cả 4 check của `code-learn`. Quy tắc "thêm type hint cho hàm public" phát biểu đúng (`name not starting with '_'`). | 8 dòng (thân 4 dòng), không thừa. `description` ("WHEN FIXING CODE OR ADDING FEATURES") nêu đúng tình huống. **`skills_read` = 2** ở `code-learn` (skill này và skill kia đều được đọc). |

**Kết quả Phần 3.4 — điểm số không đổi, dù skill đã được đọc:**

| Tác vụ | baseline | skills-auto | `skills_read` | Check thất bại (như cũ) |
|---|---|---|---|---|
| code-learn | 6/10 | 6/10 | 2 | `tests_not_modified`, `rule_type_hints`, `rule_regression_tests`, `rule_changelog` |
| data-learn | 5/8 | 5/8 | 0 | `rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv` |
| logs-learn | 6/9 | 6/9 | 0 | `rule_service_names`, `rule_sorted_errors`, `rule_schema_header` |

Không có check nào chuyển từ đỏ sang xanh. Đây là kết quả **tiêu cực** và cần phân biệt rõ hai nguyên nhân, vì chúng khác nhau về ý nghĩa:

- `data-learn` và `logs-learn`: `skills_read = 0`, tức là **skill không bao giờ được mở**. `adhere-to-strict-rules-and-schema` có `description` đúng và rộng, nhưng tác tử không chọn đọc nó. Ở Phần 4.1, `SKILLS_NOTE` yêu cầu đọc `SKILL.md` của mọi skill có thể áp dụng **ngay từ bước đầu tiên**, nhưng trên thực tế tác tử lại ưu tiên đọc tệp trong `workspace/` và chạy lệnh trước.
- `code-learn`: `skills_read = 2` — cả hai skill **đều được đọc**, tác tử còn viết đúng `tests/test_regressions.py` theo lời skill. Nhưng nó chỉ làm theo **một phần**: từ vết thấy nó sửa `parse_price` (dấu ngoặc kép kiểu kế toán) và tạo file test, còn bỏ qua type hint và không đụng `CHANGELOG.md` dù đã đọc file này. Đây chính là kiểu thất bại thứ hai mà `05_skill_quality.md` §5 mô tả: **đọc nhưng chỉ làm một phần**.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:

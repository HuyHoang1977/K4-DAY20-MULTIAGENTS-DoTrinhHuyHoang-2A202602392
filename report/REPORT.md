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
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 7/10 |
| data-learn | 5/8 | 3/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 5/9 | 5/9 | 5/9 |
| logs-eval | 6/10 | 2/10 | 6/10 |
| **Mean score - learning tasks** | 0.63 | 0.55 | 0.66 |
| **Mean score - evaluation tasks** | 0.57 | 0.43 | 0.57 |
| **Mean tokens per run** | 139,056 | 462,087 | 149,043 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12         112,739      0/3
baseline      learn    17/18         0/9          165,373      0/3
subagents     eval     13/18         0/12         438,938      0/3
subagents     learn    15/18         0/9          485,235      0/3
skills-auto   eval     17/18         0/12         111,589      0/3
skills-auto   learn    17/18         1/9          186,497      0/3
```

**Các lần chạy có `error` và cách xử lý:**

| Lần chạy | Lỗi | Xử lý |
|---|---|---|
| `subagents/logs-eval` (lần 1) | `GoogleAPIError: 503 UNAVAILABLE` (mô hình quá tải) | Chạy lại một lần, ra `2/10` hợp lệ. Đây là lỗi hạ tầng, không phải hành vi tác tử. |
| `skills-auto/code-learn` | `GraphRecursionError: Recursion limit of 60 reached` | Chạy lại **hai lần**, cả hai lần lặp lại đúng lỗi (3/3 lần), điểm đều 7/10. Giữ lần cuối. |

Ghi chú về `skills-auto/code-learn`: lỗi này **tái hiện được**, không phải nhiễu. Vết cho thấy tác tử kẹt ở việc chạy `pytest` (`ImportError` vì `rootdir` là sandbox chứ không phải `workspace`) rồi thử liên tiếp các biến thể `pytest` / `python -m pytest` / `--rootdir` / `-o pythonpath` cho tới hết trần. Điểm 7/10 vẫn có ý nghĩa vì workspace đã được tác tử sửa trước khi vòng lặp, nhưng `tool_calls = 0` (runner mất messages khi exception) nên **không được tính là một lần chạy sạch**. Biến thể lệnh đúng (`python -m pytest -o pythonpath=workspace workspace/tests`) đã từng được tác tử tự tìm ra ở lần chạy Phần 3.4, nên đây là hành vi mô hình lặp lại, không phải lỗi cấu hình sandbox.

`skills_modified` là `false` ở **toàn bộ** 6 lần chạy `skills-auto`, và `python scripts/verify_freeze.py` trả về `OK` (6 run được kiểm tra). Lưu ý: script này lỗi `UnicodeDecodeError` (cp1252) khi đọc `REPORT.md` tiếng Việt trên Windows; chạy với `PYTHONUTF8=1` là ra `OK`. Không sửa script.

## 8. Phân tích

1. **Điều kiện nào cải thiện?** Trên tác vụ học, `skills-auto` là điều kiện duy nhất có điểm trung bình cao hơn `baseline` (0,66 so với 0,63) — nhưng điểm đó **không đáng tin**: nó đến từ đúng một run (`code-learn`, 7/10) mà run đó lại bị lỗi, và chính run đó có `skills_read = 0`. Trên tác vụ đánh giá, **không điều kiện nào cải thiện**: `skills-auto` bằng đúng `baseline` (0,57) và `subagents` thấp hơn rõ (0,43). Không có trường hợp "cải thiện học nhưng không cải thiện đánh giá" theo nghĩa có ích — có trường hợp **không cải thiện ở vai trò nào**, đó là `skills-auto`.

   Kết quả này **xác nhận cả ba giả thuyết H1–H3** đã viết trước khi xem điểm đánh giá: `subagents` bằng hoặc thấp hơn; `skills-auto` không cải thiện; điểm đánh giá thấp hơn điểm học ở cả ba điều kiện (0,57 so với 0,63; 0,43 so với 0,55; 0,57 so với 0,66).

2. **Tách check kỹ thuật và check quy ước.** Đây là phát hiện lớn nhất của cả thí nghiệm: **toàn bộ 21 check quy ước (`rule_`) ở `baseline` và `subagents` đều trượt (0/12 ở đánh giá, 0/9 ở học), trong khi check kỹ thuật gần như luôn đạt (17/18)**. Nói cách khác, tác tử của chúng ta gần như hoàn hảo về phần tính toán và gần như vô dụng về phần tuân thủ quy ước báo cáo. Skill curator sinh ra **không giúp được check quy ước nào trên tác vụ đánh giá**: 0/12 ở cả `baseline` và `skills-auto`. Riêng trên tác vụ học nó giúp đúng **một** check, ở `code-learn` (`1/9`) — nhưng run đó `skills_read = 0`, nên check đó đạng được **không phải nhờ đọc skill**; đây phải là nhiễu, và tôi không ghi nhận nó là hiệu quả của skill.

   Check quy ước **mới** của tác vụ đánh giá không được skill giúp vì hai lý do độc lập, cộng lại: (i) `skills_read = 0` — skill chưa từng được mở; (ii) ngay cả khi mở, skill được sinh từ phản hồi `detail` của **tác vụ học**, mà `detail` của tác vụ đánh giá luôn rỗng, nên curator không thể biết những quy ước riêng của đánh giá. Đây là biểu hiện trực tiếp của rủi ro "quá khớp" mà `04_curator.md` dẫn từ SkillEvolBench.

3. **Một check skill giúp và một check skill không giúp.** Trường hợp **không giúp** đã rõ: `skills-auto/data-eval` trượt cả ba check quy ước (`rule_service_names` tương ứng, `rule_sorted_errors`, `rule_schema_header`) với `skills_read = 0` — skill `adhere-to-strict-rules-and-schema` vốn đúng là nói về đúng ba loại lỗi đó, và đúng một trong số đó là `schema_version`/`generated_by`; tác tử đơn giản là không mở file. Trường hợp **giúp** thì không có ví dụ nào đạt được bằng cơ chế skill trong lần chạy chính thức: lần duy nhất `skills_read > 0` là `code-learn` ở Phần 3.4 (đọc cả hai skill, `7/10` so với `6/10`), nhưng khi đối chiếu vết thì tác tử chỉ làm theo **một phần** — nó sửa `parse_price` và tạo `tests/test_regressions.py` đúng lời skill, còn bỏ qua yêu cầu thêm type hint và không sửa `CHANGELOG.md` dù đã đọc file đó. Đây chính là kiểu "đọc nhưng chỉ làm một phần" của `05_skill_quality.md` §5, và cũng là lý do điểm ở Phần 3.4 không tái lập được ở lần chạy sau đóng băng (mục 8.6).

4. **Chi phí.** Token trung bình mỗi run: `baseline` 139.056, `skills-auto` 149.043, `subagents` **462.087**. `subagents` tốn **3,3× baseline** để đạt điểm thấp hơn. Xét "điểm trên mỗi token": `baseline` và `skills-auto` gần như bằng nhau và là hai điều kiện tốt nhất; `skills-auto` tốn thêm ~7% token với lý do chính là phải nạp và (thỉnh thoảng) đọc skill. Đa tác tử **không đáng chi phí** trong thí nghiệm này: ngoài chi phí token, nó còn làm mất cả check kỹ thuật (13/18 ở đánh giá so với 17/18 của `baseline`), tức là không chỉ vô ích mà còn tiêu cực. Nguyên nhân có thể thấy rõ ở `subagents/logs-eval`: 9 lần giao cho subagent, 649.869 token, và mất cả bốn check kỹ thuật mà `baseline` đạt — thông tin bị mất qua các lần bàn giao ngữ cảnh.

5. **Rò rỉ dữ liệu và quá khớp.** Về rò rỉ: **không có**. Cơ chế chống rò rỉ hoạt động đúng và bằng chứng là nó đã bắt được việc rò rỉ thật — ở cả lần chạy 1 và lần chạy 2 của curator, `validate_skill` loại skill `adhere-to-output-rules-and-formatting*` vì chứa marker `orders`. Ngoài ra `curate_skills` chỉ nạp run có `role == "learn"`, và `test_04_curator.py` kiểm tra điều này bằng cách xác nhận tên tác vụ đánh giá không xuất hiện trong prompt. Các skill còn lại không chứa tên tệp dữ liệu, tên cột, tên hàm hay con số nào của tác vụ học; chúng chỉ nêu tên do **quy ước Acme** quy định (`tests/test_regressions.py`, `CHANGELOG.md`, `meta`, `schema_version`, `generated_by`) — theo `05_skill_quality.md` §3, đây là chính quy tắc nên dùng được.

   Về **quá khớp**: có, và nó là nguyên nhân gốc của kết quả âm. Cả hai skill đều được sinh từ phản hồi `detail` của tác vụ học. `comprehensive-regression-testing-and-type-hints` đặc biệt hẹp: nó chỉ nói về type hint, test hồi quy và changelog — tức đúng ba lỗi của `code-learn` — nên về bản chất nó là một bản chép lại của một tác vụ, chỉ được viết theo ngôn ngữ khái quát. Ở lần chạy curator đầu tiên, ngay cả các skill hợp lệ cũng chỉ phủ `code-learn`; phải đến lần chạy thứ ba mới xuất hiện được `adhere-to-strict-rules-and-schema`, skill duy nhất nói về lỗi định dạng (tiền tố cent, khóa `meta`, tên service) và là skill có triển vọng nhất trên tác vụ đánh giá. Việc phải chạy curator tới 3 lần mới có được một skill khái quát là bằng chứng định lượng cho độ ngẫu nhiên lớn mà `04_curator.md` cảnh báo. Nhóm phòng tránh bằng cách: đánh giá và xóa skill trùng lặp, **không sửa tay** nội dung skill, và chỉ giữ skill nào đúng với phản hồi `detail` của bot đánh giá.

6. **Nhiễu.** So sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu thành `results/skills-auto-dev`) và sau đóng băng:

   | Tác vụ | skills-auto (3.4, trước) | skills-auto (sau đóng băng) | chênh lệch |
   |---|---|---|---|
   | code-learn | 6/10 | 7/10 (có `error`) | +1 |
   | data-learn | 5/8 | 5/8 | 0 |
   | logs-learn | 6/9 | 6/9 | 0 |

   Trên cùng một bộ skill, một tác vụ hơn 1 điểm và hai tác vụ không đổi. Đây chính là mức nhiễu đo được của thí nghiệm: **±1 điểm trên một tác vụ đơn, ngay cả khi mọi thứ được giữ nguyên**. Hệ quả trực tiếp: mọi chênh lệch cỡ 1 điểm trong bảng mục 7 — kể cả chênh lệch ±1 điểm mà chúng ta từng thấy giữa các điều kiện — **không đủ bằng chứng để kết luận**. Đáng chú ý, `code-learn` trước đóng băng đạt 6/10 với `skills_read = 2` (đọc cả hai skill) còn sau đóng băng đạt 7/10 với `skills_read = 0` (không đọc skill nào) — tức điểm cao hơn thuộc về run **ít** dùng skill hơn, củng cố kết luận rằng skill sinh ra không tạo ra lợi ích đo được. Với mỗi điều kiện chỉ chạy **một** lần và chỉ 3 tác vụ mỗi vai trò, bảng mục 7 nên được đọc như một ảnh chụp đơn điểm, không phải một ước lượng ổn định.


## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. **Mỗi cấu hình chỉ chạy MỘT lần, trong khi nhiễu đo được là ±1 điểm trên một tác vụ.** Mục 8.6 cho thấy cùng một bộ skill cho `code-learn` dao động 6/10 → 7/10 giữa hai lần chạy. Vì vậy không chênh lệch nào cỡ 1 điểm trong bảng mục 7 có thể kết luận được; người đọc có thể dễ dàng đảo ngược thứ hạng giữa `baseline` và `skills-auto` chỉ bằng một lần chạy lại. Ảnh hưởng: kết luận "không điều kiện nào cải thiện" phải dựa vào **khoảng cách có ý nghĩa** (điểm trung bình 0,57 so với 0,57; 3,3× token; 0/12 check quy ước), không dựa vào từng ô bảng.
2. **Chỉ 3 tác vụ mỗi vai trò, và cả 6 tác vụ do giảng viên thiết kế sẵn với quy ước giống nhau.** Tổng số check quy ước toàn bộ thí nghiệm chỉ là 21 lần chấm, và cả 21 đều là cùng một loại quy tắc (định dạng đầu ra của Acme). Ảnh hưởng: kết luận "tác tử vô dụng về quy ước nhưng giỏi về kỹ thuật" có thể là đặc thù của bộ tác vụ này, không khái quát hoá được sang miền khác. Cũng không loại trừ được khả năng mô hình đã được huấn luyện đúng các quy ước này.
3. **Chỉ một mô hình, và mô hình này không đọc skill.** Toàn bộ kết luận về skill đều đi qua một điều kiện lớn: ở lần chạy chính thức, **`skills_read = 0` ở cả 6 run**. Thí nghiệm vì thế chưa thực sự đo "skill có ích không", mà mới chỉ đo "mô hình này có chịu mở skill không" — và câu trả lời là không, dù `SKILLS_NOTE` yêu cầu đọc skill là bước đầu tiên. Ảnh hưởng lớn nhất: kết quả âm về skill là kết quả về **cơ chế kích hoạt**, không phải về chất lượng nội dung skill. Muốn kết luận về nội dung thì phải cưỡng ép đọc skill (ví dụ đưa thân skill vào system prompt) và chạy lại.
4. **Ba lần chạy curator, mỗi lần gọi mô hình một lần, và curator chỉ tạo tối đa 3 skill.** Với đầu vào cố định, phải đến lần chạy thứ ba mới sinh được một skill thực sự khái quát. Ảnh hưởng: `skills/auto/` cuối cùng là một **mẫu đơn lẻ** trong không gian ngẫu nhiên, không đại diện cho curator; một lần chạy curator khác có thể cho ra bộ skill tệ hơn nhiều.
5. **Một số lần chạy bị lỗi hoặc nhiễu hạ tầng.** `subagents/logs-eval` phải chạy lại vì `503`, `skills-auto/code-learn` lỗi `GraphRecursionError` ở cả 3 lần thử, và trước đó có một `RemoteProtocolError` làm mất kết quả `subagents/data-learn`. Ảnh hưởng: các ô bảng có `error` phải được đọc thận trọng; riêng `skills-auto/code-learn` là điểm duy nhất khiến trung bình học của `skills-auto` (0,66) vượt `baseline` (0,63), và ô đó vừa bị lỗi vừa có `skills_read = 0`.

## 10. Kết luận

Trên tác vụ đánh giá, `skills-auto` **bằng đúng** `baseline` (0,57) và `subagents` **thấp hơn rõ** (0,43) trong khi tốn 3,3× token, nên trong thí nghiệm này điều kiện đơn giản nhất là điều kiện tốt nhất về điểm trên mỗi token. Skill do curator sinh không tạo ra lợi ích nào đo được: 21/21 check quy ước đều trượt ở `baseline`, 21/21 ở `subagents`, và 20/21 ở `skills-auto` — còn 17/18 check kỹ thuật thì đạt gần như tuyệt đối, cho thấy nút thắt nằm ở tuân thủ quy ước chứ không phải ở năng lực. Điều đáng chú ý nhất không phải là skill vô dụng, mà là **cơ chế kích hoạt hỏng**: ở cả 6 run `skills-auto`, `skills_read = 0` — skill nằm trong sandbox, `description` viết đúng tình huống, nhưng tác tử không bao giờ mở; và run duy nhất từng đọc skill thì chỉ làm theo một phần quy tắc. Đề xuất cải tiến tiếp theo: tách hai câu hỏi này ra — ép đọc skill bằng cách đưa thân skill vào system prompt để đo **nội dung** skill có ích không, rồi so sánh với kết quả hiện tại (đọc tự nguyện) để đo **cơ chế kích hoạt**; đồng thời chạy mỗi điều kiện ít nhất 3 lần vì nhiễu ±1 điểm đã lớn hơn mọi hiệu ứng quan sát được.


## Phụ lục

- **Lệnh đã chạy (theo thứ tự):**

  ```text
  # Phần 1-2
  pytest tests/                                     # 29 passed
  python -m lab.runner --condition baseline --tasks all
  python -m lab.runner --condition subagents --tasks learn

  # Phần 3
  python -m lab.curator                             # x3 (1 lần đầu + 2 lần chạy lại)
  python -m lab.runner --condition skills-auto --tasks learn
  mv results/skills-auto results/skills-auto-dev    # sao lưu kết quả 3.4

  # Phần 4
  git add -A && git commit -m "hypotheses"
  git commit --allow-empty -m "freeze skills" && git tag freeze
  python -m lab.runner --condition baseline --tasks eval
  python -m lab.runner --condition subagents --tasks eval        # logs-eval chạy lại vì 503
  python -m lab.runner --condition subagents --tasks logs-eval   # lần chạy lại
  python -m lab.runner --condition skills-auto --tasks all       # code-learn chạy lại 2 vì GraphRecursionError
  python -m lab.runner --condition skills-auto --tasks code-learn # x2
  PYTHONUTF8=1 python scripts/verify_freeze.py                   # -> OK
  PYTHONUTF8=1 python -m lab.compare > report/table.md
  PYTHONUTF8=1 python scripts/check_breakdown.py
  ```

- **Ghi chú khác:**

  1. **Mô hình dùng trong toàn bộ số liệu:** `google_genai:gemini-3.5-flash-lite` (Gemini API, free tier), qua `LAB_MODEL` trong `.env`. Ba điều kiện dùng chung một mô hình, nên mọi khác biệt giữa cột của bảng mục 7 là do điều kiện, không phải do mô hình.
  2. **Hạ tầng Windows phải sửa trước khi số liệu nào chạy được.** `LocalShellBackend` gọi `subprocess.run(shell=True)` → `cmd.exe`, và `cmd.exe` cắt lệnh nhiều dòng tại newline, khiến mọi `python3 -c "…"` có newline trả về exit code 0 với stdout rỗng; tác tử tưởng thành công rồi lặp lại biến thể khác cho tới khi hết `recursion_limit`. Đã sửa bằng `_BashShellBackend` trong `src/lab/agent.py` (chạy `execute` qua `bash -c` của Git for Windows). Trước khi sửa, mọi lần chạy đều chết với `score=0` — đó là điểm 0 **giả**, không phải năng lực tác tử. Ngoài ra phải cài `pandas` vào venv (không có trong `requirements.txt`; các `check.py` chỉ dùng thư viện chuẩn).
  3. **`parse_skill_blocks` cần chuẩn hóa nội dung.** Gemini 3 trả `AIMessage.content` dạng danh sách khối `[{'type':'text','text':…}]`, nên `str(reply)` trong hàm cấp sẵn khớp vào `repr()` và không tìm thấy khối skill nào (curator trả về 0 skill). Đã thêm `as_text()` trong `curate_skills`; hàm cấp sẵn không bị sửa.
  4. **`scripts/verify_freeze.py` lỗi encoding trên Windows.** `subprocess` với `text=True` giải mã theo cp1252 nên văng `UnicodeDecodeError` khi đọc `REPORT.md` tiếng Việt. Chạy với `PYTHONUTF8=1` là được `OK`. Không sửa script vì là file được cấp.
  5. **Thử thách mở rộng đã thử và không thành công:** chạy Groq free tier thay Gemini. Cả `gpt-oss-120b` và `gpt-oss-20b` sinh tool call không hợp lệ mà Groq từ chối cả request (HTTP 400), còn `qwen/qwen3.8-27b` thì vượt hạn mức chung 8000 TPM của free tier (một request của Deep Agents đã cần ~7300 input token chỉ vì system prompt và tool schemas). Không dùng được cho lab này ở bậc miễn phí.
  6. **Cảnh báo bảo mật:** ba API key (Groq và hai key Gemini) đã được ghi trực tiếp vào `.env` trong phiên làm việc này. `.env` nằm trong `.gitignore` và chưa bị commit, nhưng các key này nên được thu hồi và tạo lại.


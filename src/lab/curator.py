"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def as_text(content) -> str:
    """Chuẩn hóa nội dung trả về của LLM về một chuỗi văn bản thuần.

    Gemini 3 trả `AIMessage.content` dạng DANH SÁCH khối ([{'type': 'text', 'text': ...}]),
    còn OpenAI/Groq/DeepSeek trả chuỗi thẳng. `parse_skill_blocks` (hàm có sẵn, không sửa)
    dùng `str(reply)` nên nếu đưa thẳng danh sách vào, nó sẽ khớp vào `repr()` của dict và
    không tìm thấy dòng "=== SKILL:" nào. Ở đây gom các khối 'text' lại thành chuỗi.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(p for p in parts if p)
    return str(content)


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    results_dir, out_dir = Path(results_dir), Path(out_dir or ROOT / "skills" / "auto")

    # 1. Nạp các lần chạy TÁC VỤ HỌC; tuyệt đối bỏ qua role == "eval".
    runs = []
    for run_file in sorted(Path(results_dir, source_condition).glob("*/run.json")):
        try:
            r = json.loads(run_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print(f"skip {run_file}: unreadable JSON", flush=True)
            continue
        if r.get("role") != "learn":      # không bao giờ dùng dữ liệu tác vụ đánh giá
            continue
        failed = [(c.get("name", ""), str(c.get("detail", ""))) for c in r.get("checks", []) if not c.get("passed")]
        trace_file = run_file.parent / "trace.md"
        trace = trace_file.read_text(encoding="utf-8", errors="replace")[-6000:] if trace_file.exists() else ""
        runs.append({"task": r.get("task", run_file.parent.name), "failed": failed, "trace": trace})

    # 2. Không có phản hồi nào để rút ra -> KHÔNG gọi LLM.
    if not any(ru["failed"] for ru in runs):
        print("no failed check in any learning run: no skill written.", flush=True)
        return []

    # 3. Nhờ mô hình viết skill.
    if model is None:
        from .model import make_model
        model = make_model()
    reply = as_text(model.invoke(build_prompt(runs, max_skills)).content)
    print(f"model returned {len(parse_skill_blocks(reply))} skill block(s)", flush=True)

    # 4. Chỉ giữ skill hợp lệ, tối đa max_skills.
    written, skipped = [], []
    for name, text in parse_skill_blocks(reply):
        if len(written) >= max_skills:
            skipped.append(f"{name}: over the max_skills={max_skills} limit")
            continue
        problems = validate_skill(text, expected_name=name)
        if problems:
            skipped.append(f"{name}: {'; '.join(problems)}")
            continue
        path = out_dir / name / "SKILL.md"      # tên đã qua SAFE_NAME nên không thể thoát khỏi out_dir
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" để SKILL.md luôn là LF: hash của bộ skill không đổi theo hệ điều hành
        path.write_text(text + "\n", encoding="utf-8", newline="\n")
        written.append(path)

    for reason in skipped:
        print(f"skipped skill {reason}", flush=True)
    return written


# ---- PROMPT MẪU (điển bằng dữ liệu của các lần chạy học) --------------------------------------------------------

PROMPT_TEMPLATE = """You write SKILLs for an agent that fixes code and analyses data.
Below are the FAILED checks (name plus the review bot's feedback) and the tail of the trace of each run.

Find the procedural mistakes they share (NOT the task-specific answers) and write at most {max_skills} short
skills that help a NEW task of the same kind avoid them.

Rules:
- Be general: never name a task id, a file that belongs to one task, an answer, or a number.
- Each skill has a YAML frontmatter with `name` (lower-case, hyphens) and `description` (one sentence: WHEN TO USE),
  then at most 40 lines of imperative instructions (a checklist - checks - good habits).
- A skill must state the trigger situation in `description`, because the agent only sees name+description
  before deciding to open it.
- Output format, character for character:
=== SKILL: <name> ===
---
name: <name>
description: <when to use>
---
<content>
=== END ===

{failed_runs}"""


def build_prompt(runs: list[dict], max_skills: int) -> str:
    """Dựng prompt curator từ các lần chạy học (chỉ trường `detail` của check thất bại + phần cuối vết)."""
    parts = []
    for ru in runs:
        if not ru["failed"]:
            continue
        checks = "\n".join(f"  - {name}: {detail}" for name, detail in ru["failed"])
        parts.append(f"### task: {ru['task']}\nFAILED checks:\n{checks}\nTAIL OF THE TRACE:\n{ru['trace']}\n")
    return PROMPT_TEMPLATE.format(max_skills=max_skills, failed_runs="\n".join(parts))
# -----------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)

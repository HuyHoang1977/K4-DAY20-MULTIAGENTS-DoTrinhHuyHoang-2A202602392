"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from deepagents.backends.protocol import ExecuteResponse

# TODO 1: import các thành phần cần dùng, ví dụ:
#   from deepagents import create_deep_agent
#   from deepagents.backends import LocalShellBackend
#   from .model import make_model
#   from .subagents import get_subagents
from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------


def _bash_path() -> str | None:
    """Đường dẫn tới bash của Git for Windows, hoặc None nếu máy không có Git Bash."""
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ):
        if os.path.isfile(candidate):
            return candidate
    return None


class _BashShellBackend(LocalShellBackend):
    """`LocalShellBackend` nhưng `execute` chạy qua `bash -c` thay vì cmd.exe.

    `LocalShellBackend.execute` gọi `subprocess.run(command, shell=True)`. Trên Windows
    `shell=True` nghĩa là cmd.exe, và cmd.exe coi newline là dấu kết thúc lệnh: lệnh nhiều
    dòng mà mô hình hay viết (`python3 -c "` + code có newline + `"`) bị cắt còn lệnh rỗng,
    chạy ra exit code 0 với stdout rỗng. Tác tử thấy "thành công" nên lặp lại biến thể
    khác của cùng lệnh hỏng cho tới khi hết recursion_limit.

    bash xử lý newline và heredoc đúng, nên đường đi qua bash là cách sửa tận gốc thay vì
    dạy mô hình phải tránh lệnh nhiều dòng. Mọi thứ khác (virtual paths, PATH, biến môi
    trường) giữ nguyên theo LocalShellBackend.
    """

    def __init__(self, *args, bash: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._bash = bash

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        effective_timeout = timeout if timeout is not None else self._default_timeout
        if effective_timeout <= 0:
            raise ValueError(f"timeout must be positive, got {effective_timeout}")
        try:
            result = subprocess.run(
                [self._bash, "-c", command],  # shell=False: bash là shell thật sự
                check=False,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                text=True,
                timeout=effective_timeout,
                env=self._env,
                cwd=str(self.cwd),
            )
        except subprocess.TimeoutExpired:
            return ExecuteResponse(
                output=f"Error: command timed out after {effective_timeout}s",
                exit_code=None,
                truncated=False,
            )

        # Ghép stdout + stderr và tiền tố [stderr], giữ đúng định dạng mà LocalShellBackend
        # dùng, để mô hình không phải đọc output lạ.
        parts = []
        if result.stdout:
            parts.append(result.stdout)
        if result.stderr:
            parts.extend(f"[stderr] {line}" for line in result.stderr.strip().split("\n"))
        return ExecuteResponse(output="\n".join(parts), exit_code=result.returncode, truncated=False)


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    # Đề bài và check.py dùng lệnh POSIX (python3, cat, ls, grep). Trên Windows, execute
    # chạy qua bash của Git for Windows (_BashShellBackend) nên PATH cũng phải ở dạng POSIX,
    # còn các lệnh POSIX của đề bài đến từ thư mục usr/bin của Git.
    if os.name == "nt":
        # Đường dẫn ở dạng POSIX-forward-slash: MSYS và bash đều hiểu.
        win_root = os.environ.get("SystemRoot", r"C:\Windows").replace("\\", "/")
        path_dirs = [
            f"/{win_root.replace(':', '').lstrip('/')}/System32",
            f"/{win_root.replace(':', '').lstrip('/')}",
        ]
        # Git for Windows cung cấp các lệnh POSIX của đề bài (cat, ls, grep).
        for extra in (
            r"C:\Program Files\Git\usr\bin",
            r"C:\Program Files (x86)\Git\usr\bin",
        ):
            if os.path.isfile(os.path.join(extra, "cat.exe")):
                path_dirs.append("/" + extra.replace("\\", "/").replace(":", "").lstrip("/"))
                break

        # Đề bài và check.py gọi `python3`, nhưng venv trên Windows chỉ có `python.exe`.
        # Tạo shim script của bash trong sandbox (không phải .bat, vì execute đã chạy qua bash).
        shim_dir = sandbox / ".bin"
        path_dirs.insert(0, shim_dir.as_posix())
        try:
            shim_dir.mkdir(parents=True, exist_ok=True)
            (shim_dir / "python3").write_text(
                f'#!/usr/bin/env bash\nexec "{sys.executable}" "$@"\n', encoding="utf-8"
            )
            os.chmod(shim_dir / "python3", 0o755)
        except OSError:
            pass  # không tạo được lệnh thì bỏ qua, agent vẫn dùng được `python`

        # bash nhận PATH dạng POSIX: thư mục venv phải ở dạng /c/... (C:/... sẽ không tìm thấy).
        py_posix = "/" + Path(sys.executable).parent.as_posix().replace(":", "").replace("\\", "/").lstrip("/")
        path_dirs.insert(1, py_posix)
    else:
        path_dirs = [str(Path(sys.executable).parent), "/usr/local/bin", "/usr/bin", "/bin"]

    env = {
        "PATH": os.pathsep.join(path_dirs),
        "HOME": str(sandbox),
        # không sinh __pycache__ trong workspace
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    kwargs = {
        "root_dir": sandbox,
        "virtual_mode": True,
        # KHÔNG kế thừa biến môi trường của tiến trình cha, nếu không khóa API sẽ lộ qua execute("env")
        "inherit_env": False,
        "env": env,
        "timeout": 120,
    }
    if os.name == "nt":
        bash = _bash_path()
        if bash:
            return _BashShellBackend(bash=bash, **kwargs)
        # Không có Git Bash: cmd.exe sẽ cắt lệnh nhiều dòng, nhưng vẫn hơn là không chạy được.
    return LocalShellBackend(**kwargs)


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in {"single", "subagents"}:
        raise ValueError(f"mode không hợp lệ: {mode!r} (chỉ nhận 'single' hoặc 'subagents')")

    kwargs: dict = {}
    prompt = BASE_PROMPT

    if mode == "subagents":
        # subagent KHÔNG nhận BASE_PROMPT, nên phải nối PATHS_NOTE vào system_prompt của từng subagent,
        # nếu không subagent sẽ trộn lẫn "/workspace/x" và "workspace/x" rồi báo không tìm thấy tệp.
        kwargs["subagents"] = [
            {**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE}
            for sub in get_subagents()
        ]
        prompt = prompt + SUBAGENTS_NOTE

    if use_skills:
        # đường dẫn ảo, tính từ root_dir của backend
        kwargs["skills"] = ["/skills/"]
        prompt = prompt + SKILLS_NOTE

    return create_deep_agent(
        model=model if model is not None else make_model(),
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )

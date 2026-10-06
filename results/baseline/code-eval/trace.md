### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: glob
{"pattern": "**/*", "path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-312.pyc', '/workspace/bookings/__pycache__/billing.cpython-312.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-312.pyc', '/workspace/bookings/__pycache__/schedule.cpython-312.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-312.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool call: execute
{"command": "pytest workspace/tests/test_bookings.py"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\lab-sb-nggs1fh_
plugins: anyio-4.15.1, langsmith-0.14.4
collected 0 items / 1 error

=================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py ______________
ImportError while importing test module '~\AppData\Local\Temp\lab-sb-nggs1fh_\workspace\tests\test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
D:\AI-Action\phase2-track3\day20\K4-DAY20-MULTIAGENTS-DoTrinhHuyHoang-2A202602392\tasks\code-eval\workspace\tests\test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ===========================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 0.15s ===============================

[Command failed with exit code 2]

### Tool call: execute
{"command": "python -m pytest workspace/tests/test_bookings.py"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\lab-sb-nggs1fh_
plugins: anyio-4.15.1, langsmith-0.14.4
collected 0 items / 1 error

=================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py ______________
ImportError while importing test module '~\AppData\Local\Temp\lab-sb-nggs1fh_\workspace\tests\test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
D:\AI-Action\phase2-track3\day20\K4-DAY20-MULTIAGENTS-DoTrinhHuyHoang-2A202602392\tasks\code-eval\workspace\tests\test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ===========================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 0.09s ===============================

[Command failed with exit code 2]

### Tool call: execute
{"command": "python -m pytest workspace/tests/test_bookings.py -o pythonpath=workspace"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\lab-sb-nggs1fh_
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

workspace\tests\test_bookings.py FF.                                     [100%]

================================== FAILURES ===================================
______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

D:\AI-Action\phase2-track3\day20\K4-DAY20-MULTIAGENTS-DoTrinhHuyHoang-2A202602392\tasks\code-eval\workspace\tests\test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
workspace\bookings\schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
workspace\bookings\schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means 

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: glob
{"pattern": "**/*.py", "path": "workspace"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py"}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool call: edit_file
{"new_string": "    import math\n    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    return math.ceil(minutes / block)", "old_string": "    return round(minutes / block)", "file_path": "workspace/bookings/billing.py"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/schedule.py", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    else:\n        slots = list(slots)\n    slots.append(slot)\n    return slots", "old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"old_string": "def parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "new_string": "def parse_duration(text):\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    text = text.strip()\n    # Check 1h30m or 2h or 45m\n    m = re.fullmatch(r\"(?:(\\d+)h)?(?:(\\d+)m)?\", text)\n    if m and any(m.groups()):\n        hours = int(m.group(1)) if m.group(1) else 0\n        minutes = int(m.group(2)) if m.group(2) else 0\n        return hours * 65 if False else hours * 60 + minutes # wait, hours * 60 + minutes\n\n    # Check HH:MM or H:MM\n    m_hm = re.fullmatch(r\"(\\d+):(\\d{2})\", text)\n    if m_hm:\n        return int(m_hm.group(1)) * 60 + int(m_hm.group(2))\n\n    # Check bare number (minutes)\n    m_num = re.fullmatch(r\"(\\d+)\", text)\n    if m_num:\n        return int(m_num.group(1))\n\n    raise ValueError

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: execute
{"command": "python -m pytest workspace/tests/test_bookings.py -o pythonpath=workspace"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\lab-sb-nggs1fh_
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

workspace\tests\test_bookings.py ...                                     [100%]

============================== 3 passed in 0.01s ==============================

[Command succeeded with exit code 0]

### Tool call: write_file
{"content": "import pytest\nfrom bookings.timeutil import parse_duration\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\n\ndef test_parse_duration():\n    assert parse_duration(\"1h30m\") == 90\n    assert parse_duration(\"2h\") == 120\n    assert parse_duration(\"45m\") == 45\n    assert parse_duration(\"1:30\") == 90\n    assert parse_duration(\"45\") == 45\n    assert parse_duration(\"  2h  \") == 120\n    with pytest.raises(ValueError):\n        parse_duration(\"invalid\")\n\ndef test_billing_negative():\n    with pytest.raises(ValueError):\n        billable_blocks(-1)\n    assert billable_blocks(0) == 0\n    assert billable_blocks(15) == 1\n    assert billable_blocks(16) == 2\n\ndef test_add_slot_state():\n    s1 = add_slot(\"a\")\n    assert s1 == [\"a\"]\n    s2 = add_slot(\"b\")\n    assert s2 == [\"b\"]\n    assert s1 == [\"a\"]\n", "file_path": "workspace/tests/test_extra.py"}

### Tool result
Updated file /workspace/tests/test_extra.py

### Tool call: execute
{"command": "python -m pytest workspace/tests/ -o pythonpath=workspace"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\lab-sb-nggs1fh_
plugins: anyio-4.15.1, langsmith-0.14.4
collected 6 items

workspace\tests\test_bookings.py ...                                     [ 50%]
workspace\tests\test_extra.py ...                                        [100%]

============================== 6 passed in 0.01s ==============================

[Command succeeded with exit code 0]

### Tool call: delete
{"file_path": "workspace/tests/test_extra.py"}

### Tool result
Deleted /workspace/tests/test_extra.py

### Tool call: execute
{"command": "python -m pytest workspace/tests/test_bookings.py -o pythonpath=workspace"}

### Tool result
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: ~\AppData\Local\Temp\lab-sb-nggs1fh_
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

workspace\tests\test_bookings.py ...                                     [100%]

============================== 3 passed in 0.01s ==============================

[Command succeeded with exit code 0]

### Assistant
[{'type': 'text', 'text': 'I have successfully fixed the issues in the `bookings` package so that all tests pass and every function conforms strictly to its docstring and specifications:\n\n- **`bookings/timeutil.py`**: Updated `parse_duration` to support all required formats specified in its docstring (`"1h30m"`, `"2h"`, `"45m"`, `"1:30"`, `"45"`, and surrounding whitespace).\n- **`bookings/billing.py`**: Updated `billable_blocks` to always round up (using `math.ceil`) and raise a `ValueError` when `minutes < 0`.\n- **`bookings/schedule.py`**: Fixed `add_slot` to avoid mutable default arguments (`slots=[]`), ensuring separate calls do not share state.\n\n### Summary of Changed Files\n- `workspace/bookings/timeutil.py`\n- `workspace/bookings/billing.py`\n- `workspace/bookings/schedule.py`', 'extras': {'signature': 'EmAKXgFpFH0TsR4O1XZtRtdbpRvlGEvOQjy6KnwEn7OzCzvcap6doss/jyFDKdh0+9lKQjNeQhQlu+h7kHn507W92xv7NBkjKKPY/RtLfoXN05ApB89rhT1D5BmPwBHAckE='}}]
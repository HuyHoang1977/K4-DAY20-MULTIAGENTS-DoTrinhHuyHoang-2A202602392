---
name: comprehensive-regression-testing-and-type-hints
description: WHEN FIXING CODE OR ADDING FEATURES: Use this skill to ensure all new/modified functions have full type annotations, regression tests, and clean workspaces.
---
- Add type annotations (parameters and return values) to every public function (names not starting with `_`).
- Create a dedicated regression test file (`tests/test_regressions.py`) with at least one distinct test function per fixed bug.
- Never modify or delete original test files provided in the repository unless explicitly allowed.
- Clean up any temporary test files you created during development before finishing the task.

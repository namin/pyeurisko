# Run

With execute_command, use a `workdir` with the current directory.

- `pip install -e ".[dev]" && pytest tests/`
  - Make sure the tests pass.
- `python examples/run_eurisko.py -c 10 -v 2 -i 1.0`
  - Analyze and suggests further improvements.
  - Focus on errors, and be mindful of success rates of heuristics.
  - The heuristics are indvidually implemented in the directory `eurisko/heuristics` following the pattern `h*.py`.

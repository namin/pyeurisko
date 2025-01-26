# Run

With execute_command, use a `workdir` with the current directory.

- `pip install -e ".[dev]"`
  Install the package (only once).
- `python -m eurisko.main`
  Run the program (whenever).

The task is to rewrite the heuristics in the directory `eurisko/heuristics/`.
To see which are enabled, they are listed in the `if h['name'] not in` then the enabled heuristics in the the `continue` condition in `initialize_all_heuristics`.

The pattern to follow is that of `h2`. `h3` has been translated but is not yet being triggered, suggesting there could be a bug.

The reference implementation is in `../eurisclo/`. There, you can see `src/heuristics.lisp` as well as the task management and main in `src/eurisko.lisp`.

Please analyze all these files, and let's discuss a next task. I think we should slowly port the heuristics.

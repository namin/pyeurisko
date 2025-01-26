# Run

With execute_command, use a `workdir` with the current directory.

- `pip install -e ".[dev]"`
  Install the package (only once).
- `python -m eurisko.main`
  Run the program (whenever).
- `python tools/convert_units.py ../eurisclo/src/units.lisp eurisko/units/lisp_units.py lisp`
  Run a wip tool to fix to convert units from lisp to Python.
  This will generate lots of units in `eurisko/units/lisp_units.py`.
  Your task is to iterate between running main and fixing and running this tool.

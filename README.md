# Python solver for the Jindosh riddle in Dishonored 2

This is an automatic solver for the [Jindosh riddle](https://dishonored.fandom.com/wiki/The_Jindosh_Riddle) in Dishonored 2 implemented in Python. It solves it as a CSP using the [python-constraint](https://github.com/python-constraint/python-constraint) library.

## Instructions
With [`pipenv`](https://github.com/pypa/pipenv):
1. Run `pipenv install`.
2. Replace the text in `riddle.txt` with your riddle.
3. Run `pipenv run python solver.py`.

Without `pipenv`:
1. Run `python3 -m pip install python-constraint`.
2. Replace the text in `riddle.txt` with your riddle.
3. Run `python3 solver.py`.

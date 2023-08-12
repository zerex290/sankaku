# Contributing to sankaku

All contributions to sankaku library are welcome. Below will be described
contribution guidelines.

## Reporting a bug

When reporting a bug, please do the following:

- Include the code, which caused the bug to happen;
- Describe what you expected to happen;
- Describe what actually happened;
- Provide a stacktrace with bug information.

## Fixing bugs, adding new features, etc.

Before sending your changes to `main` branch of repository, please do the
following things:

- Create a fork of sankaku repository;
- Create a branch from `main`;
- Install additional dependencies to your project path via `pip install sankaku[dev]`;
- Develop bug fixes, new features, etc.
- Make sure that your changes are compatible with Python 3.8+;

If you fixed a bug, developed a new feature, etc:

- Run library tests with pytests: `pytest -svv tests`
- Run static type checking with pyright: `pyright sankaku`;
- Run linting with ruff: `ruff sankaku`;

> It is allowed to suppress some error messages from ruff and pyright in cases
when you're sure that such errors are unnecessary or incorrect, but in general
code should be formatted according to these messages.

After all test cases, static type checks and linting passed, please check
'Code style guide' section and apply changes to your code using `yapf` or on
your own.

Send a pull request with changes to `main` repository of sankaku.

## Code style guide

- PEP8 should be followed as much as possible;
- Preferable line length is 79, but it is allowed to write code up to 88 symbols
  in one line in cases when splitting code on separate lines looks 'ugly';
- All objects defined as public in module, should be declared in `__all__`;
- All public functions and methods should have docstrings;
- All public classes should have docstrings as well, either in `__init__` method
  (if it is presented) or after class declaration otherwise;
- All functions and methods should have type hints.

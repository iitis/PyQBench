(section/installation)=

# Installing

## Basic installation

The most up-to-date version of PyQBench can be installed from PyPI:

```shell
pip install pyqbench
```

This installs `qbench` library, as well as the CLI tool. To verify that the install suceeded,
you can check if the package is importable and the CLI tool is visible in your path.

```shell
python -c "import qbench" # Should silently pass
qbench -h                 # Should produce help message
```


## Development installation

If you want to contribute to PyQBench, clone the repository and install the package
in development mode. The example below clones repository via SSH and installs the package.

```shell
git clone git@github.com:iitis/PyQBench.git
pip install -e PyQBench
```

### Installing extra dependencies
When developing PyQBench, you most likely want to install dependencies needed for running
tests, assisting you in following style guidelines and building documentation. To this end,
PyQBench defines the following extras:

- `test`: dependencies needed for running tests
- `dev`: development tools (e.g. linters)
- `docs`: tools needed for building the documentation

Extras can be installed, as usually, by passing them in square brackets to `pip install` command.
The extras can be mixed and matched (although you probably want to install all of them).
As an illustration, example below installs the cloned repository with `test` and `dev` extras:

```shell
pip install -e PyQBench[test,dev]
```

### Installing pre-commit hook

PyQBench provides a [pre-commit](https://pre-commit.com/) configuration matching the one used in our
CI. The hooks run linters and static analysis tools, allowing you to catch any typing errors, common 
mistakes and verify inconsistencies in your code style before pushing the code to the repository (or 
its fork).

To use the hooks, first install pre-commit:

```shell
pip install pre-commit
```

And then install the hooks:

```shell
pre-commit install
```

## List and explanation of the dependencies

This section discusses dependencies used by PyQBench and their role in the project. Please note
that transitive dependencies are not included in the list.

### Mandatory dependencies

- `qiskit`: used for constructing quantum circuits and interfacing with quantum devices
- `amazon-braket-sdk` and `qiskit-braket-provider`: used for interacting with Amazon Braket devices
- `mthree`: used for readout error mitigation
- `numpy` and `scipy`: basic libraries for numerical calculations
- `tqdm`: used for rendering progress bars in CLI
- `pyaml` and `pydantic`: for reading/writing input/output files in the CLI, and validating their
  contents
- `pandas`: used for outputting final CSV file with discrimination probabilities

### Test dependencies

- `pytest`: used for defining and running tests
- `pytest-cov`: used with pytest for obtaining test-coverage

### Development dependencies

- `flake8`: used for linting code
- `black`: used for formatting code in a consistent way
- `isort`: used for consistently sorting imoprts
- `mypy`: used for static analysis of type hints

### Docs dependencies

- `sphinx`: framework used for building this documentation
- `pydata-sphinx-theme`: theme of this documentation
- `myst-parser`: used to allow Markdown instead of ReST in the docs

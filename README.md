![Logo](https://raw.githubusercontent.com/iitis/pyqbench/master/docs/source/_static/logo.png)

![GitHub](https://img.shields.io/github/license/iitis/PyQBench)
![PyPI](https://img.shields.io/pypi/v/pyqbench)
![Read the Docs](https://img.shields.io/readthedocs/pyqbench)

https://arxiv.org/abs/2304.00045

**PyQBench** is a package for benchmarking gate-based quantum computers by estimating how well they can discriminate between two von Neumann measurements.  **PyQBench** is built around the Qiskit ecosystem and its configuration is driven by YAML files describing the experiment scenarios and backends to be used.

## Installation

PyQBench can be installed from PyPI using `pip`:

```bash
pip install pyqbench
```

## Quickstart

The most basic way to use PyQBench is by using its CLI. For more advanced usages see [PyQBench's docs](https://pyqbench.readthedocs.io/en/latest/notebooks/Example%2001%20discriminating%20measurements%20in%20Hadamard%20basis.html).

PyQBench's CLI can only run experiments using the parametrized [Fourier family of measurements](https://pyqbench.readthedocs.io/en/latest/reference/fourier.html#qbench.fourier.FourierComponents). Here's a basic example of how it works:

### Step 1: preparing configuration files

The first YAML configuration file describes the experiment scenario to be executed:

```yml
type: discrimination-fourier
qubits:
    - target: 1
      ancilla: 2
angles:
    start: 0
    stop: 2 * pi
    num_steps: 3
gateset: ibmq
method: direct_sum
num_shots: 100
```
The second file describes the backend. The precise format of this file depends on the type of the backend, here's an example for Qiskit's IBMQ backend:

```yml
name: ibmq_quito
asynchronous: true
provider:
    hub: ibm-q
    group: open
    project: main
```
IBMQ backends typically require an access token to IBM Quantum Experience. Since it would be unsafe
to store it in plain text, the token has to be configured separately in ``IBMQ_TOKEN`` environmental variable.

### Step 2: running the experiment
After preparing YAML files defining experiment and backend, running the benchmark can be launched by using the following command line invocation:
```bash
qbench disc-fourier benchmark experiment_file.yml backend_file.yml --output async_results.yml
```

The `benchmark` command will submit several batch jobs that will run asynchronously. It is non blocking, meaning that it won't wait for the jobs to finish.

You can check the status of the submitted jobs by running:

```bash
qbench disc-fourier status async_results.yml
```

### Step 3: resolving asynchronous jobs
To get the actual results from the submitted asynchronous jobs, you can use `resolve` command.
```bash
qbench disc-fourier resolve async-results.yml resolved.yml
```

This operation is blocking and will wait for all the results to be available.

### Step 4: tabulate results

Finally, the obtained results can be summarized into a table.
```bash
qbench disc-fourier tabulate results.yml results.csv
```

Here's what the result looks like:

| target      | ancilla     | phi           | ideal_prob      | disc_prob     | mit_disc_prob   |
| :----:      | :----:      |  :----:       | :----:          |    :----:     |         :----:  |
| 1           | 2           | 0             | 0.5             | 0.57          | 0.57            |
| 1           | 2           | 3.14          | 1               | 0.88          | 0.94            |
| 1           | 2           | 6.28          | 0.5             | 0.55          | 0.56            |


## What else can PyQBench do?

The above quickstart guide does not cover:

- Running the experiments in synchronous (blocking mode)
- Using error mitigation via [M3Mitigation suite](https://qiskit.org/ecosystem/mthree/stubs/mthree.M3Mitigation.html)
- Using user-defined measurements instead of the default Fourier

Refer to [PyQBench's documentation](https://pyqbench.readthedocs.io/en/latest/index.html) for further reading.

## Authors and Citation

PyQBench is the work of Konrad Jałowiecki, Paulina Lewandowska and Łukasz Pawela.
Support email for questions ``dexter2206@gmail.com``.
If you use PyQBench, please cite as per the included [BibTeX file](https://github.com/iitis/PyQBench/tree/pl/readme/pyqbench.bib
).

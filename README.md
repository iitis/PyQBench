# PyQBench

PyQBench is a package for benchmarking gate-based quantum computers by
estimating how well they can discriminate between two von Neumann measurements. Benchmarks in PyQBench work by experimentally determining the probability of correct discrimination by the device under test and comparing the result with the ideal, theoretical predictions. PyQBench offers a simplified, ready-to-use, command line interface (CLI) for running benchmarks using a predefined parametrized Fourier family of measurements. For more advanced scenarios, PyQBench offers a way of employing user-defined measurements instead of predefined ones. PyQBench is built around the Qiskit ecosystem and the configuration of CLI is done by YAML  files describing the benchmark to be performed and the description of the backend on which the benchmark should be run. Additionally, PyQBench's CLI can be used in synchronous and asynchronous modes.

For more details on how to use PyQBench you can refer to the documentation located here:

https://pyqbench.readthedocs.io/en/latest/

or the article:

https://arxiv.org/abs/2304.00045

## Installation

We encourage installing PyQBench via ``pip``. The following command installs needed packages and actual versions neceserry to use PyQBench.

```bash
pip install pyqbench
```

## Set-up
### Von Neumann measurements
A von Neumann measurement $\mathcal{P}$ is a collection of rank--one projectors
 that sum up to identity. If $U$ is a unitary matrix,
one can construct a von Neumann measurement $\mathcal{P}_{U}$ by taking projectors onto its columns. In this
case we say that $\mathcal{P}_{U}$ is described by the matrix $U$.
To implement an arbitrary von Neumann measurement $\mathcal{P}_{U}$, one has to first apply $U^\dagger$
 and then follow with $Z$-basis measurement.
In PyQBench we will consider discrimination task between single qubit measurements
$\mathcal{P}_I$, performed in the computational Z-basis, and an alternative measurement $\mathcal{P}_U$ performed in the basis $U$.

### Discrimination scheme
In general, the discrimination scheme  requires an
auxiliary qubit. First, the joint system is prepared in some state $\ket{\psi}$. Then, one of the
measurements,  either $\mathcal{P}_U$ or $\mathcal{P}_I$, is performed on the first part of the system. Based on its outcome $i$, we choose another POVM $\mathcal{P}_{V_i}$ and perform it on the second
qubit, obtaining the output in $j$. Finally, if $j=0$, we say that the performed measurement is
$\mathcal{P}_U$, otherwise we say that it was $\mathcal{P}_I$. Naturally, we need to repeat the
same procedure multiple times for both measurements to obtain a reliable estimate of the underlying
probability distribution. In PyQBench, we assume that the experiment is repeated the same number of
times for both $\mathcal{P}_U$ and $\mathcal{P}_I$.

Current NISQ devices are unable to perform conditional measurements, which is the biggest
obstacle to implementing our scheme on real hardware. However, we circumvent this problem by
slightly adjusting our scheme so that it only uses components available on current devices.
For this purpose, we use two possible options: using a postselection or a direct sum.

### Discrimination scheme for parameterized Fourier family of measurements

The parametrized Fourier family of measurements is defined as a set of the measurements for

$U_\phi = H
\begin{pmatrix} 1&0\\0&e^{i \phi}\end{pmatrix}  H^\dagger,
$

where $\phi \in [0, 2\pi]$
and $H$ is the Hadamard matrix of dimension two. For this family of measurement we calculate components $\ket{\psi}$, $\mathcal{P}_{V_i}$ and probability of discirmination to implement it in CLI mode.
## Creating Your First Benchmark with PyQBench
As already described, PyQBench can be used both as a library and a CLI. Both functionalities are
implemented as a part of ``qbench`` Python package. The exposed CLI tool is also named ``qbench``.
A general form of the CLI invocation is:
```bash
qbench <benchmark-type> <command> <parameters>
```

The workflow with PyQBench's CLI can be summarized
as the following list of steps:
- Preparing configuration files describing the backend and the experiment scenario.
- Submitting/running experiments. Depending on the experiment scenario, execution can be synchronous, or asynchronous.
- (optional) Checking the status of the submitted jobs if the execution is asynchronous.
- Resolving asynchronous jobs into the actual measurement outcomes.
- Converting obtained measurement outcomes into tabulated form.

The first YML configuration file describes the experiment ``experiment_file.yml`` scenario to be executed.

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
The second file describes example of the backend in ``backend_file.yml``.

```yml
name: ibmq_quito
asynchronous: true
provider:
    hub: ibm-q
    group: open
    project: main
```
IBMQ backends typically require an access token to IBM Quantum Experience. Since it would be unsafe
to store it in plain text, the token has to be configured separately in ``IBMQ_TOKEN``
environmental variable.

After preparing YAML files defining experiment and backend,
running the benchmark can be launched by using the following command line invocation:
```bash
qbench disc-fourier benchmark experiment_file.yml backend_file.yml
```
The output file will be printed to stdout. Optionally, the ``--output OUTPUT`` parameter might be provided to write the output to the ``OUTPUT`` file instead.
```bash
qbench disc-fourier benchmark experiment_file.yml backend_file.yml --output async_results.yml
```

The result of running the above command can be twofold:
- If backend is asynchronous, the output will contain intermediate data containing, amongst others, ``job_ids`` correlated with the circuit they correspond to.
- If the backend is synchronous, the output will contain measurement outcomes (bitstrings) for each of the circuits run.

PyQBench provides also a helper command that will fetch the statuses of asynchronous jobs. The command is:
```bash
qbench disc-fourier status async_results.yml
```

For asynchronous experiments, the stored intermediate data has to be resolved in actual
by using the following command:
```bash
qbench disc-fourier resolve async-results.yml resolved.yml
```

The resolved results, stored in ``resolved.yml``, would look just like if the experiment was
run synchronously and no matter which option we use, results file has to be passed to ``tabulate``
command:
```bash
qbench disc-fourier tabulate results.yml results.csv
```

## Authors and Citation

PyQBench is the work of Konrad Jałowiecki, Paulina Lewandowska and Łukasz Pawela.
Support email for questions ``dexter2206@gmail.com``.
If you use PyQBench, please cite as per the included [BibTeX file](https://arxiv.org/abs/2304.00045).

# Usage as a CLI tool

Using PyQBench as a library allows one to conduct, in principle, arbitrary two-qubit von Neumann 
measurement experiment. However, as discussed in the previous guide, it requires some amount of 
boilerplate code.

However, for a Fourier parametrized family of measurements, PyQBench offers a simplified way of 
performing the experiment using a Command Line Interface (CLI).


## Overview of CLI workflow

Experiments that can be run using `qbench` cli tool are separate into stages. This is a design 
choice that ensures a reasonable level of fault-tolerance. If at any stage fails (e.g. due to 
network error), it can be repeated without running everything from the beginning.

The workflow is best describe as a list of steps:

1. You prepare configuration files describing backend and the experiment scenario.
2. Submit/run experiments. Depending on the experiment scenario, execution can be synchronous,
   or asynchronous.
3. (optional) If the execution is asynchronous, you can check status of the submitted jobs.
4. For asynchronous jobs, you need to *resolve* jobs into actual measurements.
5. Obtained measurements are used for computing discrimination probabilities and outputting the 
   resulting table. 

## Defining the experiment

Experiments are defined in YAML files. An example experiment definition looks as follows.

```yaml
type: discrimination-fourier
qubits:
  - target: 0
    ancilla: 1
  - target: 2
    ancilla: 3
angles:
  start: 0
  stop: 2 * pi
  num_steps: 50
gateset: ibmq
method: direct_sum
num_shots: 100
```

Let's break it down:

- The `type` describes type of the experiment. Currently, the only option for `type` is 
  `discrimination-fourier`. In the future, other benchmarks may be added, in which keys the 
  `types` key should contain their name.
- The `qubits` list describes pair of qubits on which the experiment should be run. In our 
  example, the benchmark will run on qubits 0, 1 and 2, 3. Notice that we distinguish between 
  ancilla and target qubit, so e.g. 
  ```yaml
  qubits:
    - target: 0
      ancilla: 1
  ```
  is not the same as 
  ```yaml
  qubits:
    - ancilla: 0
      target: 1
  ```
- The `angles` key describe range of angles for Fourier parametrized family. The range is always 
  uniform, starts at the `start`, ends at `stop` and contains `num_steps` points, including both 
  `start` and `stop`. The start and stop can be arithmetic expressions using `pi` literal. For 
  instance range defined as:
  ```yaml
  angles:
    start: 0
    stop: 2 * pi
    num_steps: 3
  ```
  would contain three angles, 0, $\pi$ and $2\pi$.
- The `gateset` key informs what gates can be used in the experiment. The possible choices are 
  the same as for {class}`FourierComponents <qbench.fourier.FourierComponents>`.
- The `method` can take one of two values: `direct_sum` or `postselection`, and as the name 
  suggests, defines which method is used to implement the experiment.
- The `num_shots` defines how many shots are performed in the experiment for particular angle, 
  qubit pair and circuit. 

For the purpose of calculating possible costs, this is how you compute total number of shots and 
executed circuits. Let $N$ be the number of qubit pairs in `qubits` key and let $M$ be the number
of steps defined in the `angles` key. Then number of executed circuits is $2MN$ for the 
`direct_sum` method and $4MN$ for the `postselection` method. Each of those circuits is executed 
`num_shots` times.

Observe that the experiment file does not specify what backend to use. This way, the same 
experiment file can be used on multiple backends.

## Defining the backend

The backend is also specified in YAML file. But here's where things get complicated. Different 
backends may require different information to be used. For instance, IBMQ backends might require 
hub, group and project, whereas backends from the `Aer` package do not. Hence, the exact format of 
the YAML file depends on what backend one wants to use. Below are the available options.

### IBMQ backends

The description of IBMQ backend looks as follows, with the obvious meaning of most of the 
parameters:

```yaml
name: ibmq_quito
asynchronous: true
provider:
  hub: ibm-q
  group: open
  project: main
```

The only key that requires the explanation is `asynchronous` which determines whether 
experiments will be run asynchronously or not. We recommend setting it to `true`, unless your 
experiment is really small (several circuits total).

IBMQ backends typically require and access token to IBM Quantum Experience. It would be unsafe 
to store them in plain text, and therefore the token is configured separately. Before running 
the experiment, you should place your token in the `IBMQ_TOKEN` environmental variable.

## Backends obtainable from simple providers

In many cases, backend can be created using `Provider.get_backend()` method. For such cases,
PyQBench provides a simple description. For instance:

```yaml
provider: qiskit_braket_provider:AWSBraketProvider
name: SV1
asynchronous: true
```

This backend will be created using code similar to the one below:

```python
from qiskit_braket_provider import AWSBraketProvider

provider = AWSBraketProvider()
backend = provider.get_backend("SV1")
```

For this to work, the following conditions have to be satisfied:

- `provider` key has to contain full Python path of the provider class, where the class itself 
  is separated from the module with `:`. 
- The provider class needs to have parameter-less initializer.

The `asynchronous` key, as in other backends, determines if the backend will be used 
asynchronously (`true`) or synchronously (`false`).

:::{note}
If you are using AWSBraketProvider, you need to have the AWS CLI configured on your machine.
:::

## Backends constructed from a simple function call

If your backend can be obtained by calling a simple function (without a need for creating a 
provider or other objects), you can define it as follows:

```yaml
factory: mypackage.my_module:create_backend
asynchronous: false
args:
  - backend_name
kwargs:
  foo: bar  
run_options:
  baz: 123
```

This backend would be constructed using code similar to the one below:
```python
from mypackage.my_module import create_backend

backend = create_backend("backend_name", foo="bar")
```
Whenever the circuit is run using this backend, an addition `baz=123` keyword parameter would be 
passed to `backend.run` method.

Except from the factory, other parameters are optional (e.g. you don't have to provide `args` or 
`kwargs` if your `create_backend` function does not have parameters).

As a practical example, this is how you would define local Braket backend:

```yaml
factory: qiskit_braket_provider:BraketLocalBackend
args:
  - "braket_sv"
```


## Notes on using the asynchronous flag

Some backends may not support asynchronous execution. This might be especially the case with 
local simulators. For asynchronous execution to work, the following conditions have to be met:

- Jobs returned by the backend have unique `job_id`
- Job object is retrievable from the backend using `backend.retrieve_job` method, even from 
  another process (e.g. if the original process running the experiment has finished).

Since PyQBench cannot determine if the job retrieval works for given backend, your are 
responsible for checking it yourself. 

## Running the experiment and collecting measurements data

### Starting the experiment
Running the experiment is done by using the following command line invocation:

```text
qbench disc-fourier benchmark experiment_file.yaml backend_file.yaml
```

The output file will be printed to stdout. Optionally, the `--output OUTPUT` flag might be 
provided to write the output to the `OUTPUT` file instead.

The result of running the above command can be twofold:

- If backend is asynchronous, the output will contain intermediate data containing, amongst 
  others, job _ids correlated with the circuit they correspond to.
- If the backend is synchronous, the output will contain measurement data (bitstrings) for each 
  of the circuits run.

:::{note}
Synchronous benchmarks can take quite a lot of time. For your convenience, the progress bar will 
be displayed to provide an estimate on how long the benchmark will take. However, please 
remember that the estimate might be quite a bit off for backends that use external APIs or queues.
This is because it is impossible to anticipate the future load of the external resources.
:::

For asynchronous experiments, the output looks similar to the one below:
```yaml
metadata:
  experiment:
    type: discrimination-fourier
    qubits:
    - {target: 0, ancilla: 1}
    angles: {start: 0.0, stop: 6.283185307179586, num_steps: 3}
    gateset: ibmq
    method: postselection
    num_shots: 100
  backend_description:
    provider: qiskit_braket_provider:AWSBraketProvider
    name: SV1
    run_options: {}
    asynchronous: true
results:
- job: {aws_job_id: 'arn:aws:braket:eu-west-2:673402117850:quantum-task/e22f4792-a082-4ae1-af53-0f024792fd72;arn:aws:braket:eu-west-2:673402117850:quantum-task/79b23b9d-e48e-4249-867c-15dd889afac7;arn:aws:braket:eu-west-2:673402117850:quantum-task/dfa4f61a-9ae3-42d8-a1ba-93d4f126d1e4;arn:aws:braket:eu-west-2:673402117850:quantum-task/193adaba-7364-4947-962a-01c220105912;arn:aws:braket:eu-west-2:673402117850:quantum-task/07c89ced-08ab-4102-92eb-fb50f0a68b9f;arn:aws:braket:eu-west-2:673402117850:quantum-task/e0c0b9a5-8f18-4b49-aeba-540ccdebc56d;arn:aws:braket:eu-west-2:673402117850:quantum-task/688f1c6e-ef5d-4c16-b4f8-4c32051d6fe2;arn:aws:braket:eu-west-2:673402117850:quantum-task/70b9eb68-e739-4431-adaf-f3840058aef2;arn:aws:braket:eu-west-2:673402117850:quantum-task/2fc41fa7-114b-4690-bb59-744885ae7b01;arn:aws:braket:eu-west-2:673402117850:quantum-task/8a8cd36c-cabd-48e1-bd06-e8645dd5810c;arn:aws:braket:eu-west-2:673402117850:quantum-task/eb34e000-9410-428e-9fae-72a731841bb6;arn:aws:braket:eu-west-2:673402117850:quantum-task/25e5ed04-1386-4846-9b7b-ae7da5d23334'}
  keys:
  - [0, 1, id_v0, 0.0]
  - [0, 1, id_v1, 0.0]
  - [0, 1, u_v0, 0.0]
  - [0, 1, u_v1, 0.0]
  - [0, 1, id_v0, 3.141592653589793]
  - [0, 1, id_v1, 3.141592653589793]
  - [0, 1, u_v0, 3.141592653589793]
  - [0, 1, u_v1, 3.141592653589793]
  - [0, 1, id_v0, 6.283185307179586]
  - [0, 1, id_v1, 6.283185307179586]
  - [0, 1, u_v0, 6.283185307179586]
  - [0, 1, u_v1, 6.283185307179586]
```

For synchronous experiment, this looks as follows (the file is truncated and showing only 
several entries in the `data` section:
```yaml
metadata:
  experiment:
    type: discrimination-fourier
    qubits:
    - target: 0
      ancilla: 1
    - target: 1
      ancilla: 2
    - target: 1
      ancilla: 3
    angles:
      start: 0.0
      stop: 6.283185307179586
      num_steps: 21
    gateset: ibmq
    method: direct_sum
    num_shots: 10000
  backend_description:
    name: ibmq_belem
    asynchronous: true
    provider:
      group: open
      hub: ibm-q
      project: main
data:
- target: 0
  ancilla: 1
  phi: 0.0
  results_per_circuit:
  - name: id
    histogram:
      '00': 2727
      '01': 2320
      '10': 2701
      '11': 2252
  - name: u
    histogram:
      '00': 2583
      '01': 2482
      '10': 2639
      '11': 2296
- target: 0
  ancilla: 1
  phi: 0.3141592653589793
  results_per_circuit:
  - name: id
    histogram:
      '00': 2303
      '01': 2023
      '10': 3134
      '11': 2540
# Truncated here
```

As you can see, the output is rather verbose, but don't worry, we only describe it here for 
completeness, but you will rarely (probably never) have to inspect the file by yourself.

### (Optional) Getting status of asynchronous jobs

The whole point of running the asynchronous jobs is to be able to retrieve the results at a 
later point in time. But how do you know that the jobs you submitted to the backend have 
completed or not? You can of course, inspect the file manually and check e.g. IBMQ dashboard to 
see the statuses of the jobs. However, PyQBench provides a helper command that will fetch the 
statuses for you. The command is:

```shell
qbench disc-fourier status aysnc-results.yml
```
and it will display dictionary with histogram of statuses.

### Resolving asynchronous jobs
Before we can compute the discrimination probabilities, we have to obtain measurements from the 
submitted jobs. This is done using the following command:

```shell
qbench disc-fourier resolve async-results.yml resolved.yml
```

The resolved results, stored in `resolved.yml`, would look just like the experiment was run 
synchronously. In other words, at this step you should have a file containing measurement 
histograms, no matter if you run a synchronous or asynchronous experiment. We are ready to move 
on to computing probabilities.

## Computing probabilities

To construct a table with discrimination probabilities, you can use the following command

```shell
qbench disc-fourier tabulate resolved.yml results.csv 
```

The resulting csv will similarly to the one below:
```text
target,ancilla,phi,disc_prob,mit_disc_prob
0,1,0.0,0.5009,0.5009414225941422
0,1,0.3141592653589793,0.56505,0.5680439330543934
0,1,0.6283185307179586,0.62695,0.6327928870292887
0,1,0.9424777960769379,0.69045,0.6992154811715481
0,1,1.2566370614359172,0.76165,0.7736924686192469
0,1,1.5707963267948966,0.81305,0.8274581589958159
```

As you can see, it contains a single row for each tuple of `(target, ancilla, phi)`. The 
`disc_prob` column will contain the discrimination probability for given configuration. The 
`mit_disc_prob` column contains discrimination probability if Mthree mitigation was applied. 

:::{note}
The MThree mitigation requires knowledge of the stochastic matrix describing the measurement errors.
Currently, only the IBMQ backends provide this data, and other backends would require running 
calibration circuits to obtain the matrix. Hence, the `qbench` CLI performs mitigation only for 
IBMQ backends. If you wish to perform MThree mitigation with other backend, you need to use 
PyQBench as a library (see our {ref}`section/tutorial` to learn how to do this).
:::

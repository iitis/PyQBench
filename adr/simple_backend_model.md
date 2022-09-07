# Defining backend model for simple backends obtained from providers

## Deciders

- Paulina Lewandowska
- Konrad Jałowiecki

## Description

We want to define a pydantic model for backends obtainable from basic providrs.
Here, by basic we mean ones that can be created as an instance of some
importable type, without providing additional argument. e.g.:

```python
from qiskit_braket_provider.providers import AWSBraketProvider

provider = AWSBraketProvider()
backend = provider.get_backend("SV1")
```

## Outcome

### Yaml description

We decided that backend models should have the following form:

```yaml
provider: "fully.qualified.path:ProviderCls"
name: "backend_name"
run_options:
  run_option_1: some_value
  run_option_2: another_value
```

Here, `run_options` are optional keyword arguments to be passed to
`backend.run` method when executing circuits. The purpose of this property is 
mainly to allow for passing `verbatim` and `disable_qubit_rewiring` options
for Braket backends.

For the example code above, this would look like

```yaml
provider: "qiskit_braket_provider.providers:AWSBraketProvider"
name: "SV1"
```

Another example, for qiskit's `aer_simulator`:

```yaml
provider: "qiskit.providers.aer:AerProvider"
name: "aer_simulator"
```

As an example of backend with additional `run_options`, the below snippet 
shows definition for OQC Lucy device

```yaml
provider: "qiskit_braket_provider.providers:AWSBraketProvider"
name: "Lucy"
run_options:
  verbatim: true
```

### Pydantic models

The corresponding pydantic model should:

- validate that the provider specification is syntactically correct (i.e. it 
  is a correct fully qualified path followed by colon and correct class name)
- provide `create_backend` method returning the described backend.


## Rejected options

We rejected possibility of placing additional run options in separate model 
and passing them as separate file in CLI, as we feel that CLI would become 
more difficult to use.

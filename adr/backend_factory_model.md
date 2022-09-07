# Defining backend model for backends obtainable from factory

## Deciders

- Paulina Lewandowska
- Konrad Jałowiecki

## Description

While defining models for simple backends obtainable from provider, we 
noticed that not all relevant backends fit into this category, or even into 
category of backends obtainable from providers with some more work (e.g. IBMQ).
Some backends can be obtained by directly instantiating respective backend 
class directly, or calling some function. Practical example involves 
`BraketLocalBackend`, which cannot be obtained from `AWSBraketProvider`.

```python
from qiskit_braket_provider import BraketLocalBackend

backend = BraketLocalBackend(name="braket_dm")
```

Since at the client level there is very little difference between 
instantiating a class and calling a function, we will consider all backends 
created this way as created via call to some factory. 

We want to describe pydantic models for describing such backends in such a 
way, that it has `create_backend` method compatible with the previous 
backend description models. Hence, once the models are instantiated, they 
will be completely interchangeable.

## Outcome

### Yaml description

We decided that backend models that can be created via call to some factory, 
the yaml description of the following form should be sufficient:

```yaml
factory: "fully.qualified.path:factory_name"
args:
  - arg1
  - arg2
  - ...
kwargs:
  kw1: val1
  kw2: val2
run_options:
  run_option_1: some_value
  run_option_2: another_value
```

Here, `run_options` are optional keyword arguments to be passed to
`backend.run` method when executing circuits. The purpose of this property is 
mainly to allow for passing `verbatim` and `disable_qubit_rewiring` options
for Braket backends.

The `args` and `kwargs` arguments can be used to pass arbitrary arguments to 
the factory function, thus allowing for, in principle, arbitrary 
instantiation of backends. Both `args` and `kwargs` are optional.

Consider the previously discussed code creating `BraketLocalBackend`. The 
following yaml description should be sufficient to construct the same backend.

```yaml
factory: qiskit_braket_provider:BraketLocalBackend
kwargs:
  name: "braket_dm"
```


### Pydantic models

The corresponding pydantic model should:

- validate that the factory specification is syntactically correct (i.e. it 
  is a correct fully qualified path followed by colon and correct identifier)
- provide `create_backend` method returning the described backend.

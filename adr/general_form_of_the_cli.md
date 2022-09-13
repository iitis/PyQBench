# Defining general form of the CLI

## Deciders

- Paulina Lewandowska
- Konrad Jałowiecki

## Description

We need to decide the general form of the CLI for PyQbench. The goals we want it to meet:

- cover all present use cases: benchmarking and plotting results obtained from discrimination 
  experiment with parametrized Fourier family
- be extensible to future benchmarking schemes

## Outcome

We decided on the following look of the general command for PyQBench:

```text
qbench <experiment-type> <command> <inputs> <optional arguments>
```

For instance, the following could be a command for running Fourier-discrimination experiment

```shell
qbench disc-fourier benchmark experiment.yml backend.yml --output result.yml
```

Here:

- `disc-fourier` is an `<experiment-type>`
- `benchmark` is a `<command>`
- `experiment.yml` and `backend.yml` are positional (mandatory) `<inputs> for the `benchmark 
  command`
- `--output result.yml` is an `<optional argument>` 

The proposed form of the CLI achieves our needs because:

- it covers present use cases (e.g. `disc-fourier benchmark` and `disc-fourier plot`)
- it does not block us from adding new benchmarking schemes (e.g. `qbench new-scheme benchmark`)


## Rejected ideas

1. Passing commands before the experiment type. 

    ```shell
    qbench benchmark disc-fourier experiment.yml backend.yml --output result.yml
    qbench plot disc-fourier result.yml --output plots.pdf
    ```

   We rejected this one because future experiment types may not have the same set of operations 
   as Fourier-discrimination. For instance, some experiments my not produce plots, in which 
   case the following command would make no sense:

   ```shell
   qbench plot stome-other-scheme experiment.yml backend.yml --output plots.pdf
   ```

2. Creating separate command for each experiment type, e.g.:

    ```shell
    qbench-fourier-disc benchmark experiment.yml backend.yml --output result.yml
    qbench-fourier-disc plot result.yml --output plots.pdf
    ```
   
    We decided that this form of the commands is clunky.

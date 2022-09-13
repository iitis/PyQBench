# Defining CLI for Fourier discrimination experiments

## Deciders

- Paulina Lewandowska
- Konrad Jałowiecki

## Description

This ADR describes the form of the CLI of the Fourier discrimination experiment. Note that we 
are not concerned about other possible discrimination experiments for now. The suggested CLI has 
to conform to the requirements describe in the ADR about general CLI from. 

## Outcome

We decided that the CLI should support commands for:

- running the benchmarks
- plotting the results

We split the commands (instead of plotting the results right after the benchmark) for better 
modularity and quicker implementation. Also, the same results may be plotted with different 
aesthetics, so the splitting seems to be justified.

The precise form of the commands would be:

```shell
qbench disc-fourier benchmark experiment.yml backend.yml --output result.yml
qbench disc-fourier plot result.yml --output plots.pdf
```

Note that later we might wish to extend the plotting command with additional arguments 
controlling aesthetics, but this will be presented, if necessary, in another ADR.

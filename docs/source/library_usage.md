# Usage as a library

This guide introduces basic concepts needed for using PyQBench as a library from a Python
script. In particular, we will cover the following topics:

- Defining experiment using circuit components.
- Assembling circuits needed for given benchmarking scheme.
- Running experiment on simulator or hardware.
- Obtaining discrimination probability from the measurements.
- Visualising results.

## Setting the stage

Before we start, make sure you installed PyQBench (see installation for detailed instruction).
Optionally, you might want to install matplotlib library for plotting the final results.

In this guide we won't repeat mathematical foundations needed for understanding measurement
discrimination experiments. We'll only restrict ourselves to the details necessary for running 
experiments using PyQBench. However, we encourage you to check out Mathematical Foundations to
get a better grasp of the entities and concepts discussed here.

## Defining experiment using circuit components.

On the conceptual level, every discrimination experiment performed in PyQBench needs the following:

- Unitary $U^\dagger$ defining alternative measurement to be discriminated from the measurement
  in Z-basis.
- Discriminator, i.e. optimal initial state for the circuit.
- $V_0^\dagger$ and $V_1^\dagger$, positive and negative parts of optimal 
  measurement from Holevo-Helstrom theorem.

Currently available quantum computers typically cannot start execution from an arbitrary state. 
Instead, we have to prepare it ourselves. Hence, to execute experiment using postselection 
scheme, we need the following operations implemented as Qiskit Instructions:

- An instruction taking $|00\rangle$ to the desired discriminator.
- Instructions implementing $U^\dagger$, $V_0^\dagger$ and $V_1^\dagger$.

Task of implementing needed instruction is trivial when we know the decomposition of our 
unitaries into sequences of gates. If we only know unitary matrices, we can either decompose 
them by hand, or try using one of the available transpilers.

For the direct-sum experiment we don't use $V_0^\dagger$ and $V_1^\dagger$ separately. Instead, 
we need a two-qubit gate $V_0^\dagger \oplus V_1^\dagger$.


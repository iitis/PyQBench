# Usage as a library

This guide introduces basic concepts needed for using PyQBench as a library from a Python
script. In particular, we will cover the following topics:

- Defining experiment using circuit components.
- Assembling circuits needed for given benchmarking scheme.
- Running experiment on simulator or hardware.
- Obtaining discrimination probability from the measurements.
- Visualising results.

## Setting the stage

Before we start, make sure you installed PyQBench (see installation for 
detailed instructions).
Optionally, you might want to install matplotlib library for plotting the final results.

In this guide we won't repeat mathematical foundations needed for understanding measurement
discrimination experiments. We'll only restrict ourselves to the details necessary for running 
experiments using PyQBench. However, we encourage you to check out Mathematical Foundations to
get a better grasp of the entities and concepts discussed here.

## What do we need?

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
unitaries into sequences of gates. If we only know the unitary matrices, we can either decompose 
them by hand, or try using one of the available transpilers.

For the direct-sum experiment we don't use $V_0^\dagger$ and $V_1^\dagger$ separately. Instead, 
we need a two-qubit gate $V_0^\dagger \oplus V_1^\dagger$.

## Our toy model

In our example, we will use $U = H$ (the Hadamard gate). To keep us focused on the implementation
in PyQBench and not delve too deep into mathematical explanation, we simply provide explicit 
formulas for discriminator $|\Psi_0\rangle$ and $V_0$ and $V_1$, leaving the 
calculations to the interested reader.

The explicit formula for discriminator in our toy model reads:

$$
| \Psi_0 \rangle = \frac{1}{\sqrt{2}} (| 00 \rangle + | 11 \rangle),
$$ 

with corresponding parts of optimal measurement being equal to 

$$
V_0 = \begin{bmatrix}
\alpha & -\beta \\
\beta & \alpha
\end{bmatrix}
$$

$$
V_1 = \begin{bmatrix}
-\beta & \alpha \\
\alpha & \beta
\end{bmatrix}
$$

where

$$
\alpha = \frac{\sqrt{2 - \sqrt{2}}}{2} = \cos\left(\frac{3}{8}\pi\right)
$$

$$
\beta = \frac{\sqrt{2 + \sqrt{2}}}{2} = \sin\left(\frac{3}{8}\pi\right)
$$

For completeness, here's how the direct sum $V_0 \oplus V_1$ looks like

$$
V_0 \oplus V_1  = \begin{bmatrix}
V_0 & 0 \\
0 & V_1
\end{bmatrix} = \begin{bmatrix}
\alpha & -\beta & 0 & 0 \\
\beta & \alpha & 0 & 0 \\
0 & 0 & -\beta & \alpha \\
0 & 0 & \alpha & \beta
\end{bmatrix}
$$

As a next step, we need decompose our matrices into actual sequences of gates.

## Decomposing circuit components into gates

We are lucky, because our discriminator is just a Bell state. Thus, the circuit taking 
$|00\rangle$ to $|\Phi_0 \rangle$ is well known, and comprises  Hadamard gate 
followed by CNOT gate on both qubits.

< PLACEHOLDER FOR CIRCUIT >

For $V_0$ and $V_1$ observe that $V_0 = \operatorname{RY} \left( \frac{3}{4} \pi \right)$, where 
$\operatorname{RY}$ is just standard rotation around the $Y$ axis

$$
\operatorname{RY}(\theta) = \begin{bmatrix}
\cos \frac{\theta}{2} & -\sin \frac{\theta}{2} \\
\sin \frac{\theta}{2} & \cos \frac{\theta}{2}
\end{bmatrix}
$$

To obtain $V_1$, we need only to swap the columns, which is equivalent to following $V_0$ by $X$ 
matrix. Finally, remembering that we need to take Hermitian conjugates for our actual circuits,
we obtain the following decompositions

$$
V_0^\dagger = \operatorname{RY} \left( \frac{3}{4} \pi \right)^\dagger = \operatorname{RY} \left
( -\frac{3}{4} \pi \right)
$$

$$
V_1^\dagger = \left(\operatorname{RY} \left( \frac{3}{4} \pi \right) \cdot X\right)^\dagger = 
X \cdot \operatorname{RY} \left ( -\frac{3}{4} \pi \right)
$$

Recall that to perform an experiment using postselection scheme we need four circuits. One of them 
(realizing $(U, V_0)$ alternative) looks like this.

![Circuit implementing U^dagger, V_0 alternative](img/hadamard_u_v0.svg){#imgattr width="70%"}

Other circuits can be created analogously by using identity instead of $U$ and/or $V_1^\dagger$ 
instead of $V_0^\dagger$. However, you don't need to memorize how the circuits look like, because
qbench will construct them for you.

## Defining needed instructions using Qiskit

We will start our code with the needed imports. Aside standard stuff like 
numpy, we need to be able to define quantum circuits and a simulator to run 
them.

```{literalinclude} examples/example_01_hadamard.py
:start-after: "# External imports"
:end-before: "# ---"
```


Next we import needed functions from PyQBench. For our first example we'll 
need two functions.
```{literalinclude} examples/example_01_hadamard.py
:start-after: "# PyQBench imports"
:end-before: "# ---"
```

The first one, `benchmark_using_postselection` performs 
the whole benchmarking process using postselection scheme. In particular, it 
assembles the needed circuits, runs them using specified backend and 
interprets measurement histograms in terms of discrimination probability. 
Similarly, the `benchmark_using_direct_sum` does the same but with "direct 
sum" scheme.

To run any of these functions, we need to define components that we 
discussed in previous sections. Its perhaps best to do this by defining 
separate function for each component. The important thing to remember is 
that we need to create Qiskit instructions, not circuits. We can 
conveniently do so by constructing circuit acting on qubits 0 and 1 and then 
converting them using `to_instruction()` method.

```{literalinclude} examples/example_01_hadamard.py
:start-after: "# Components definitions"
:end-before: "# ---"
```

:::{note}
You may wonder why we only define circuits on qubits 0 and 1, when we might 
want to run the benchmarks for other qubits as well? It turns out that it 
doesn't matter. In Qiskit, circuit converted to Instruction behaves just 
like a gate. During the assembly stage, PyQBench will use those 
instructions on correct qubits.
:::

Lastly, before launching our simulations, we need to construct simulator 
they will run on. For the purpose of this example, we'll start with basic 
[Qiskit Aer simulator](https://github.com/Qiskit/qiskit-aer).

```{literalinclude} examples/example_01_hadamard.py
:start-after: "# Obtaining Aer Simulator"
:end-before: "# ---"
```

Now running the simulation is as simple as invoking functions imported from 
`qbench` package.

```{literalinclude} examples/example_01_hadamard.py
:start-after: "# Running postselection"
:end-before: "# ---"
```
```{literalinclude} examples/example_01_hadamard.py
:start-after: "# Running direct_sum"
:end-before: "# ---"
```

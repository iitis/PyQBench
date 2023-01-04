(section/math)=

# How it works

## Motivation

Suppose we have access to a device performing one of the predefined von Neumann
measurements[^whatwediscriminate], $\PP$ or $\QQ$. While the $\PP$ and $\QQ$ are known, it is not
known which of them is performed when the device executes. Based on the measurement outcome,
you have to guess which measurement was performed (but you can perform arbitrary unitary
operations before and after the measurement). What is the highest probability of making a
correct guess? And what do you have to do to achieve it? And, most importantly, why would we
want to do this?

Suppose that you know a strategy that, for an ideal device, would yield a probability
$p_{\text{succ}}$ of successfully discriminating between two measurements. Will the probability be
the same on an actual physical device? For current, Noisy Intermediate Scale Quantum devices
(NISQs), the answer is: certainly not. However, the error rate that you make when guessing can be
used as a benchmarking metric. PyQBench helps you in organizing such discrimination experiments for
a single qubit system[^optimal], executing them on real hardware or simulators, and
computing discrimination probabilities based on the measured bitstrings.

## Notation and some preliminaries

Recall that a general quantum
measurement, that is a positive operator valued measure (POVM) $\PP$ is a
collection of positive semidefinite operators $\{E_1, \ldots, E_m \}$ called
*effects*, which sum up to identity, i.e. $ \, \, \sum_{i=1}^m E_i = \Id$.
In PyQBench, we are interested only in von Neumann measurements, i.e. measurements
for which all the effects are rank-one projectors. Every such measurement can be
parameterized by a unitary matrix $U$ which the effects $\{\proj{u_0}, \ldots, \proj{u_{d-1}}\}$,
are created by taking $\ket{u_i}$ as $i+1$-th column of the unitary matrix $U$.
We will denote von Neumann measurements described by the matrix $U$ by $\PP_{U}$.

Typically, NISQ devices can only perform measurements in computational $Z$-basis.
To perform an arbitrary von Neumann measurement $\PP_{U}$, one has to first apply $U^\dagger$
to the measured system and then follow with $Z$-basis measurement. Hence, the following two
circuits are equivalent.

:::{figure-md} fig-von-neumann

![Implementation of von Neumann measurement](img/vonneumann.svg){#imgattr width="70%" align="center"}

Implementation of von Neumann measurement.
:::

Note that the decomposition above is basically a change of basis in which the measurement
is performed.

## Discrimination scheme

Without loss of generality, we consider discrimination between a measurement in the computational
Z-basis ($\PP_\Id$), and an alternative measurement performed in the basis $U$
($\PP_U$)[^zbasis]. In PyQBench, we operate only on two-level systems, but the discrimination scheme,
described in detail in {cite:p}`puchala2018strategies`, makes no assumptions about the 
dimensionality.

In general, the discrimination scheme, presented in {numref}`fig-theoretical-scheme`,
requires a
second system of the same dimensionality as the measured one. First, the joint system is prepared in
some state $\ket{\psi_0}$. Then, the unknown measurement is performed on the first part of the
system. Based on its outcome $i$, another measurement $\mathcal{P}_{V_i}$ is performed to obtain an
outcome $j$. Finally, if $j=0$ we guess that the performed measurement is $\mathcal{P}_U$, otherwise
we guess that it was $\mathcal{P}_\Id$.

:::{figure-md} fig-theoretical-scheme

![Theoretical scheme of discrimination between von Neumann measurements](img/theoretical_scheme.svg){width="70%" align="center"}

Theoretical scheme of discrimination between von Neumann measurements $\PP_{U}$ and 
$\PP_\Id$. 
:::

## Limitations of NISQ devices and practical considerations

Current NISQ devices are unable to perform conditional measurements, which is the biggest
obstacle to implementing our scheme on real hardware. Luckily, we can overcome it by
cleverly adjusting our scheme so that it only uses components available on current devices.
We have two possible choices here: using a postselection or a direct sum
$V_0^\dagger\oplus V_1^\dagger$.

### Scheme 1: using postselection

The first idea is very simple. Instead of performing a conditional measurement, for each
measurement $\PP_U, \PP_\Id$ to be discriminated and each choice of $k \in \{0, 1\}$ we run 
circuit presented in {numref}`fig-postselection`.

:::{figure-md} fig-postselection

![postselection-scheme](img/postselection_no_channels.svg){width="70%" align=center}

Postselection scheme of discrimination between von Neumann measurements $\PP_{U}$ and $\PP_\Id$.
:::

But now our experiment does not match the previously described scheme, right?
Yes, unless we discard all the outcomes for which $i\ne k$ (hence the name \emph{postselection},
we are selecting valid outcomes after the experiment is performed).

More precisely, our experiments can be grouped into classes identified by tuples of the form
$(\mathcal{Q}, k, i, j)$, where $\mathcal{Q} \in \{\PP_U, \PP_\Id\}$ denotes the chosen measurement.
We discard all the experiments for which $k \ne i$. Hence, the total number of valid experiments is

\begin{eqnarray}
	N_\text{total} = \#\{(\QQ, k, i, j): k = i \}
\end{eqnarray}

We now need to count the experiments (among the valid ones) resulting in successful discrimination.
If we have chosen $\PP_U$, then we guess correctly iff $j=0$. Similarly, for
$P_\Id$, we guess correctly iff $j=1$. If we define

\begin{eqnarray}
	N_{\PP_U} &= \#\{(\mathcal{Q}, k, i, j): \mathcal{Q} = \PP_U, k = i, j = 0\}, \\
	N_{\PP_\Id} &= \#\{(\mathcal{Q}, k, i, j): \mathcal{Q} = \PP_\Id, k = i, j = 1\},
\end{eqnarray}

then the empirical success probability can be computed as

\begin{equation}
p_{\text{succ}}(\PP_{U}, \PP_{\Id}) = \frac{N_{\PP_U} + N_{\PP_\Id}}{N_{\text{total}}}.
\end{equation}

### Scheme 2: By using direct sum of $V_0^\dagger \oplus V_1^\dagger$

1. We prepare the discriminator $\ket{\psi_{0}}$ on bipartite
system.
2. We apply one of unitary,   either $U^\dagger$ or
$\Id$, on the first system.
3. We apply direct sum $V_0^\dagger \oplus V_1^\dagger$ on the whole systems.
4. We measure both systems in computational basis $\Delta$.
5. We make a decision based on the received label $j$ on the second system. If $j=0$, then we
decide that $\PP_U$ occurs. Otherwise, we decide that $\PP_{\Id}$ occurs.

The schematic representation of this setup is depicted in {numref}`fig-direct-sum`.

:::{figure-md} fig-direct-sum

![Direct sum scheme](img/direct_sum.svg){width="70%" align=center}

A schematic representation of the setup for distinguishing  measurements using controlled 
unitary gate.
:::

In this scheme, the experiment can be characterized by a pair $(\mathcal{Q}, i,j)$, where 
$\mathcal{Q} = \{ \PP_{U}, \PP_{\Id} \}$. The number of successful trials for $U$ and $\Id$, 
respectively, can be written as

\begin{eqnarray}
N_{\PP_U} &= \#\{(\mathcal{Q},  i, j): \mathcal{Q} = \PP_U, j = 0\}, \\
N_{\PP_\Id} &= \#\{(\mathcal{Q},  i, j): \mathcal{Q} = \PP_\Id, j = 1\}.
\end{eqnarray}

Then, the probability of correct discrimination between $\PP_{U} $ and $\PP_\Id$ is given by
\begin{equation}
p_{\text{succ}} = \frac{N_{\PP_{U}} + N_{\PP_{\Id}}}{N_{\text{total}}},
\end{equation}
where $N_{\text{total}}$ is the number of trials.


[^whatwediscriminate]: In PyQBench, we restrict ourselves to discriminating von Neumann
measurements. This is because, unlike other measurement types, they can be implemented on actual
hardware.
[^optimal]: As we will soon see, the optimal discrimination strategy requires the usage of an
additional auxiliary qubit.
[^zbasis]: Explaining why we can consider only Z-basis and alternative  measurement is beyond
the scope of this technical documentation. See {cite:p}`puchala2018strategies` if you are 
interested in  the explanation.

## References

```{bibliography}
```

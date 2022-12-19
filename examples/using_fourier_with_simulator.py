import numpy as np
from matplotlib import pyplot as plt
from qiskit_braket_provider import BraketLocalBackend

from qbench.fourier import discrimination_probability_upper_bound
from qbench.fourier._components import FourierComponents
from qbench.schemes.direct_sum import benchmark_using_direct_sum

NUM_SHOTS_PER_MEASUREMENT = 10000
TARGET = 0
ANCILLA = 1
GATESET = "ibmq"


def main():
    backend = BraketLocalBackend()
    phis = np.linspace(0, 2 * np.pi, 100)

    theoretical_probs = discrimination_probability_upper_bound(phis)

    actual_probs = [
        benchmark_using_direct_sum(
            backend=backend,
            target=TARGET,
            ancilla=ANCILLA,
            state_preparation=circuits.state_preparation,
            u_dag=circuits.u_dag,
            v0_v1_direct_sum_dag=circuits.v0_v1_direct_sum_dag,
            num_shots_per_measurement=NUM_SHOTS_PER_MEASUREMENT,
        )
        for circuits in (FourierComponents(phi, gateset=GATESET) for phi in phis)
    ]

    fig, ax = plt.subplots()
    ax.plot(phis, theoretical_probs, color="red", label="theoretical_predictions")
    ax.plot(phis, actual_probs, color="blue", label="actual data")
    ax.legend()

    plt.show()


if __name__ == "__main__":
    main()

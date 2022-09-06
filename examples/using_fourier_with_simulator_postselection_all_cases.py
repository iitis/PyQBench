import numpy as np
from matplotlib import pyplot as plt
from qiskit_braket_provider import BraketLocalBackend

from qbench.fourier import FourierComponents, discrimination_probability_upper_bound
from qbench.postselection_all_cases import benchmark_using_postselection_all_cases

NUM_SHOTS_PER_MEASUREMENT = 1000
TARGET = 0
ANCILLA = 1
GATESET = "rigetti"


def main():
    backend = BraketLocalBackend()
    phis = np.linspace(0, 2 * np.pi, 100)

    theoretical_probs = discrimination_probability_upper_bound(phis)

    actual_probs = [
        benchmark_using_postselection_all_cases(
            backend=backend,
            target=TARGET,
            ancilla=ANCILLA,
            state_preparation=circuits.state_preparation,
            black_box_dag=circuits.black_box_dag,
            v0_dag=circuits.v0_dag,
            v1_dag=circuits.v1_dag,
            num_shots_per_measurement=NUM_SHOTS_PER_MEASUREMENT,
        )
        for circuits in (FourierComponents(phi, gateset=GATESET) for phi in phis)
    ]

    fig, ax = plt.subplots()
    ax.plot(phis, theoretical_probs, color="red", label="theoretical_predictions")
    ax.plot(phis, actual_probs, color="blue", label="actual results")
    ax.legend()

    plt.show()


if __name__ == "__main__":
    main()

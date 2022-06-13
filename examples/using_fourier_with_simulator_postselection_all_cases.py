import numpy as np
from braket import devices
from matplotlib import pyplot as plt

from qbench import fourier
from qbench.postselection_all_cases import benchmark_using_postselection_all_cases

NUM_SHOTS_PER_MEASUREMENT = 10000
TARGET = 0
ANCILLA = 1
NATIVE_ONLY = True


def main():
    device = devices.LocalSimulator(backend="braket_dm")
    phis = np.linspace(0, 2 * np.pi, 100)

    theoretical_probs = fourier.discrimination_probability_upper_bound(phis)

    actual_probs = [
        benchmark_using_postselection_all_cases(
            device=device,
            target=TARGET,
            ancilla=ANCILLA,
            state_preparation=fourier.state_preparation,
            basis_change=fourier.unitary_to_discriminate(phi),
            v0=fourier.v0_dag(phi, native_only=NATIVE_ONLY),
            v1=fourier.v1_dag(phi, native_only=NATIVE_ONLY),
            num_shots_per_measurement=NUM_SHOTS_PER_MEASUREMENT,
        )
        for phi in phis
    ]

    fig, ax = plt.subplots()
    ax.plot(phis, theoretical_probs, color="red", label="theoretical_predictions")
    ax.plot(phis, actual_probs, color="blue", label="actual results")
    ax.legend()

    plt.show()


if __name__ == "__main__":
    main()

import numpy as np
from braket import devices
from matplotlib import pyplot as plt

from qbench.fourier import FourierCircuits, discrimination_probability_upper_bound
from qbench.postselection import benchmark_using_postselection

NUM_SHOTS_PER_MEASUREMENT = 10000
TARGET = 0
ANCILLA = 1
NATIVE_ONLY = True


def main():
    device = devices.LocalSimulator(backend="braket_dm")
    phis = np.linspace(0, 2 * np.pi, 100)

    theoretical_probs = discrimination_probability_upper_bound(phis)

    actual_probs = [
        benchmark_using_postselection(
            device=device,
            target=TARGET,
            ancilla=ANCILLA,
            state_preparation=circuits.state_preparation,
            basis_change=circuits.unitary_to_discriminate,
            v0=circuits.v0_dag,
            v1=circuits.v1_dag,
            num_shots_per_measurement=NUM_SHOTS_PER_MEASUREMENT,
        )
        for circuits in (FourierCircuits(phi, native_only=NATIVE_ONLY) for phi in phis)
    ]

    fig, ax = plt.subplots()
    ax.plot(phis, theoretical_probs, color="red", label="theoretical_predictions")
    ax.plot(phis, actual_probs, color="blue", label="actual results")
    ax.legend()

    plt.show()


if __name__ == "__main__":
    main()

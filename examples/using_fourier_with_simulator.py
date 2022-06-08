import numpy as np
from braket import devices
from matplotlib import pyplot as plt

from qbench import fourier
from qbench.direct import benchmark_using_controlled_unitary

NUM_SHOTS_PER_MEASUREMENT = 1000
TARGET = 0
ANCILLA = 1
NATIVE_ONLY = True


def main():
    device = devices.LocalSimulator(backend="braket_dm")
    phis = np.linspace(0, 2 * np.pi, 100)

    p = benchmark_using_controlled_unitary(
        device=device,
        target=TARGET,
        ancilla=ANCILLA,
        state_preparation=fourier.state_preparation,
        basis_change=fourier.unitary_to_discriminate(np.pi / 2),
        controlled_unitary=fourier.controlled_v0_v1_dag(np.pi / 2, native_only=NATIVE_ONLY),
        num_shots_per_measurement=NUM_SHOTS_PER_MEASUREMENT,
    )

    theoretical_probs = fourier.discrimination_probability_upper_bound(phis)

    actual_probs = [
        benchmark_using_controlled_unitary(
            device=device,
            target=TARGET,
            ancilla=ANCILLA,
            state_preparation=fourier.state_preparation,
            basis_change=fourier.unitary_to_discriminate(phi),
            controlled_unitary=fourier.controlled_v0_v1_dag(phi, native_only=NATIVE_ONLY),
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

import pytest
from qiskit import QiskitError, QuantumCircuit
from qiskit.providers import JobStatus

from qbench.testing import MockProvider


def test_two_independently_obtained_mock_simulators_share_job_cache():
    circuit = QuantumCircuit(1)
    circuit.h(0)
    circuit.measure_all()

    provider1 = MockProvider()
    backend1 = provider1.get_backend("mock-backend")

    provider2 = MockProvider()
    backend2 = provider2.get_backend("mock-backend")

    job = backend1.run(circuit, shots=10)
    assert backend2.retrieve_job(job.job_id()) == job


def test_mock_simulator_properly_fails_selected_jobs():
    circuit = QuantumCircuit(1)
    circuit.x(0)
    circuit.measure_all()

    provider = MockProvider()
    provider.reset_caches()

    backend = provider.get_backend("failing-mock-backend")

    jobs = [backend.run(circuit, shots=10) for _ in range(4)]

    for job in jobs:
        job.wait_for_final_state()

    for i in (0, 3):
        assert jobs[i].status() == JobStatus.DONE
        assert sum(jobs[i].result().get_counts().values()) == 10

    for i in (1, 2):
        assert jobs[i].status() == JobStatus.ERROR
        with pytest.raises(QiskitError):
            jobs[i].result()

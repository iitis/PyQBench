from qiskit import QuantumCircuit

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

from pathlib import Path

import yaml

p_direct = Path("experiments/fourier-disc-direct-sum.yml")
p_post = Path("experiments/fourier-disc-postselection.yml")

with open(p_direct, "r") as stream:
    direct = yaml.safe_load(stream)

with open(p_post, "r") as stream:
    post = yaml.safe_load(stream)

for i in range(2, 127, 2):
    direct["qubits"].append({"target": i, "ancilla": i + 1})
    post["qubits"].append({"target": i, "ancilla": i + 1})

    with open(p_direct, "w") as stream:
        yaml.dump(direct, stream)

    with open(p_post, "w") as stream:
        yaml.dump(post, stream)

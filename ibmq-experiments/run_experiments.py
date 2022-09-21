import subprocess
from pathlib import Path

# curr_p_post = p_post.with_stem(f"{p_post.stem[:-4]}-{i}-{i+1}")
for experiment in Path().glob("experiments/*.yml"):
    for backend in Path().glob("backends/*.yml"):
        output_folder = Path("results") / backend.stem
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = output_folder / experiment.name

        subprocess.run(
            [
                "qbench",
                "disc-fourier",
                "benchmark",
                f"{experiment}",
                f"{backend}",
                "--output",
                f"{output_file}",
            ]
        )

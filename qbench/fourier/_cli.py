from argparse import FileType

from yaml import safe_dump, safe_load

from ..common_models import BackendDescriptionRoot
from ._experiment import _fetch_statuses, run_experiment
from ._models import FourierDiscriminationExperiment, FourierDiscriminationResult


def _run_benchmark(args):
    experiment = FourierDiscriminationExperiment(**safe_load(args.experiment_file))
    backend_description = BackendDescriptionRoot(__root__=safe_load(args.backend_file)).__root__

    result = run_experiment(experiment, backend_description)
    safe_dump(result.dict(), args.output, sort_keys=False)


def _status(args):
    results = FourierDiscriminationResult(**safe_load(args.async_results))
    counts = _fetch_statuses(results)
    print(counts)


def add_fourier_parser(parent_parser):
    parser = parent_parser.add_parser("disc-fourier")

    subcommands = parser.add_subparsers()

    benchmark = subcommands.add_parser(
        "benchmark",
        description=(
            "Run benchmarking experiment utilizing measurement discrimination "
            "with parametrized Fourier family of measurements."
        ),
    )

    benchmark.add_argument(
        "experiment_file", help="path to the file describing the experiment", type=FileType("r")
    )
    benchmark.add_argument(
        "backend_file",
        help="path to the file describing the backend to be used",
        type=FileType("r"),
    )

    benchmark.add_argument(
        "--output",
        help="optional path to the output file. If not provided, output will be printed to stdout",
        type=FileType("w"),
        default="-",
    )

    benchmark.set_defaults(func=_run_benchmark)

    plot = subcommands.add_parser("plot")

    plot.add_argument(
        "result",
        help=(
            "result of discrimination experiment which can be obtained by running "
            "qbench benchmark"
        ),
        type=str,
    )

    plot.add_argument(
        "--output",
        help=(
            "optional path to the output file. If not provided, the plots will be shown "
            "but not saved. The extension of the output file determines the output format "
            "and it can be any of the ones supported by the matplotlib"
        ),
        type=str,
    )

    resolve = subcommands.add_parser(
        "resolve",
        description=(
            "Resolve asynchronous results into final histograms by querying remote jobs "
            "specified in the results file."
        ),
    )

    resolve.add_argument(
        "async_result",
        help=(
            "path to the file with results of discrimination experiment which can be obtained by "
            "running qbench benchmark using backend with asynchronous flag equal to True."
        ),
        type=str,
    )

    resolve.add_argument(
        "output",
        help=(
            "path to the file where synchronous results resolved from the asynchronous one should "
            "be saved."
        ),
    )

    status = subcommands.add_parser(
        "status", description="Query the status of an asynchronous jobs from the results file."
    )

    status.add_argument(
        "async_results",
        help=(
            "path to the file with results of discrimination experiment which can be obtained by "
            "running qbench benchmark using backend with asynchronous flag equal to True."
        ),
        type=FileType("r"),
    )

    status.set_defaults(func=_status)

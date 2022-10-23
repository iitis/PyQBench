"""Definition of command line parsers and handlers for qbench disc-fourier command."""
from argparse import FileType

from yaml import safe_dump, safe_load

from ..common_models import BackendDescriptionRoot
from ._experiment_runner import (
    fetch_statuses,
    resolve_results,
    run_experiment,
    tabulate_results,
)
from ._models import (
    FourierDiscriminationAsyncResult,
    FourierDiscriminationExperiment,
    FourierDiscriminationSyncResult,
)


def _run_benchmark(args):
    """Function executed when qbench disc-fourier benchmark is invoked."""
    experiment = FourierDiscriminationExperiment(**safe_load(args.experiment_file))
    backend_description = BackendDescriptionRoot(__root__=safe_load(args.backend_file)).__root__

    result = run_experiment(experiment, backend_description)
    safe_dump(result.dict(), args.output, sort_keys=False, default_flow_style=None)


def _status(args):
    """Function executed when qbench disc-fourier status is invoked."""
    results = FourierDiscriminationAsyncResult(**safe_load(args.async_results))
    counts = fetch_statuses(results)
    print(counts)


def _resolve(args):
    """Function executed when qbench disc-fourier resolve is invoked."""
    results = FourierDiscriminationAsyncResult(**safe_load(args.async_results))
    resolved = resolve_results(results)
    safe_dump(resolved.dict(), args.output, sort_keys=False)


def _tabulate(args):
    """Function executed when qbench disc-fourier tabulate is invoked."""
    results = FourierDiscriminationSyncResult(**safe_load(args.sync_results))
    table = tabulate_results(results)
    table.to_csv(args.output, index=False)


def add_fourier_parser(parent_parser) -> None:
    """Add disc-fourier parser to the parent parser.

    The added parser will have the following subcommands:
    - benchmark: run fourier discrimination experiment against given backend
    - status: check status of asynchronously executed experiment
    - resolve: retrieve data of completed asynchronous job

    The exact syntax for using each command can be, as usually, obtained by running
    qbench disc-fourier <command> -h

    :param parent_parser: a parser to which disc-fourier command should be added.
    """
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
            "Resolve asynchronous data into final histograms by querying remote jobs "
            "specified in the data file."
        ),
    )

    resolve.add_argument(
        "async_results",
        help=(
            "path to the file with data of discrimination experiment which can be obtained by "
            "running qbench benchmark using backend with asynchronous flag equal to True."
        ),
        type=FileType("r"),
    )

    resolve.add_argument(
        "output",
        help=(
            "path to the file where synchronous data resolved from the asynchronous one should "
            "be saved."
        ),
        type=FileType("w"),
    )

    resolve.set_defaults(func=_resolve)

    status = subcommands.add_parser(
        "status", description="Query the status of an asynchronous jobs from the data file."
    )

    status.add_argument(
        "async_results",
        help=(
            "path to the file with data of discrimination experiment which can be obtained by "
            "running qbench benchmark using backend with asynchronous flag equal to True."
        ),
        type=FileType("r"),
    )

    status.set_defaults(func=_status)

    tabulate = subcommands.add_parser(
        "tabulate",
        description=(
            "Compute and tabulate probabilities from measurements obtained from the experiment."
        ),
    )

    tabulate.add_argument(
        "sync_results",
        help=(
            "path to the file with data of discrimination experiment. If the experiment was "
            "conducted using asynchronous backend, they need to be manually resolved."
        ),
        type=FileType("r"),
    )

    tabulate.add_argument(
        "output",
        help=(
            "path to the resulting CSV file. This file will contain columns 'target', 'ancilla' "
            "'phi' and 'disc_prob' with obvious meanings. If, in addition, experiment contained "
            "mitigation data, the 'mitigated_disc_prob` containing discrimination probabilities "
            "computed using mitigated bitstrings will also be added."
        ),
        type=FileType("w"),
    )

    tabulate.set_defaults(func=_tabulate)

"""Definition of command line parsers and handlers for qbench disc-fourier command.

This module also contains thin wrappers for functions from qbench.fourier.experiment_runner,
to adapt them for command line usage.
"""
from argparse import FileType, Namespace

from yaml import safe_dump, safe_load

from ..common_models import BackendDescriptionRoot
from ._models import (
    FourierDiscriminationAsyncResult,
    FourierDiscriminationSyncResult,
    FourierExperimentSet,
)
from .experiment_runner import (
    fetch_statuses,
    resolve_results,
    run_experiment,
    tabulate_results,
)


def _run_benchmark(args: Namespace) -> None:
    """Function executed when qbench disc-fourier benchmark is invoked."""
    experiment = FourierExperimentSet(**safe_load(args.experiment_file))
    backend_description = BackendDescriptionRoot(__root__=safe_load(args.backend_file)).__root__

    result = run_experiment(experiment, backend_description)
    safe_dump(result.dict(), args.output, sort_keys=False, default_flow_style=None)


def _status(args: Namespace) -> None:
    """Function executed when qbench disc-fourier status is invoked."""
    results = FourierDiscriminationAsyncResult(**safe_load(args.async_results))
    counts = fetch_statuses(results)
    print(counts)


def _resolve(args: Namespace) -> None:
    """Function executed when qbench disc-fourier resolve is invoked."""
    results = FourierDiscriminationAsyncResult(**safe_load(args.async_results))
    resolved = resolve_results(results)
    safe_dump(resolved.dict(), args.output, sort_keys=False)


def _tabulate(args: Namespace) -> None:
    """Function executed when qbench disc-fourier tabulate is invoked."""
    results = FourierDiscriminationSyncResult(**safe_load(args.sync_results))
    table = tabulate_results(results)
    table.to_csv(args.output, index=False)


def add_fourier_parser(parent_parser) -> None:
    """Add disc-fourier parser to the parent parser.

    The added parser will have the following subcommands:
    - benchmark: run set of Fourier discrimination experiments against given backend
    - status: check status of asynchronously executed set of experiments
    - resolve: retrieve results of completed asynchronous job

    The exact syntax for using each command can be, as usually, obtained by running
    qbench disc-fourier <command> -h

    :param parent_parser: a parser to which disc-fourier command should be added.
    """
    parser = parent_parser.add_parser("disc-fourier")

    subcommands = parser.add_subparsers()

    benchmark = subcommands.add_parser(
        "benchmark",
        description=(
            "Run set of benchmarking experiments utilizing measurement discrimination "
            "with parametrized Fourier family of measurements."
        ),
    )

    benchmark.add_argument(
        "experiment_file",
        help="path to the file describing the set of experiments",
        type=FileType("r"),
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
            "result of discrimination experiments which can be obtained by running "
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
        description="Resolve asynchronous jobs to obtain final experiments data.",
    )

    resolve.add_argument(
        "async_results",
        help=(
            "path to the file with data of discrimination experiments which can be obtained by "
            "running `qbench` benchmark using backend with asynchronous flag equal to True."
        ),
        type=FileType("r"),
    )

    resolve.add_argument(
        "output",
        help="path to the file where data resolved from asynchronous jobs should be stored.",
        type=FileType("w"),
    )

    resolve.set_defaults(func=_resolve)

    status = subcommands.add_parser(
        "status", description="Query the status of an asynchronous jobs from the results file."
    )

    status.add_argument(
        "async_results",
        help=(
            "path to the file with data of discrimination experiments which can be obtained by "
            "running qbench benchmark using backend with asynchronous flag equal to True."
        ),
        type=FileType("r"),
    )

    status.set_defaults(func=_status)

    tabulate = subcommands.add_parser(
        "tabulate",
        description=(
            "Compute and tabulate probabilities from measurements obtained from the experiments."
        ),
    )

    tabulate.add_argument(
        "sync_results",
        help=(
            "path to the file with results of discrimination experiments. If experiments were "
            "conducted using asynchronous backend, they need to be manually resolved."
        ),
        type=FileType("r"),
    )

    tabulate.add_argument(
        "output",
        help=(
            "path to the resulting CSV file. This file will contain columns 'target', 'ancilla' "
            "'phi' and 'disc_prob' with obvious meanings. If each experiment contained "
            "mitigation data, the 'mitigated_disc_prob` containing discrimination probabilities "
            "computed using mitigated bitstrings will also be added."
        ),
        type=FileType("w"),
    )

    tabulate.set_defaults(func=_tabulate)

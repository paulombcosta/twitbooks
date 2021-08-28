from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, \
    TransferSpeedColumn, TimeRemainingColumn
from rich import print
import sys


def sync_progress() -> Progress:
    return Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )


def download_progress() -> Progress:
    return Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )


def info(msg: str):
    print("[green]{}".format(msg))


def error(msg: str):
    print("[red]ERROR: {}".format(msg))
    sys.exit(1)

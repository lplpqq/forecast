from argparse import ArgumentParser, Namespace
from functools import cache


class ForecastNamespace(Namespace):
    initial_run: bool


@cache
def create_parser() -> ArgumentParser:
    ap = ArgumentParser()
    ap.add_argument(
        '--initial',
        dest='initial_run',
        action='store_true',
    )

    return ap


def parse_args(parser: ArgumentParser) -> ForecastNamespace:
    np = ForecastNamespace()
    parser.parse_args(namespace=np)

    return np

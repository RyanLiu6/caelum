#!/usr/bin/env python

import click

from vigor.utils import configure_logger


@click.command()
def import_csv() -> None:
    pass


if __name__ == "__main__":
    configure_logger()

    import_csv()

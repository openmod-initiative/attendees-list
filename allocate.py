"""Allocation of things to resources."""
import random

import click
import pandas as pd


@click.command()
@click.argument("resources", nargs=-1)
def random_allocation(resources):
    """Allocates resource to things.

    Reads things to allocate, like workshop participants, to resources. Things are read from stdin.

    Writes allocation as csv to stdout.

    \b
    Example:
        cat things.txt | python allocate.py room1 room2 room3 > allocation.csv

    \b
    Parameters:
        * resources: a list of resource to allocate things to
    """
    things = set(click.get_text_stream('stdin').read().splitlines())
    allocation = _random_allocation(things=things, resources=resources)
    allocation.to_csv(click.get_text_stream('stdout'), header=True)


def _random_allocation(things, resources):
    unallocated = set(things)
    allocated = pd.Series(index=things, data=None)
    allocated.name = "resource"
    group_size = round(len(things) / len(resources))
    for i, resource in enumerate(resources):
        chosen = set(random.sample(
            population=unallocated,
            k=min(group_size, len(unallocated))
        ))
        allocated[chosen] = resource
        unallocated = unallocated - chosen
    if unallocated is not {}:
        allocated[unallocated] = resources[-1]
    return allocated


if __name__ == "__main__":
    random_allocation()

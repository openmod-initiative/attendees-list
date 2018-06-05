"""Allocation of things to resources."""
import random

import click
import pandas as pd
import jinja2


ALLOCATION_TABLE_HTML = './templates/allocation_table.html'
ALLOCATION_ROW_HTML = './templates/allocation_row.html'


@click.group()
def allocate():
    """Allocation of things to resources."""
    pass


@allocate.command()
@click.argument("resources", nargs=-1)
def random_allocation(resources):
    """Randomly allocate things to resources.

    Allocates things like workshop participants to resources. Things are read from stdin.
    List of resources is the only parameter.

    Writes allocation as csv to stdout.

    \b
    Example:
        cat things.txt | python allocate.py random_allocation room1 room2 room3 > allocation.csv

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


@allocate.command()
def html():
    """Renders allocation table to HTML.

    \b
    Reads allocation table as CSV from stdin, writes neatly formatted
    table as HTML to stdout.

    \b
    Example:
        cat allocation.csv | python allocate.py html > allocation.html

    """
    allocation = pd.read_csv(click.get_text_stream('stdin'), index_col=0)
    html = _html_table(allocation)
    click.get_text_stream('stdout').write(html)


def _html_table(allocation):
    with open(ALLOCATION_TABLE_HTML, 'r') as f:
        table_template = jinja2.Template(f.read())

    with open(ALLOCATION_ROW_HTML, 'r') as f:
        row_template = jinja2.Template(f.read())

    groups = {
        resource: sorted([thing.title() for thing in things])
        for resource, things in allocation.groupby('resource').groups.items()
    }

    rows = '\n'.join([row_template.render(name=resource, items=', '.join(things))
                      for resource, things in groups.items()])

    html = table_template.render(rows=rows)

    return html


if __name__ == "__main__":
    allocate()

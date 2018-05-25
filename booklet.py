import yaml

import click
import pandas as pd
import jinja2


PARTICIPANT_HTML = './booklet-templates/participant.html'
BOOKLET_HTML = './booklet-templates/booklet.html'
CSS = './booklet-templates/styles.css'


def render_participant(participant):
    """
    Parameters
    ----------

    participant : pd.Series
        A series with participant details.

    """

    with open(PARTICIPANT_HTML, 'r') as f:
        html_template = jinja2.Template(f.read())

    # Link label for website: clean out some unneccesary bits
    clean_website = participant['website'].replace('https://', '').replace('http://', '').strip('/')

    # Truncate bio if too long
    bio = participant['bio']
    if len(bio) > 550:
        bio = bio[:500].rsplit(' ', 1)[0]
        bio += '... <a href="https://forum.openmod-initiative.org/u/{}">[read more on forum profile]</a>'.format(participant.name)

    html = html_template.render(
        username=participant.name,
        name=participant['name'].title(),
        bio=bio,
        affiliation=participant['affiliation'],
        website_url=participant['website'],
        website_text=clean_website,
        location=participant['location'],
        portrait_url=participant['avatar_url']
    )

    return html


def render_booklet(participants, metadata):

    participants_html = '\n'.join([render_participant(p) for i, p in participants.iterrows()])

    with open(CSS, 'r') as f:
        css = f.read()

    with open(BOOKLET_HTML, 'r') as f:
        html_template = jinja2.Template(f.read())

    html = html_template.render(
        css=css,
        participants=participants_html,
        title=metadata['title'],
        subtitle=metadata['subtitle']
    )

    return html


@click.group()
def booklet():
    """Build an HTML conference participant booklet."""
    pass


@booklet.command()
@click.argument("metadata_file", click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--users", "-u", type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help="Path to user details CSV file.")
def build(metadata_file, users):
    """Build the booklet.

    Reads user details as csv from stdin and writes the booklet to stdout.

    \b
    Parameters
    ----------
    metadata_file : str
        Path to metadata YAML file.

    """
    if not users:
        users = click.get_text_stream('stdin')
    users = pd.read_csv(users, index_col=0)

    with open(metadata_file, 'r') as f:
        metadata = yaml.load(f)

    # Order users by last name
    users['lastname'] = users.name.str.split().str.get(-1)
    users = users.sort_values(by='lastname')

    # Replace NaN with empty string so can do {% if variable %} in jinja templates
    users = users.replace(pd.np.nan, '')

    html = render_booklet(users, metadata)

    click.echo(html)


if __name__ == "__main__":
    booklet()

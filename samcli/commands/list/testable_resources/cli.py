"""
Sets up the cli for resources
"""

import click

from samcli.cli.main import pass_context

HELP_TEXT = """
Get a summary of the testable resources in the stack.\n
This command will show both the cloud and local endpoints that can
be used with sam local and sam sync. Currently the testable resources
are lambda functions and API Gateway API resources.
"""

# @click.command(name="resources", cls=GenerateEventCommand, help=HELP_TEXT)


@click.command(name="testable-resources", help=HELP_TEXT)
@click.option(
    "--stack-name",
    help=(
        "Name of corresponding deployed stack.(Not including"
        "a stack name will only show local resources defined"
        "in the template.)"
    ),
    type=click.STRING,
)
@click.option(
    "--output",
    help=("Output the results from the command in a given" "output format (json, yaml, table or text)."),
    type=click.Choice(["json", "yaml", "table", "text"], case_sensitive=False),
)
@pass_context
def cli(self, stack_name, output):
    """
    Generate an event for one of the services listed below:
    """

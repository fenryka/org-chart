import click

from typing import Dict, AnyStr
from csv_loader import load_csv, Employee

# -------------------------------------------------------------------------------


@click.command()
@click.argument("data", type=click.File("r"))
@click.option("-f", "--file", default="org-chart.png", help="output file")
def cli(data):
    csv = load_csv(data)
    employees_by_id: Dict[AnyStr, Employee] = csv['employees_by_id']

    for employee in employees_by_id.values():
        if employee.supervisor == "":
            click.echo(employee.name)

# -------------------------------------------------------------------------------


if __name__ == "__main__":
    cli()

import sys
import click
import random
import webcolors

from ete3 import Tree, TreeStyle, TextFace, add_face_to_node, NodeStyle, TextFace
from typing import List, Dict, AnyStr, Callable

# -------------------------------------------------------------------------------

locationColours = {}
teamColours = {}
allColours = [*webcolors.CSS3_NAMES_TO_HEX]

# -------------------------------------------------------------------------------


def pick_colours():
    bgColour = random.choice(allColours)
    rgb = webcolors.name_to_rgb(bgColour, spec=webcolors.CSS3)

    luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    fgColour = "white" if (luminance < 140) else "black"

    return [bgColour, fgColour]

# -------------------------------------------------------------------------------


class Employee:
    setters = {
        "Employee ID": lambda x, y: setattr(x, "employee_id", y),
        "Name": lambda x, y: setattr(x, "name", y),
        "Location": lambda x, y: setattr(x, "location", y),
        "Grade": lambda x, y: setattr(x, "grade", y),
        "Supervisor ID": lambda x, y: setattr(x, "supervisor", y),
        "Role": lambda x, y: setattr(x, "role", y),
        "Image": lambda x, y: setattr(x, "image", y),
        "Top-level team": lambda x, y: setattr(x, "team", y),
        "Gender": lambda x, y: setattr(x, "gender", y),
        "Start Date": lambda x, y: setattr(x, "start_date", y)
    }

    @staticmethod
    def initial_attributes():
        return {k: -1 for k in Employee.setters.keys()}

    def __init__(self, map_: Dict, tokens_: List, colour_: Callable):
        self.employee_id = ""
        self.name = ""
        self.grade = ""
        self.supervisor = ""
        self.image = ""
        self.role = ""
        self.location = ""
        self.team = ""
        self.gender = ""
        self.reports = []

        for k, v in map_.items():
            Employee.setters[k](self, tokens_[v])

        self.colours = colour_(self)

    def __str__(self):
        return self.name


# -------------------------------------------------------------------------------


def colour_by_team(employee_: Employee):
    return teamColours.setdefault(employee_.team, pick_colours())


def colour_by_role(employee_: Employee):
    return teamColours.setdefault(employee_.role, pick_colours())


def colour_by_gender(employee_: Employee):
    return teamColours.setdefault(employee_.gender, pick_colours())


def colour_by_location(employee_: Employee):
    return teamColours.setdefault(employee_.location, pick_colours())


def colour_by_grade(employee_: Employee):
    return teamColours.setdefault(employee_.grade, pick_colours())


def colour_by_none(_):
    return ["White", "Black"]

# -------------------------------------------------------------------------------


def ete_graph(employee_: AnyStr, employees_: Dict, manager_=None):
    employee = employees_[employee_]

    employeeNode = manager_.add_child(name=employee.name, dist=1) if manager_ else Tree(name=employee.name)

    nodeStyle = NodeStyle()
    nodeStyle["shape"] = "sphere"
    nodeStyle["size"] = 40 if employee.role else 20
    nodeStyle["fgcolor"] = locationColours.setdefault(employees_[employee_].location, random.choice(allColours))

    employeeNode.set_style(nodeStyle)

    def text_face(name_, colour_, fsize_=30):
        face = TextFace(name_, tight_text=False, fsize=fsize_)
        face.margin_right = 5
        face.margin_left = 5
        face.background.color = colour_[0]
        face.fgcolor = colour_[1]
        return face

    position = "branch-right"

    employeeNode.add_face(text_face(employee.name, employee.colours), column=0, position=position)

    if employee.role:
        employeeNode.add_face(text_face(employee.role, employee.colours, 20), column=0, position=position)

    for report in employees_[employee_].reports:
        ete_graph(report, employees_, employeeNode)

    if not manager_:
        return employeeNode


# -------------------------------------------------------------------------------

def tree_style():
    ts = TreeStyle()
    ts.show_leaf_name = False  # we're manually adding text faces
    ts.mode = "c"
    ts.show_scale = False
    ts.scale = None
    ts.optimal_scale_level = "full"
    ts.force_topology = True

    return ts


# -------------------------------------------------------------------------------

def handle_colour_by(_, __, value: AnyStr):
    if value == "role":
        return colour_by_role
    elif value == "location":
        return colour_by_location
    elif value == "grade":
        return colour_by_grade
    elif value == "gender":
        return colour_by_gender
    elif value == "team":
        return colour_by_team
    elif value == "none":
        return colour_by_none


# -------------------------------------------------------------------------------

@click.command()
@click.argument("data", type=click.File("r"))
@click.option("-r", "--root", default=None, help="Person to use as the top of the chart")
@click.option("-f", "--file", default="org-chart.png", help="output file")
@click.option("-c", "--colour-by", type=click.Choice(["role", "location", "grade", "gender", "team", "none"]),
              default="team", callback=handle_colour_by)
def cli(data, root, file, colour_by):
    employees = []

    def normalise(str_):
        return str_.rstrip("\n")

    attributes = Employee.initial_attributes()

    headers = list(map(normalise, data.readline().split(',')))
    for i, token in enumerate(headers):
        attributes[token] = i

    for line in data.readlines()[:]:
        tokens = list(map(normalise, line.split(',')))
        employees.append(Employee(attributes, tokens, colour_by))

    employeesById = {k.employee_id: k for k in employees}
    nameToId = {k.name: k.employee_id for k in employees}

    # TODO Don't take two passes to do this
    for employee in employees:
        try:
            employeesById[employee.supervisor].reports.append(employee.employee_id)
        except KeyError:
            pass

        if employee.supervisor == "" and not root:
            root = employee.name

    try:
        employee_id = nameToId[root]
    except KeyError:
        sys.stderr.write(root + " Does not exist in csv file\n")
        sys.exit(1)

    tree = ete_graph(employee_id, employeesById)
    tree.render(file, tree_style=tree_style())

# -------------------------------------------------------------------------------


if __name__ == "__main__":
    cli()

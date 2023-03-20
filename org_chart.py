import sys
import click
import random
import webcolors

from ete3 import Tree, TreeStyle, NodeStyle, TextFace
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
        "Employee Id": lambda x, y: setattr(x, "employee_id", y),
        "Name": lambda x, y: setattr(x, "name", y),
        "Full Name": lambda x, y: setattr(x, "name", y),
        "Location": lambda x, y: setattr(x, "location", y),
        "Office": lambda x, y: setattr(x, "location", y),
        "Grade": lambda x, y: setattr(x, "grade", y),
        "Supervisor ID": lambda x, y: setattr(x, "supervisor", y),
        "Reports To": lambda x, y: setattr(x, "supervisor", y),
        "Role": lambda x, y: setattr(x, "role", y),
        "Image": lambda x, y: setattr(x, "image", y),
        "Top-level team": lambda x, y: setattr(x, "tl_team", y),
        "Division": lambda x, y: setattr(x, "tl_team", y),
        "Team": lambda x, y: setattr(x, "team", y),
        "Gender": lambda x, y: setattr(x, "gender", y),
        "Start Date": lambda x, y: setattr(x, "start_date", y),
        "Job Title": lambda x, y: setattr(x, "job_title", y),
        "Date of Birth": lambda x, y: setattr(x, "dob", y)
    }

    @staticmethod
    def initial_attributes():
        return {k: -1 for k in Employee.setters.keys()}

    def __init__(self, colour_: Callable, map_: Dict, tokens_):
        self.employee_id = ""
        self.name = ""
        self.grade = ""
        self.supervisor = ""
        self.image = ""
        self.role = ""
        self.location = ""
        self.tl_team = ""
        self.team = ""
        self.gender = ""
        self.job_title = ""
        self.dob = ""
        self.reports = []

        self.colours = colour_(self)

        for k, v in filter(lambda x: x[1] != -1, map_.items()):
            try:
                Employee.setters[k](self, tokens_[v])
            except KeyError:
                pass

    def __str__(self):
        return "id: {}\n  name: {}\n  grade: {}\n  supervisor: {}\n  image: {}\n  role: {}\n  location: {}\n  team: {}"\
               "\n  tl team: {}\n  gender: {}\n  job title: {}\n    [{}]".format(
                    self.employee_id,
                    self.name,
                    self.grade,
                    self.supervisor,
                    self.image,
                    self.role,
                    self.location,
                    self.tl_team,
                    self.team,
                    self.gender,
                    self.job_title,
                    ", ".join(self.reports))


# -------------------------------------------------------------------------------


def colour_by_team(employee_: Employee):
    return teamColours.setdefault(employee_.tl_team, pick_colours())


def colour_by_role(employee_: Employee):
    return teamColours.setdefault(employee_.role, pick_colours())


def colour_by_gender(employee_: Employee):
    return teamColours.setdefault(employee_.gender, pick_colours())


def colour_by_location(employee_: Employee):
    return teamColours.setdefault(employee_.location, pick_colours())


def colour_by_grade(employee_: Employee):
    return teamColours.setdefault(employee_.grade, pick_colours())


def colour_by_jon_title(employee_: Employee):
    return teamColours.setdefault(employee_.job_title, pick_colours())


def colour_by_none(_):
    return ["White", "Black"]

# -------------------------------------------------------------------------------


def ete_graph(employee_: AnyStr, employees_: Dict, manager_=None):
    employee = employees_[employee_]

    employee_node = manager_.add_child(name=employee.name, dist=1) if manager_ else Tree(name=employee.name)

    node_style = NodeStyle()
    node_style["shape"] = "sphere"
    node_style["size"] = 40 if employee.role else 20
    node_style["fgcolor"] = locationColours.setdefault(employees_[employee_].location, random.choice(allColours))

    employee_node.set_style(node_style)

    def text_face(name_, colour_, fsize_=30):
        face = TextFace(name_, tight_text=False, fsize=fsize_)
        face.margin_right = 5
        face.margin_left = 5
        face.background.color = colour_[0]
        face.fgcolor = colour_[1]
        # face.rotation = -45
        return face

    position = "branch-right"

    employee_node.add_face(text_face(employee.name, employee.colours), column=0, position=position)

    if employee.role:
        employee_node.add_face(text_face(employee.role, employee.colours, 20), column=0, position=position)

    for report in employees_[employee_].reports:
        ete_graph(report, employees_, employee_node)

    if not manager_:
        return employee_node


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


def tree_style_rect():
    ts = TreeStyle()
    ts.show_leaf_name = False  # we're manually adding text faces
    ts.mode = "r"
    ts.rotation = 90
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
    elif value == "title":
        return colour_by_jon_title
    elif value == "none":
        return colour_by_none


# -------------------------------------------------------------------------------

@click.command()
@click.argument("data", type=click.File("r"))
@click.option("-r", "--root", default=None, help="Person to use as the top of the chart")
@click.option("-f", "--file", default="org-chart.png", help="output file")
@click.option("-c", "--colour-by", type=click.Choice(["role", "location", "grade", "gender", "team", "none", "title"]),
              default="none", callback=handle_colour_by)
def cli(data, root, file, colour_by):
    employees = {}

    def normalise(str_):
        return str_.rstrip("\n")

    attributes = Employee.initial_attributes()

    # Read the first line of the CSV file to grab the list of tokens each column represents
    headers = list(map(normalise, data.readline().split(',')))

    for i, token in enumerate(headers):
        attributes[token] = i

    for line in data.readlines()[:]:
        tokens = list(map(normalise, line.split(',')))
        employee = Employee(colour_by, attributes, tokens)
        employees[employee.employee_id] = employee

    name_to_id = {k.name: k.employee_id for k in employees.values()}

    # TODO Don't take two passes to do this
    for employee in employees.values():
        try:
            # print (employee.name + " -> " + employees[employee.supervisor].name)
            employees[employee.supervisor].reports.append(employee.employee_id)
        except KeyError:
            pass

        if employee.supervisor == "" and not root:
            root = employee.name

    try:
        employee_id = name_to_id[root]
    except KeyError:
        sys.stderr.write(root + " Does not exist in csv file\n")
        sys.exit(1)

    tree = ete_graph(employee_id, employees)
    tree.render(file, tree_style=tree_style())
    #tree.render(file, tree_style=tree_style_rect())

# -------------------------------------------------------------------------------


if __name__ == "__main__":
    cli()

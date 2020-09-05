import sys
import click

from ete3 import Tree, TreeStyle, TextFace, add_face_to_node, NodeStyle, TextFace

# -------------------------------------------------------------------------------

locationColours = {
    "London": "darkred",
    "Dublin": "green",
    "New York": "blue",
    "Singapore": "yellow"
}


# -------------------------------------------------------------------------------

class Employee:
    def __init__(self, id_, name_, grade_, supervisor_, role_, location_):
        self.id = id_
        self.name = name_
        self.grade = grade_
        self.supervisor = supervisor_
        self.role = role_
        self.location = location_
        self.reports = []

    def __str__(self):
        return self.name


# -------------------------------------------------------------------------------

def ete_graph(employee_, employees_, manager_=None):
    name = employees_[employee_].name

    employee = manager_.add_child(name=name, dist=1) if manager_ else Tree(name=name)

    nstyle = NodeStyle()
    nstyle["shape"] = "sphere"
    nstyle["size"] = 25
    nstyle["fgcolor"] = locationColours[employees_[employee_].location]

    employee.set_style(nstyle)

    face = TextFace(name, tight_text=False, fsize=30)
    face.margin_right = 5
    face.margin_left = 5

    position = "branch-right"

    employee.add_face(face, column=0, position=position)

    for report in employees_[employee_].reports:
        ete_graph(report, employees_, employee)

    if not manager_:
        return employee


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

@click.command()
@click.option("--data", type=click.File("r"), help="File to parse")
@click.option("--root", default=None, help="Person to use as the top of the chart")
@click.option("--file", default="org-chart.png", help="output file")
def cli(data, root, file):
    employees = []

    for line in data.readlines()[1:]:
        vals = line.split(',')
        employees.append(Employee(vals[0], vals[1], vals[2], vals[3], vals[4], vals[5]))

    employeesById = {k.id: k for k in employees}
    nameToId = {k.name: k.id for k in employees}

    for employee in employees:
        try:
            employeesById[employee.supervisor].reports.append(employee.id)
        except KeyError:
            pass

        if employee.supervisor == "" and not root:
            root = employee.name

    try:
        empoyee_id = nameToId[root]
    except KeyError:
        sys.stderr.write(root + " Does not exist in csv file\n")
        sys.exit(1)

    tree = ete_graph(empoyee_id, employeesById)
    tree.render(file, tree_style=tree_style())

# -------------------------------------------------------------------------------

import click

from typing import Dict, List, Callable


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
        "Top-Level Team": lambda x, y: setattr(x, "team", y),
        "Gender": lambda x, y: setattr(x, "gender", y),
        "Start Date": lambda x, y: setattr(x, "start_date", y),
        "Job Title": lambda x, y: setattr(x, "job_title", y),
        "Division": lambda x, y: setattr(x, "division", y),
        "Ethnicity": lambda x, y: setattr(x, "ethnicity", y),
        "Perm": lambda x, y: setattr(x, "perm", True if y == "Y" else False)
    }

    @staticmethod
    def initial_attributes():
        return {k: -1 for k in Employee.setters.keys()}

    def __init__(self, map_: Dict, tokens_: List, colour_: Callable = lambda _: "black" ):
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
        self.division = ""
        self.ethnicity = ""
        self.perm = False
        self.reports = []
        self.dob = ""
        self.reports = []

        for k, v in filter(lambda x: x[1] != -1, map_.items()):
            try:
                Employee.setters[k](self, tokens_[v])
            except KeyError:
                click.echo("Unknown key: " + k + " val: " + (tokens_[v] if (tokens_[v]) else "NULL"), err=True)
                pass

        self.colours = colour_(self)

    def __str__(self):
        return "id: {}\n  name: {}\n  grade: {}\n  supervisor: {}\n  image: {}\n  role: {}\n  location: {}\n  team: {}"\
               + "\n  gender: {}\n  job title: {}\n    [{}]".format(
                    self.employee_id,
                    self.name,
                    self.grade,
                    self.supervisor,
                    self.image,
                    self.role,
                    self.location,
                    self.team,
                    self.gender,
                    self.job_title,
                    ", ".join(self.reports))


def load_csv(data, colour_by: Callable = None):
    def normalise(str_):
        return str_.rstrip("\n")

    attributes = Employee.initial_attributes()

    headers = list(map(normalise, data.readline().split(',')))
    for i, token in enumerate(headers):
        attributes[token] = i

    employees = []
    for line in data.readlines()[:]:
        tokens = list(map(normalise, line.split(',')))
        if colour_by:
            employees.append(Employee(attributes, tokens, colour_by))
        else:
            employees.append(Employee(attributes, tokens))

    employees_by_id = {k.employee_id: k for k in employees}
    employees_by_name = {k.name: k.employee_id for k in employees}

    for employee in employees:
        try:
            employees_by_id[employee.supervisor].reports.append(employee.employee_id)
        except KeyError:
            pass

    return {
        "employees_by_id": employees_by_id,
        "employees_by_name": employees_by_name
    }

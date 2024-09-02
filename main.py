import json
from collections import defaultdict
import sys

# Assumption: School names are unique and can be used as identifiers
# Assumption: Distance score is normalized using the maximum distance to any student for each school
# Assumption: The coordinate system for locations is a 2D Cartesian plane


class Location:
    x: int
    y: int

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


def distance(a: Location, b: Location) -> int:
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


class School:
    name: str
    location: Location
    maxAllocation: int
    max_distance: float

    def __init__(self, name: str, location: Location, maxAllocation: int) -> None:
        self.name = name
        self.location = location
        self.maxAllocation = maxAllocation
        self.max_distance = 0


class Student:
    id: int
    homeLocation: Location
    alumni: str | None
    volunteer: str | None

    def __init__(
        self,
        student_id: int,
        homeLocation: Location,
        alumni: str | None = None,
        volunteer: str | None = None,
    ) -> None:
        self.id = student_id
        self.homeLocation = homeLocation
        self.alumni = alumni
        self.volunteer = volunteer

    def compute_score(self, school: School) -> float:
        score = 0
        if self.alumni and self.alumni == school.name:
            score += 0.3
        if self.volunteer and self.volunteer == school.name:
            score += 0.2
        score += 0.5 * (
            1 - distance(self.homeLocation, school.location) / school.max_distance
        )
        return score


with open(sys.argv[1]) as f:
    input_data = json.load(f)

schools = {
    school["name"]: School(
        school["name"],
        Location(school["location"][0], school["location"][1]),
        school["maxAllocation"],
    )
    for school in input_data.get("schools", [])
}
students = [
    Student(
        student["id"],
        Location(student["homeLocation"][0], student["homeLocation"][1]),
        student.get("alumni"),
        student.get("volunteer"),
    )
    for student in input_data.get("students", [])
]

for school in schools.values():
    school.max_distance = max(
        [distance(student.homeLocation, school.location) for student in students]
    )

admitted_students = set()
school_admissions = defaultdict(list)
scores = {
    (student.id, school.name): student.compute_score(school)
    for school in schools.values()
    for student in students
}

for (student_id, school_name), _ in sorted(
    scores.items(), key=(lambda x: (x[1], x[0][0])), reverse=True
):
    if student_id in admitted_students:
        continue
    if len(school_admissions[school_name]) >= schools[school_name].maxAllocation:
        continue
    school_admissions[school_name].append(student_id)

with open("output.json", "w+") as f:
    json.dump(dict(school_admissions), f)

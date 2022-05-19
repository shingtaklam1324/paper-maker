from dataclasses import dataclass
from typing import List, Dict, Tuple
import re
from glob import glob
from random import choice

pattern = re.compile(r"---\ncourse: (.+)\ncourse_year: (?:.+)\nquestion_number: (?:.+)\ntags:\n(?:- (?:.+)\n)+title: '?Paper (.+), Section (.+),.*'?\nyear: (.+)\n---")
base_path = "maths-tripos-questions/src/part-ib/"

def get_info_from_paper(path: str):
    with open(path, "r") as f:
        text = f.read()
    res = pattern.match(text)
    if res is None:
        raise Exception(f"Could not parse paper header for: {path}")
    [course, paper, section, year] = res.groups()
    return [course, paper, section, int(year)]

@dataclass
class Course:
    name: str
    num_short: int
    num_long: int
    min_year: int
    max_year: int

    def __hash__(self):
        return hash(self.name)

@dataclass
class Config:
    courses: List[Course]
    out_path: str

    def build(self):
        questions: Dict[Course, Tuple[List[str], List[str]]] = {}
        for path in glob(base_path + "201*.md"):
            [course, _, section, year] = get_info_from_paper(path)
            for c in self.courses:
                if c.name == course and c.min_year <= year <= c.max_year:
                    qc = questions.setdefault(c, ([], []))
                    if section == "1" or section == "I":
                        questions[c] = (qc[0] + [path], qc[1])
                    elif section == "2" or section == "II":
                        questions[c] = (qc[0], qc[1] + [path])
                    break
        chosen_questions = [[], []]
        for k, v in questions.items():
            s = list(v)
            n = (k.num_short, k.num_long)
            for j in [0, 1]:
                if len(v[j]) < n[j]:
                    raise Exception(f"No questions for course {k.name} section {j+1}")
                if len(v[j]) > n[j]:
                    chosen_questions[j].append(choice(v[j]))
        with open(self.out_path, "w") as out:
            for s in chosen_questions:
                for p in s:
                    [course, paper, section, year] = get_info_from_paper(p)
                    f = open(p, "r")
                    print(f"{year} Paper {paper} Section {section} Course: {course}" + "\n".join(f.readlines()[11:]) + "\n\n", file=out)
                    f.close()

min_year=2015
max_year=2019

# In the following configs, we use Analysis II on papers 1 and 3, Met & Top on papers 2 and 4
paper1 = Config([
    Course("Linear Algebra", 1, 1, min_year, max_year),
    Course("Analysis II", 0, 1, min_year, max_year),
    Course("Markov Chains", 0, 1, min_year, max_year),
    Course("Complex Analysis or Complex Methods", 1, 1, min_year, max_year),
    Course("Numerical Analysis", 1, 1, min_year, max_year),
    Course("Geometry", 1, 1, min_year, max_year),
    Course("Statistics", 1, 1, min_year, max_year),
    Course("Groups, Rings and Modules", 0, 1, min_year, max_year),
    Course("Variational Principles", 1, 0, min_year, max_year)
], "out.md")

paper1.build()
# c = Config([Course(name="Linear Algebra", num_short=1, num_long=1, min_year=2015, max_year=2017)], out_path="out.md")
# c.build()

            

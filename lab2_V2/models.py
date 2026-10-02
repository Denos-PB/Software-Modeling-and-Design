from dataclasses import dataclass
from typing import Optional


@dataclass
class Department:
    name: str
    id: Optional[int] = None

@dataclass
class StudentGroup:
    name: str
    department_id: int
    id: Optional[int] = None

@dataclass
class Student:
    full_name: str
    email: str
    group_id: int
    id: Optional[int] = None

@dataclass
class StudentCard:
    student_id: int
    number: str
    id: Optional[int] = None

@dataclass
class Teacher:
    full_name: str
    department_id: int
    id: Optional[int] = None

@dataclass
class Course:
    name: str
    credits: int
    teacher_id: int
    id: Optional[int] = None

@dataclass
class Enrollment:
    student_id: int
    course_id: int
    grade: Optional[int] = None
    id: Optional[int] = None
from dataclasses import asdict
from models import Department, StudentGroup, Student, StudentCard, Teacher, Course, Enrollment


class UniversityRepository:
    TABLES = {
        Department: "departments", StudentGroup: "student_groups",
        Student: "students", StudentCard: "student_cards",
        Teacher: "teachers", Course: "courses", Enrollment: "enrollments",
    }

    def __init__(self, database):
        self.connection = database.connection

    def _table(self, model):
        if model not in self.TABLES:
            raise ValueError("Невідомий клас моделі")
        return self.TABLES[model]

    def add(self, entity):
        table = self._table(type(entity))
        if entity.id is not None:
            raise ValueError("Новий об'єкт не повинен мати id")
        data = asdict(entity)
        data.pop("id")
        columns = ", ".join(data)
        placeholders = ", ".join("?" for _ in data)
        with self.connection:
            cursor = self.connection.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                tuple(data.values()),
            )
        entity.id = cursor.lastrowid
        return entity

    def get(self, model, entity_id):
        table = self._table(model)
        row = self.connection.execute(
            f"SELECT * FROM {table} WHERE id = ?", (entity_id,)
        ).fetchone()
        return model(**dict(row)) if row else None

    def get_all(self, model):
        table = self._table(model)
        rows = self.connection.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
        return [model(**dict(row)) for row in rows]

    def update(self, entity):
        table = self._table(type(entity))
        if entity.id is None:
            raise ValueError("Для оновлення потрібен id")
        data = asdict(entity)
        entity_id = data.pop("id")
        assignments = ", ".join(f"{column} = ?" for column in data)
        with self.connection:
            cursor = self.connection.execute(
                f"UPDATE {table} SET {assignments} WHERE id = ?",
                (*data.values(), entity_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Запис не знайдено")
        return entity

    def delete(self, model, entity_id):
        table = self._table(model)
        with self.connection:
            cursor = self.connection.execute(
                f"DELETE FROM {table} WHERE id = ?", (entity_id,)
            )
        return cursor.rowcount > 0

    def enroll(self, student_id, course_id):
        return self.add(Enrollment(student_id, course_id))

    def set_grade(self, enrollment_id, grade):
        if type(grade) is not int or not 0 <= grade <= 100:
            raise ValueError("Оцінка має бути цілим числом від 0 до 100")
        enrollment = self.get(Enrollment, enrollment_id)
        if enrollment is None:
            raise ValueError("Запис на курс не знайдено")
        enrollment.grade = grade
        return self.update(enrollment)

    def student_report(self, student_id):
        rows = self.connection.execute("""
            SELECT c.name AS course, t.full_name AS teacher, e.grade
            FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE e.student_id = ? ORDER BY c.name
        """, (student_id,)).fetchall()
        return [dict(row) for row in rows]

    def average_grade(self, student_id):
        return self.connection.execute(
            "SELECT AVG(grade) FROM enrollments WHERE student_id = ?", (student_id,)
        ).fetchone()[0]

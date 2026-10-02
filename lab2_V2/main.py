import argparse
import sqlite3
from pathlib import Path
from database import Database
from models import Department, StudentGroup, Student, StudentCard, Teacher, Course
from repository import UniversityRepository

def demo(repo):
    department = repo.add(Department("Інженерія програмного забезпечення"))
    group = repo.add(StudentGroup("ПЗ-31", department.id))
    student = repo.add(Student("Дмитро Петренко", "dmytro@example.com", group.id))
    repo.add(StudentCard(student.id, "КВ123456"))
    teacher = repo.add(Teacher("Олена Коваль", department.id))
    course = repo.add(Course("Бази даних", 5, teacher.id))
    enrollment = repo.enroll(student.id, course.id)
    repo.set_grade(enrollment.id, 95)
    print("Студенти:", repo.get_all(Student))
    print("Успішність:", repo.student_report(student.id))
    print("Середній бал:", repo.average_grade(student.id))
    student.email = "new.email@example.com"
    repo.update(student)
    print("Оновлений студент:", repo.get(Student, student.id))
    temporary = repo.add(Student("Тестовий Студент", "temp@example.com", group.id))
    print("Видалення тестового студента:", repo.delete(Student, temporary.id))

def menu(repo):
    models = list(repo.TABLES)
    while True:
        print("\n1 Кафедра | 2 Група | 3 Студент | 4 Квиток | 5 Викладач | 6 Курс")
        print("7 Запис на курс | 8 Оцінка | 9 Список | 10 Звіт студента")
        print("11 Змінити email студента | 12 Видалити запис | 0 Вихід")
        try:
            choice = input("Оберіть дію: ").strip()
            if choice == "0":
                return
            if choice == "1":
                result = repo.add(Department(input("Назва кафедри: ")))
            elif choice == "2":
                result = repo.add(StudentGroup(input("Назва групи: "), int(input("ID кафедри: "))))
            elif choice == "3":
                result = repo.add(Student(input("ПІБ: "), input("Email: "), int(input("ID групи: "))))
            elif choice == "4":
                result = repo.add(StudentCard(int(input("ID студента: ")), input("Номер квитка: ")))
            elif choice == "5":
                result = repo.add(Teacher(input("ПІБ: "), int(input("ID кафедри: "))))
            elif choice == "6":
                result = repo.add(Course(input("Назва курсу: "), int(input("Кредити: ")), int(input("ID викладача: "))))
            elif choice == "7":
                result = repo.enroll(int(input("ID студента: ")), int(input("ID курсу: ")))
            elif choice == "8":
                result = repo.set_grade(int(input("ID запису на курс: ")), int(input("Оцінка 0–100: ")))
            elif choice in ("9", "12"):
                for index, model in enumerate(models, 1):
                    print(index, model.__name__)
                index = int(input("Номер типу: "))
                if not 1 <= index <= len(models):
                    raise ValueError("Невідомий тип")
                model = models[index - 1]
                if choice == "9":
                    result = repo.get_all(model)
                else:
                    result = repo.delete(model, int(input("ID для видалення: ")))
            elif choice == "10":
                student_id = int(input("ID студента: "))
                if repo.get(Student, student_id) is None:
                    raise ValueError("Студента не знайдено")
                result = repo.student_report(student_id)
                print("Середній бал:", repo.average_grade(student_id))
            elif choice == "11":
                student = repo.get(Student, int(input("ID студента: ")))
                if student is None:
                    raise ValueError("Студента не знайдено")
                student.email = input("Новий email: ")
                result = repo.update(student)
            else:
                print("Невідома дія")
                continue
            if isinstance(result, list):
                for item in result:
                    print(item)
                if not result:
                    print("Записів немає")
            else:
                print(result)
        except (ValueError, sqlite3.IntegrityError) as error:
            print("Помилка даних:", error)
        except (EOFError, KeyboardInterrupt):
            print("\nЗавершення роботи")
            return

def main():
    parser = argparse.ArgumentParser(description="Автоматизація університету")
    parser.add_argument("--demo", action="store_true", help="Приклад в окремій тимчасовій БД")
    parser.add_argument("--db", default=str(Path(__file__).with_name("university.db")))
    args = parser.parse_args()
    with Database(":memory:" if args.demo else args.db) as database:
        repo = UniversityRepository(database)
        if args.demo:
            demo(repo)
        else:
            menu(repo)

if __name__ == "__main__":
    main()
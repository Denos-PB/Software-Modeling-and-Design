PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0)
);
CREATE TABLE IF NOT EXISTS student_groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    department_id INTEGER NOT NULL REFERENCES departments(id)
);
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    email TEXT NOT NULL UNIQUE CHECK(length(trim(email)) > 0),
    group_id INTEGER NOT NULL REFERENCES student_groups(id)
);
CREATE TABLE IF NOT EXISTS student_cards (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
    number TEXT NOT NULL UNIQUE CHECK(length(trim(number)) > 0)
);
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    department_id INTEGER NOT NULL REFERENCES departments(id)
);
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    credits INTEGER NOT NULL CHECK(typeof(credits) = 'integer' AND credits BETWEEN 1 AND 30),
    teacher_id INTEGER NOT NULL REFERENCES teachers(id)
);
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    grade INTEGER CHECK(grade IS NULL OR (typeof(grade) = 'integer' AND grade BETWEEN 0 AND 100)),
    UNIQUE(student_id, course_id)
);

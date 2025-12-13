CREATE DATABASE planifydb;

CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    username VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    contact_number VARCHAR(11) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL
);

CREATE TABLE course (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(20) NOT NULL,
    block_section VARCHAR(20) NOT NULL,
    description TEXT,
    educator_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enrollment_code VARCHAR(10) UNIQUE NOT NULL,
    FOREIGN KEY (educator_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE lesson_plan (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    course_id INTEGER NOT NULL,
    educator_id INTEGER NOT NULL,
    objectives TEXT,
    topic VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE,
    FOREIGN KEY (educator_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE learning_material (
    id SERIAL PRIMARY KEY,
    lesson_plan_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plan(id) ON DELETE CASCADE
);

CREATE TABLE enrollment (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE,
    CONSTRAINT unique_enrollment UNIQUE (student_id, course_id)
);

CREATE TABLE attendance_record (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    recorded_by INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT unique_attendance UNIQUE (student_id, course_id, date)
);

CREATE TABLE contact_message (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
DROP TABLE IF EXISTS responses;
DROP TABLE IF EXISTS vacancies;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS experiences;
DROP TABLE IF EXISTS employment_types;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('candidate', 'recruiter', 'admin')) NOT NULL,
    full_name TEXT,
    phone TEXT
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE employment_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE vacancies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiter_id INTEGER,
    title TEXT NOT NULL,
    category_code TEXT,
    salary_from INTEGER,
    salary_to INTEGER,
    experience_code TEXT,
    employment_code TEXT,
    description TEXT,
    company_name TEXT,
    city TEXT,
    image_url TEXT,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recruiter_id) REFERENCES users(id)
);

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vacancy_id INTEGER,
    candidate_id INTEGER,
    cover_letter TEXT,
    resume_url TEXT,
    status TEXT DEFAULT 'Новый',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vacancy_id, candidate_id),
    FOREIGN KEY (vacancy_id) REFERENCES vacancies(id),
    FOREIGN KEY (candidate_id) REFERENCES users(id)
);

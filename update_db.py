import sqlite3


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS responses")
    cursor.execute("DROP TABLE IF EXISTS vacancies")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS categories")
    cursor.execute("DROP TABLE IF EXISTS experiences")
    cursor.execute("DROP TABLE IF EXISTS employment_types")

    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('candidate', 'recruiter', 'admin')) NOT NULL,
            full_name TEXT,
            phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE employment_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
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
        )
    """)

    cursor.execute("""
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
        )
    """)

    categories_data = [
        ('IT', 'IT / Разработка'),
        ('Marketing', 'Маркетинг / PR'),
        ('Transport', 'Транспорт / Логистика'),
        ('Sales', 'Продажи'),
    ]
    experiences_data = [
        ('no_experience', 'Без опыта'),
        ('1-3_years', 'От 1 до 3 лет'),
        ('3-6_years', 'От 3 до 6 лет'),
    ]
    employment_data = [
        ('full-time', 'Полный день'),
        ('remote', 'Удаленная работа'),
        ('part-time', 'Частичная занятость'),
    ]

    cursor.executemany("INSERT INTO categories (code, name) VALUES (?, ?)", categories_data)
    cursor.executemany("INSERT INTO experiences (code, name) VALUES (?, ?)", experiences_data)
    cursor.executemany("INSERT INTO employment_types (code, name) VALUES (?, ?)", employment_data)

    cursor.executemany("""
        INSERT INTO users (username, email, password_hash, role, full_name, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ('admin', 'admin@work.ru', 'admin123', 'admin', 'Главный Администратор', '+79990000000'),
        ('recruiter1', 'hr@yandex.ru', 'recruiter123', 'recruiter', 'Анна Иванова', '+79991112233'),
        ('candidate1', 'ivan@mail.ru', 'candidate123', 'candidate', 'Иван Петров', '+79995554433'),
    ])

    test_vacancies = [
        (2, 'Python/Flask разработчик', 'IT', 90000, 140000, '1-3_years', 'remote',
         'Ищем бэкендера для разработки веб-сервисов. Знание Flask/Django и SQL обязательно.',
         'ТехноРешения', 'Москва', None),
        (2, 'Frontend-разработчик (Стажер)', 'IT', 40000, 60000, 'no_experience', 'full-time',
         'Стажировка для начинающих. Нужно знать HTML, CSS и базовый JavaScript.',
         'ВебСтудия', 'Санкт-Петербург', None),
        (2, 'Интернет-маркетолог', 'Marketing', 80000, None, '1-3_years', 'full-time',
         'Настройка контекстной рекламы, ведение соцсетей, аналитика трафика.',
         'Продвижение Плюс', 'Новосибирск', None),
    ]

    cursor.executemany("""
        INSERT INTO vacancies (
            recruiter_id, title, category_code, salary_from, salary_to,
            experience_code, employment_code, description, company_name, city, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, test_vacancies)

    conn.commit()
    conn.close()
    print("База данных успешно инициализирована!")
    print("Тестовые аккаунты:")
    print("  admin / admin123       (администратор)")
    print("  recruiter1 / recruiter123")
    print("  candidate1 / candidate123")


if __name__ == '__main__':
    init_db()

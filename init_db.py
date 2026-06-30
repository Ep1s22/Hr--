import sqlite3


def init_database():
    """Инициализация БД через schema.sql. Для полной настройки используйте update_db.py."""
    connection = sqlite3.connect('database.db')

    with open('schema.sql', 'r', encoding='utf-8') as f:
        connection.executescript(f.read())

    cursor = connection.cursor()

    cursor.executemany("""
        INSERT INTO users (username, email, password_hash, role, full_name, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ('admin', 'admin@work.ru', 'admin123', 'admin', 'Главный Администратор', '+79990000000'),
        ('recruiter1', 'hr@yandex.ru', 'recruiter123', 'recruiter', 'Анна Иванова', '+79991112233'),
        ('candidate1', 'ivan@mail.ru', 'candidate123', 'candidate', 'Иван Петров', '+79995554433'),
    ])

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

    test_vacancies = [
        (2, 'Python/Flask разработчик', 'IT', 90000, 140000, '1-3_years', 'remote',
         'Ищем бэкендера для разработки веб-сервисов.', 'ТехноРешения', 'Москва', None),
        (2, 'Frontend-разработчик (Стажер)', 'IT', 40000, 60000, 'no_experience', 'full-time',
         'Стажировка для начинающих.', 'ВебСтудия', 'Санкт-Петербург', None),
    ]

    cursor.executemany("""
        INSERT INTO vacancies (
            recruiter_id, title, category_code, salary_from, salary_to,
            experience_code, employment_code, description, company_name, city, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, test_vacancies)

    connection.commit()
    connection.close()
    print("База данных успешно создана и заполнена тестовыми данными!")


if __name__ == '__main__':
    init_database()

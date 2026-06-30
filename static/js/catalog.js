let categoryLabels = {};
let experienceLabels = {};
let employmentLabels = {};

// 1. Загрузка фильтров из БД
function loadFilterOptions() {
    fetch('/api/filters')
        .then(response => response.json())
        .then(data => {
            const catSelect = document.getElementById('category-select');
            data.categories.forEach(cat => {
                categoryLabels[cat.code] = cat.name;
                const opt = document.createElement('option');
                opt.value = cat.code;
                opt.textContent = cat.name;
                catSelect.appendChild(opt);
            });

            const expContainer = document.getElementById('experience-container');
            data.experiences.forEach(exp => {
                experienceLabels[exp.code] = exp.name;
                const label = document.createElement('label');
                label.style.cssText = 'display: block; margin-bottom: 5px;';
                label.innerHTML = `<input type="radio" name="experience" value="${exp.code}"> ${exp.name}`;
                expContainer.appendChild(label);
            });

            const empContainer = document.getElementById('employment-container');
            data.employment_types.forEach(emp => {
                employmentLabels[emp.code] = emp.name;
                const label = document.createElement('label');
                label.style.cssText = 'display: block; margin-bottom: 5px;';
                label.innerHTML = `<input type="checkbox" name="employment_type" value="${emp.code}"> ${emp.name}`;
                empContainer.appendChild(label);
            });

            // Запускаем поиск вакансий только после того, как подгрузили все подписи
            loadVacancies();
        })
        .catch(error => console.error('Ошибка загрузки фильтров:', error));
}

// 2. Загрузка вакансий
function loadVacancies() {
    const form = document.getElementById('filter-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const searchParams = new URLSearchParams();
    
    if (formData.get('category')) searchParams.append('category', formData.get('category'));
    if (formData.get('experience')) searchParams.append('experience', formData.get('experience'));
    
    const checkboxes = form.querySelectorAll('input[name="employment_type"]:checked');
    checkboxes.forEach(cb => {
        searchParams.append('employment_type', cb.value);
    });

    const searchInput = document.getElementById('search-input');
    if (searchInput && searchInput.value.trim() !== '') {
        searchParams.append('search', searchInput.value.trim());
    }

    fetch('/api/vacancies?' + searchParams.toString())
        .then(response => response.json())
        .then(vacancies => {
            renderVacancies(vacancies);
        })
        .catch(error => console.error('Ошибка получения вакансий:', error));
}

// 3. Отрисовка резиновых карточек с логотипами
function renderVacancies(vacancies) {
    const container = document.getElementById('vacancies-container');
    if (!container) return;

    if (vacancies.length === 0) {
        container.innerHTML = '<p style="padding: 20px; color: #6c757d;">По вашему запросу вакансий не найдено. Попробуйте создать новую вакансию из кабинета рекрутера.</p>';
        return;
    }
    container.innerHTML = '';

vacancies.forEach(vacancy => {
        let salaryText = vacancy.salary_from ? `от ${vacancy.salary_from.toLocaleString()} ₽` : 'Зарплата не указана';
        if (vacancy.salary_from && vacancy.salary_to) {
            salaryText = `${vacancy.salary_from.toLocaleString()} - ${vacancy.salary_to.toLocaleString()} ₽`;
        }

        const expText = experienceLabels[vacancy.experience_code] || vacancy.experience_code;
        const typeText = employmentLabels[vacancy.employment_code] || vacancy.employment_code;
        const catText = categoryLabels[vacancy.category_code] || vacancy.category_code;

        const card = document.createElement('div');
        card.className = 'vacancy-card';
        // Резиновая карточка
        card.style.cssText = `
            background: #2a2e33; 
            border: 1px solid #2ecc71; 
            border-radius: 8px; 
            padding: 4%; 
            margin-bottom: 15px; 
            box-shadow: 0 2px 4px rgba(102, 92, 92, 0.02);
            display: flex;
            gap: 4%;
            align-items: flex-start;
            width: 100%;
            box-sizing: border-box;
        `;
        
        // Проверяем, есть ли логотип у компании. Если нет — ставим серую заглушку
        const logoUrl = vacancy.image_url ? vacancy.image_url : 'https://placehold.co/100x100?text=No+Logo';

        card.innerHTML = `
            <div style="width: 15%; min-width: 60px;">
                <img src="${logoUrl}" alt="Logo" style="width: 100%; height: auto; border-radius: 6px; object-fit: cover; border: 1px solid #f0f0f0;">
            </div>

            <div style="width: 80%;">
                <h3 style="margin-top: 0; color: #007bff; font-size: 1.3rem;">${vacancy.title}</h3>
                <p style="font-weight: bold; color: #28a745; margin: 5px 0;">${salaryText}</p>
                <p style="margin: 5px 0; color: #6c757d;"><strong>${vacancy.company_name}</strong> · ${vacancy.city}</p>
                <div style="margin: 10px 0; display: flex; flex-wrap: wrap; gap: 5px;">
                    <span style="background: #f8f9fa; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">${expText}</span>
                    <span style="background: #e2e6ea; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">${typeText}</span>
                    <span style="background: #e8f4fd; color: #007bff; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">${catText}</span>
                </div>
                <p style="font-size: 0.95rem; color: #b4b6b8; line-height: 1.4;">${vacancy.description}</p>
                <button style="background: #007bff; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.9rem;">Откликнуться</button>
            </div>
        `;

        // Обработчик отклика
const respondBtn = card.querySelector('button');
        respondBtn.addEventListener('click', () => {
            // Создаем модальное окно динамически с адаптивной версткой в %
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.5); display: flex; align-items: center;
                justify-content: center; z-index: 9999; box-sizing: border-box; padding: 4%;
            `;

            modal.innerHTML = `
                <div style="background: #fff; width: 100%; max-width: 500px; padding: 6%; border-radius: 8px; box-sizing: border-box; position: relative;">
                    <h3 style="margin-top: 0; color: #007bff; margin-bottom: 15px;">Отклик на вакансию</h3>
                    <p style="font-weight: bold; margin-bottom: 15px;">${vacancy.title}</p>
                    
                    <form id="modal-respond-form" enctype="multipart/form-data">
                        <div style="margin-bottom: 15px; width: 100%;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Сопроводительное письмо</label>
                            <textarea name="cover_letter" placeholder="Расскажите о себе..." rows="4" style="width: 100%; box-sizing: border-box; padding: 8px; border-radius: 4px; border: 1px solid #ccc; font-family: inherit;"></textarea>
                        </div>
                        <div style="margin-bottom: 20px; width: 100%;">
                            <label style="display: block; margin-bottom: 5px; font-weight: bold;">Файл резюме (PDF, DOCX, TXT)</label>
                            <input type="file" name="resume_file" accept=".pdf,.docx,.doc,.txt" style="width: 100%; box-sizing: border-box;">
                        </div>
                        <div style="display: flex; gap: 4%; width: 100%;">
                            <button type="submit" style="width: 48%; background: #28a745; color: #fff; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold;">Отправить</button>
                            <button type="button" id="close-modal-btn" style="width: 48%; background: #6c757d; color: #fff; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold;">Отмена</button>
                        </div>
                    </form>
                </div>
            `;

            document.body.appendChild(modal);

            // Кнопка закрытия модалки
            modal.querySelector('#close-modal-btn').addEventListener('click', () => modal.remove());

            // Отправка формы через FormData (чтобы улетел файл!)
            modal.querySelector('#modal-respond-form').addEventListener('submit', (e) => {
                e.preventDefault();
                const mForm = e.target;
                const mFormData = new FormData(mForm);

                fetch(`/api/respond/${vacancy.id}`, {
                    method: 'POST',
                    body: mFormData // Отправляем как FormData, а не JSON!
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.success);
                        modal.remove();
                        respondBtn.innerText = 'Откликнуто';
                        respondBtn.disabled = true;
                        respondBtn.style.background = '#6c757d';
                    } else {
                        alert(data.error);
                    }
                })
                .catch(error => console.error('Ошибка отклика:', error));
            });
        });

        container.appendChild(card);
    });
}

// 4. Инициализация
document.addEventListener('DOMContentLoaded', () => {
    loadFilterOptions();

    const form = document.getElementById('filter-form');
    if (form) {
        form.addEventListener('change', loadVacancies);
    }

    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', loadVacancies);
    }

    const resetBtn = document.getElementById('reset-filters');
    if (resetBtn && form) {
        resetBtn.addEventListener('click', () => {
            form.reset();
            loadVacancies();
        });
    }
});
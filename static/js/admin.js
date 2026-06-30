document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.admin-panel');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            tabButtons.forEach(b => b.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });
});

function deleteUser(userId, username) {
    if (!confirm(`Удалить пользователя «${username}»? Все его вакансии и отклики будут удалены.`)) {
        return;
    }

    fetch(`/admin/api/users/${userId}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error);
            }
        })
        .catch(() => alert('Ошибка связи с сервером'));
}

function changeRole(userId, newRole) {
    fetch(`/admin/api/users/${userId}/role`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.success);
            } else {
                alert(data.error);
                location.reload();
            }
        })
        .catch(() => alert('Ошибка связи с сервером'));
}

function deleteVacancy(vacancyId, title) {
    if (!confirm(`Удалить вакансию «${title}»? Все отклики на неё будут удалены.`)) {
        return;
    }

    fetch(`/admin/api/vacancies/${vacancyId}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error);
            }
        })
        .catch(() => alert('Ошибка связи с сервером'));
}

function updateResponseStatus(responseId, newStatus) {
    fetch(`/admin/api/responses/${responseId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.success);
            } else {
                alert(data.error);
            }
        })
        .catch(() => alert('Ошибка связи с сервером'));
}

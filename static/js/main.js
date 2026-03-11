// ============================================
// AI PLANNER - MAIN JS
// ============================================

document.addEventListener('DOMContentLoaded', function () {

    // ===== SIDEBAR TOGGLE =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });

        document.addEventListener('click', function (e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    // ===== AUTO HIDE MESSAGES =====
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.4s ease';
            setTimeout(function () { alert.remove(); }, 400);
        }, 4000);
    });

    // ===== REFRESH FUNCTIONS =====
    async function refreshTaskPartials() {
        const header = document.getElementById('tasksHeader');
        const list = document.getElementById('tasksList');
        if (!header && !list) return;
        const qs = window.location.search || '';
        try {
            const res = await fetch(`/tasks/partials/${qs}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await res.json();
            if (data.success) {
                if (header) header.innerHTML = data.header_html;
                if (list) list.innerHTML = data.list_html;
            }
        } catch (e) { console.error(e); }
    }

    async function refreshDashboardPartials() {
        const stats = document.getElementById('dashboardStats');
        const today = document.getElementById('dashboardTodayBlock');
        const upcoming = document.getElementById('dashboardUpcoming');
        if (!stats && !today && !upcoming) return;
        try {
            const res = await fetch('/dashboard/partials/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await res.json();
            if (data.success) {
                if (stats) stats.innerHTML = data.stats_html;
                if (today) today.innerHTML = data.today_tasks_html;
                if (upcoming) upcoming.innerHTML = data.upcoming_html;
            }
        } catch (e) { console.error(e); }
    }

    async function refreshGoalListPartials() {
        const list = document.getElementById('goalsListContainer');
        if (!list) return;
        const qs = window.location.search || '';
        try {
            const res = await fetch(`/goals/${qs}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await res.json();
            if (data.success) {
                if (list) list.innerHTML = data.list_html;
            }
        } catch (e) { console.error(e); }
    }

    async function refreshGoalDetailPartials() {
        const tasksList = document.getElementById('goalTasksList');
        const info = document.querySelector('.grid-2 > div:first-child');
        if (!tasksList) return;

        const goalId = window.location.pathname.split('/').filter(p => p).pop();
        if (!goalId || isNaN(goalId)) return;

        try {
            const res = await fetch(`/goals/${goalId}/partials/`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await res.json();
            if (data.success) {
                if (tasksList) tasksList.innerHTML = data.tasks_html;
                if (info) {
                    const infoCard = info.querySelector('.card:first-child');
                    if (infoCard) infoCard.innerHTML = data.info_html;
                }
            }
        } catch (e) { console.error(e); }
    }

    async function refreshAllVisiblePartials() {
        await Promise.all([
            refreshTaskPartials(),
            refreshDashboardPartials(),
            refreshGoalDetailPartials(),
            refreshGoalListPartials()
        ]);
    }

    // ===== MODAL HANDLING =====
    const taskModal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalClose = document.querySelector('.modal-close');

    function openModal(title, url) {
        if (!taskModal) return;
        modalTitle.textContent = title;
        modalBody.innerHTML = '<div style="text-align:center; padding:20px;"><div class="loading-spinner"></div><p>Yuklanmoqda...</p></div>';
        taskModal.classList.add('open');

        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(res => res.text())
            .then(html => {
                modalBody.innerHTML = html;
                const firstInput = modalBody.querySelector('input, select, textarea');
                if (firstInput) firstInput.focus();
            })
            .catch(err => {
                console.error(err);
                modalBody.innerHTML = '<div class="alert alert-danger">Yuklashda xatolik yuz berdi.</div>';
            });
    }

    function closeModal() {
        if (taskModal) taskModal.classList.remove('open');
        setTimeout(() => { if (modalBody) modalBody.innerHTML = ''; }, 300);
    }

    function submitModalForm(form) {
        const formData = new FormData(form);
        const url = form.getAttribute('action') || window.location.pathname;

        fetch(url, {
            method: 'POST', body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken') }
        })
            .then(res => {
                const isJson = res.headers.get('content-type')?.includes('application/json');
                return isJson ? res.json() : res.text();
            })
            .then(async data => {
                console.log('AJAX Response received:', typeof data);
                if (typeof data === 'string') {
                    // This is usually a form with errors (partial HTML)
                    modalBody.innerHTML = data;
                    // Focus first field with error or just first field
                    const firstError = modalBody.querySelector('.form-error');
                    if (firstError) {
                        const input = firstError.parentElement.querySelector('input, select, textarea');
                        if (input) input.focus();
                    }
                    return;
                }
                if (data.success) {
                    showToast(data.message || '✅ Saqlandi', 'success');
                    closeModal();
                    await refreshAllVisiblePartials();
                } else {
                    console.error('Submission failed logic:', data);
                    showToast(data.error || 'Xato yuz berdi', 'danger');
                }
            })
            .catch(err => {
                console.error('AJAX Error:', err);
                showToast('Tarmoq xatosi yoki serverda muammo yuz berdi', 'danger');
            });
    }

    if (modalClose) modalClose.addEventListener('click', closeModal);
    window.addEventListener('click', e => { if (e.target === taskModal) closeModal(); });

    // Global click listener for delegation
    document.addEventListener('click', function (e) {
        // Modal Cancel
        if (e.target.closest('.modal-close-btn, .modal-cancel-btn')) {
            closeModal();
            return;
        }

        // Task Complete
        const completeBtn = e.target.closest('.task-complete-btn');
        if (completeBtn) {
            e.preventDefault();
            const taskId = completeBtn.dataset.taskId;

            // Optimistic UI
            const allBtns = document.querySelectorAll(`.task-complete-btn[data-task-id="${taskId}"]`);
            allBtns.forEach(btn => {
                const it = btn.closest('.task-item');
                if (it) {
                    const ch = it.querySelector('.task-check');
                    const ti = it.querySelector('.task-title');
                    if (ch) { ch.classList.toggle('completed'); ch.innerHTML = ch.classList.contains('completed') ? '✓' : ''; }
                    if (ti) ti.classList.toggle('completed-text');
                }
            });

            fetch(`/tasks/${taskId}/complete/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(res => res.json())
                .then(async data => {
                    if (!data.success) { showToast(data.error || 'Xato', 'danger'); await refreshAllVisiblePartials(); return; }
                    showToast(data.message, 'success');
                    await refreshAllVisiblePartials();
                }).catch(() => { refreshAllVisiblePartials(); });
            return;
        }

        // Task Delete
        const deleteBtn = e.target.closest('.task-delete-btn');
        if (deleteBtn) {
            e.preventDefault();
            if (!confirm("O'chirmoqchimisiz?")) return;
            fetch(`/tasks/${deleteBtn.dataset.taskId}/delete/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            }).then(r => r.json()).then(d => { if (d.success) { showToast(d.message, 'success'); refreshAllVisiblePartials(); } });
            return;
        }

        // Add/Edit Task/Goal
        const tAdd = e.target.closest('.task-add-btn');
        if (tAdd) { e.preventDefault(); let u = '/tasks/create/'; if (tAdd.dataset.goalId) u += `?goal=${tAdd.dataset.goalId}`; openModal('Yangi vazifa', u); return; }

        const tEdit = e.target.closest('.task-edit-btn');
        if (tEdit) { e.preventDefault(); openModal('Vazifani tahrirlash', `/tasks/${tEdit.dataset.taskId}/edit/`); return; }

        const gAdd = e.target.closest('.goal-add-btn');
        if (gAdd) { e.preventDefault(); openModal('Yangi maqsad', '/goals/create/'); return; }

        const gEdit = e.target.closest('.goal-edit-btn');
        if (gEdit) { e.preventDefault(); openModal('Maqsadni tahrirlash', `/goals/${gEdit.dataset.goalId}/edit/`); return; }

        const gDel = e.target.closest('.goal-delete-btn');
        if (gDel) {
            e.preventDefault();
            if (!confirm("Maqsadni o'chirmoqchimisiz?")) return;
            fetch(`/goals/${gDel.dataset.goalId}/delete/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            }).then(r => r.json()).then(d => {
                if (d.success) {
                    showToast(d.message, 'success');
                    if (window.location.pathname.includes('/goals/') && !window.location.pathname.endsWith('/goals/')) {
                        window.location.href = '/goals/';
                    } else {
                        refreshGoalListPartials();
                        refreshDashboardPartials();
                    }
                }
            });
            return;
        }

        // Goal Filter Clear
        const gClr = e.target.closest('.goal-filter-clear');
        if (gClr) { e.preventDefault(); window.history.pushState({}, '', gClr.getAttribute('href')); refreshGoalListPartials(); return; }

        // Filter Clear
        const clr = e.target.closest('.task-filter-clear');
        if (clr) { e.preventDefault(); window.history.pushState({}, '', clr.getAttribute('href')); refreshTaskPartials(); return; }
    });

    // Global submit listener
    document.addEventListener('submit', function (e) {
        // Modal Form
        const mForm = e.target.closest('#taskModal form');
        if (mForm) { e.preventDefault(); submitModalForm(mForm); return; }

        // Goal Filter Form
        const gfForm = e.target.closest('#goalFilterForm');
        if (gfForm) {
            e.preventDefault();
            const params = new URLSearchParams(new FormData(gfForm));
            window.history.pushState({}, '', `${window.location.pathname}?${params.toString()}`);
            refreshGoalListPartials();
            return;
        }

        // Goal Progress Form
        const pForm = e.target.closest('#goalProgressForm');
        if (pForm) {
            e.preventDefault();
            fetch(pForm.getAttribute('action'), {
                method: 'POST', body: new FormData(pForm),
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken') }
            }).then(r => r.json()).then(d => { if (d.success) { showToast(d.message, 'success'); refreshAllVisiblePartials(); } });
        }
    });

    // Delegation for Goal range and input
    document.addEventListener('input', function (e) {
        if (e.target.id === 'progressInput') {
            const disp = document.getElementById('progressValue');
            if (disp) disp.textContent = e.target.value + '%';
        }
    });
    document.addEventListener('change', function (e) {
        if (e.target.id === 'progressInput') {
            const f = e.target.closest('#goalProgressForm');
            if (f) f.dispatchEvent(new Event('submit'));
        }
    });

    // ===== AI CHAT =====
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const adviceTypeSelect = document.getElementById('adviceType');

    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;
            appendMessage('user', message);
            chatInput.value = '';
            const loadingId = appendMessage('ai', '⏳ AI o\'ylayapti...', true);
            const adviceType = adviceTypeSelect ? adviceTypeSelect.value : 'general';

            fetch('/ai/ask/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ message: message, advice_type: adviceType })
            }).then(res => res.json()).then(data => {
                const loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                if (data.success) appendMessage('ai', data.response);
                else appendMessage('ai', '❌ Xato: ' + (data.error || 'Noma\'lum xato'));
            }).catch(() => {
                const loadingEl = document.getElementById(loadingId);
                if (loadingEl) loadingEl.remove();
                appendMessage('ai', '❌ Server bilan bog\'liq xato yuz berdi.');
            });
        });

        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); chatForm.dispatchEvent(new Event('submit')); }
        });
    }

    // ===== HELPERS =====
    function appendMessage(type, content, isLoading = false) {
        if (!chatMessages) return;
        const id = 'msg-' + Date.now();
        const isUser = type === 'user';
        const div = document.createElement('div');
        div.id = id;
        div.className = `chat-message ${type} fade-in ${isLoading ? 'loading' : ''}`;
        div.innerHTML = `
            <div class="message-avatar ${isUser ? 'user-avatar-chat' : 'ai-avatar'}">${isUser ? '👤' : '🤖'}</div>
            <div class="message-bubble">${formatMarkdown(content)}</div>
        `;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function formatMarkdown(text) {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^### (.*)/gm, '<h4>$1</h4>')
            .replace(/^## (.*)/gm, '<h3>$1</h3>')
            .replace(/^# (.*)/gm, '<h2>$1</h2>')
            .replace(/^- (.*)/gm, '<li>$1</li>')
            .replace(/^\d+\. (.*)/gm, '<li>$1</li>')
            .replace(/\n/g, '<br>');
    }

    function showToast(message, type = 'info') {
        const container = document.getElementById('messagesContainer');
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} fade-in`;
        toast.innerHTML = `<span>${message}</span><button class="alert-close" onclick="this.parentElement.remove()">×</button>`;
        if (container) container.appendChild(toast);
        else {
            toast.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;min-width:250px;';
            document.body.appendChild(toast);
        }
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(60px)';
            toast.style.transition = 'all 0.4s ease';
            setTimeout(() => toast.remove(), 400);
        }, 3500);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Global exports
    window.showToast = showToast;
    window.getCookie = getCookie;
    window.refreshAllVisiblePartials = refreshAllVisiblePartials;

});

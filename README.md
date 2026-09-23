# 🎯 AI Planning Pro — Intelligent Life & Goal Management Platform

![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI-Powered](https://img.shields.io/badge/AI-Advisor_Integration-FF6F00?style=for-the-badge&logo=google&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-HTML5_CSS3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

An all-in-one productivity and personal growth management system powered by **Django** and **AI Assistance**, helping users structure their life goals, track habits, organize tasks on a Kanban board, and receive personalized AI action plans.

---

## 🌟 Modules & Features

- **🤖 AI Advisor (`ai_advisor`)**: Smart recommendations and personalized action advice for personal goals.
- **🎯 Goal Tracker (`goals`)**: Long-term goal setting, milestone progress tracking, and target dates.
- **⚡ Habit Tracker (`habits`)**: Daily habit streak monitoring and routine analytics.
- **📋 Kanban Board (`kanban`)**: Interactive drag-and-drop task board for visual project management.
- **📅 Schedule & Planner (`schedule`)**: Calendar integration for daily time-blocking and event scheduling.
- **✅ Task Management (`tasks`)**: Prioritized task list, deadline reminders, and completion status.
- **🔐 User Profiles (`users`)**: Custom user registration, authentication, and personal settings.

---

## 🏗 Modular Architecture

```text
ai-planning-pro/
├── apps/
│   ├── ai_advisor/     # AI prompt orchestration & advice engine
│   ├── goals/          # Milestone & Goal tracking models
│   ├── habits/         # Habit frequency & streak calculations
│   ├── kanban/         # Board columns & task cards
│   ├── schedule/       # Calendar events & daily planner
│   ├── tasks/          # Todo items & priority queues
│   └── users/          # Custom auth & user profiles
├── config/             # Django settings & URL routing
└── templates/          # Responsive UI templates
```

---

## ⚙️ Quick Start

1. **Clone & Navigate:**
   ```bash
   git clone https://github.com/Juravoyev/ai-planning-pro.git
   cd ai-planning-pro
   ```

2. **Environment & Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```

4. **Migrate & Run:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   Access the dashboard at `http://127.0.0.1:8000/`.

---

## 👨‍💻 Author

**Shams Juravoyev**  
- Telegram: [@Juravoyev](https://t.me/Juravoyev)  
- LinkedIn: [Shams Juravoyev](https://www.linkedin.com/in/shams-juravoyev-3017473ab/)  
- GitHub: [@Juravoyev](https://github.com/Juravoyev)  

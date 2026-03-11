#!/bin/bash

# AI Planner - Tez sozlash skripti
echo "🧠 AI Planner sozlanmoqda..."
echo "================================"

# Virtual muhit yaratish
echo "📦 Virtual muhit yaratilmoqda..."
python -m venv venv

# Virtual muhitni faollashtirish
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Bog'liqliklarni o'rnatish
echo "📥 Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt

# .env faylini yaratish
if [ ! -f ".env" ]; then
    echo "⚙️  .env fayli yaratilmoqda..."
    cp .env.example .env
    echo "⚠️  .env faylini oching va API kalitlarini kiriting!"
fi

# Migratsiyalar
echo "🗄️  Ma'lumotlar bazasi sozlanmoqda..."
python manage.py migrate

echo ""
echo "✅ Sozlash tugadi!"
echo "================================"
echo ""
echo "Keyingi qadamlar:"
echo "1. .env faylini oching va OPENAI_API_KEY kiriting"
echo "2. 'python manage.py createsuperuser' buyrug'ini bajaring"
echo "3. 'python manage.py runserver' buyrug'ini bajaring"
echo "4. http://127.0.0.1:8000 ga kiring"
echo ""
echo "🚀 Omad!"

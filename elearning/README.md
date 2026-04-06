# 🚀 Django Project Setup Guide

## 📌 Περιγραφή

Αυτό το project είναι ένα Django web application. Παρακάτω θα βρείτε οδηγίες για τοπική εγκατάσταση και ρύθμιση περιβάλλοντος.

---

## 🛠️ Προαπαιτούμενα

* Python 3.10+
* pip
* virtualenv (προαιρετικά αλλά προτείνεται)
* Git

---

## 📥 Clone το Repository

```bash
git clone https://github.com/cmakionitis/elearning-ice.git
cd elearning
```

---

### Ενεργοποίηση:

* Windows:

```bash
env\Scripts\activate
```

* Linux / Mac:

```bash
source env/bin/activate
```

---

## 📦 Εγκατάσταση Requirements

```bash
pip install -r requirements.txt
```

---

## ⚙️ Ρύθμιση .env αρχείου

Δημιούργησε ένα αρχείο `.env` στη ρίζα του project:

```bash
touch .env
```

ή σε Windows:

```bash
type nul > .env
```

### Παράδειγμα `.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🔐 Φόρτωση Environment Variables

Βεβαιώσου ότι χρησιμοποιείς το package:

```bash
pip install python-dotenv
```

και στο `settings.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"
```

---

## 🗄️ Database Setup

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

---

## 👤 Δημιουργία Superuser

```bash
python manage.py createsuperuser
```

---

## ▶️ Εκκίνηση Server

```bash
python manage.py runserver
```

Το project θα τρέχει στο:
👉 http://127.0.0.1:8000/

---

## 📁 Δομή Project (ενδεικτικά)

```
project/
│── app/
│── project/
│── manage.py
│── requirements.txt
│── .env
```

---

## ✅ Tips

* Μην ανεβάζεις το `.env` στο GitHub (βάλε το στο `.gitignore`)
* Χρησιμοποίησε διαφορετικά env για production
* Πάντα κράτα backup της βάσης

---

## 📜 License

This project is licensed under the MIT License.

---

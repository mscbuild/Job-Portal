# Job-Portal
 ![](https://komarev.com/ghpvc/?username=mscbuild) 
 [![Author](https://img.shields.io/badge/Author-Yuri%20Dev-blue.svg)](http://mscbuild.github.io/)
 ![](https://img.shields.io/github/license/mscbuild/Job-Portal) 
 ![](https://img.shields.io/badge/PRs-Welcome-green)
 ![](https://img.shields.io/github/languages/code-size/mscbuild/Job-Portal)
![](https://img.shields.io/badge/code%20style-python-green)
![](https://img.shields.io/github/stars/mscbuild)
![](https://img.shields.io/badge/Topic-Github-lighred)
![](https://img.shields.io/website?url=https%3A%2F%2Fgithub.com%2Fmscbuild)


A full-fledged system in Python/Flask with basic functionality:

## ✨ Features

- 🔐 Authentication (Flask-Login)
- 🛡 CSRF protection (Flask-WTF)
- 💼 Job posting (employers)
- 📄 Job applications (workers)
- 🔍 Search + filters (salary, category, city)
- 📊 Sorting (salary, date)
- ⭐ Favorites
- 📥 Resume upload + download
- 🔔 Notifications system
- 🎨 Bootstrap UI
- 🧪 Unit tests (pytest) 

## 📁 Project structure

~~~bash
job-portal/
│
├── app.py
├── config.py
├── models.py
├── forms.py
├── extensions.py
│
├── requirements.txt
├── README.md
├── run.py
│
├── resumes/
├── tests/
│   ├── test_auth.py
│   ├── test_jobs.py
│   └── test_applications.py
│
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard_worker.html
    ├── dashboard_employer.html
    ├── upload_resume.html
    ├── applications.html
    └── notifications.html
~~~

## 🔧 1. app.py

## 📄 2. models.py

## 🖼️ HTML-templates

## ▶️ Installation and launch
~~~bash
# Install dependencies
pip install flask flask_sqlalchemy werkzeug

# Start the server
python app.py
~~~
# 📄 License

> MIT License
 

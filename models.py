from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# =========================
# 🏢 EMPLOYER
# =========================
class Employer(db.Model):
    __tablename__ = 'employers'

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    jobs = db.relationship('Job', backref='employer', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# 👷 WORKER
# =========================
class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    resumes = db.relationship('Resume', backref='worker', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# 💼 JOB
# =========================
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))

    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# 📄 RESUME
# =========================
class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text)
    education = db.Column(db.Text)

    file_path = db.Column(db.String(255))

    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

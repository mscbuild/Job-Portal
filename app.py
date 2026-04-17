import os
import secrets
import bleach
import magic
from datetime import datetime

from flask import Flask, render_template, request, redirect, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import or_, desc, asc

from config import Config
from extensions import db, login_manager, csrf
from models import User, Job, Application, Favorite, Notification
from forms import RegisterForm, LoginForm, JobForm, ResumeForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

login_manager.login_view = "login"

os.makedirs("resumes", exist_ok=True)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- AUTH ----------

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# ---------- DASHBOARD ----------

@app.route('/dashboard')
@login_required
def dashboard():
    jobs_query = Job.query

    q = request.args.get('q')
    city = request.args.get('city')
    sort = request.args.get('sort')

    if q:
        jobs_query = jobs_query.filter(Job.title.ilike(f"%{q}%"))
    if city:
        jobs_query = jobs_query.filter(Job.city.ilike(f"%{city}%"))

    if sort == "salary_desc":
        jobs_query = jobs_query.order_by(desc(Job.salary))
    elif sort == "salary_asc":
        jobs_query = jobs_query.order_by(asc(Job.salary))
    elif sort == "newest":
        jobs_query = jobs_query.order_by(desc(Job.created_at))

    jobs = jobs_query.all()
    return render_template("dashboard_worker.html", jobs=jobs)

# ---------- POST JOB ----------

@app.route('/post_job', methods=['POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=bleach.clean(form.description.data),
            salary=form.salary.data,
            category=form.category.data,
            city=form.city.data,
            employer_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()

        # 🔔 notifications
        workers = User.query.filter_by(role='worker').all()
        for w in workers:
            db.session.add(Notification(
                user_id=w.id,
                message=f"New job: {job.title}"
            ))
        db.session.commit()

    return redirect('/dashboard')

# ---------- APPLY ----------

@app.route('/apply/<int:job_id>')
@login_required
def apply(job_id):
    if not Application.query.filter_by(worker_id=current_user.id, job_id=job_id).first():
        db.session.add(Application(worker_id=current_user.id, job_id=job_id))
        db.session.commit()
    return redirect('/dashboard')

# ---------- FAVORITE ----------

@app.route('/favorite/<int:job_id>')
@login_required
def favorite(job_id):
    db.session.add(Favorite(user_id=current_user.id, job_id=job_id))
    db.session.commit()
    return redirect('/dashboard')

# ---------- DOWNLOAD RESUME ----------

@app.route('/download_resume/<int:user_id>')
@login_required
def download_resume(user_id):
    user = User.query.get_or_404(user_id)
    return send_file(user.resume, as_attachment=True)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)

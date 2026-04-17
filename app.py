import os
import secrets
import bleach
import magic

from flask import Flask, render_template, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import CSRFProtect

from models import db, User, Job, Application
from forms import RegisterForm, LoginForm, JobForm, ResumeForm
from sqlalchemy import or_

# ---------------- CONFIG ----------------

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'resumes'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

os.makedirs('resumes', exist_ok=True)

# ---------------- EXTENSIONS ----------------

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------------- DB INIT ----------------

with app.app_context():
    db.create_all()

# ---------------- LOGIN LOADER ----------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- HELPERS ----------------

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            return "User exists"

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

        return "Invalid credentials"

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'employer':
        jobs = Job.query.filter_by(employer_id=current_user.id).all()
        return render_template('dashboard_employer.html', jobs=jobs)

    query = request.args.get('q')

    if query:
        jobs = Job.query.filter(
            or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%")
            )
        ).all()
    else:
        jobs = Job.query.all()

    return render_template('dashboard_worker.html', jobs=jobs)


@app.route('/post_job', methods=['POST'])
@login_required
def post_job():
    if current_user.role != 'employer':
        return "Access denied"

    form = JobForm()

    if form.validate_on_submit():
        clean_desc = bleach.clean(form.description.data)

        job = Job(
            title=form.title.data,
            description=clean_desc,
            employer_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()

    return redirect('/dashboard')


@app.route('/apply/<int:job_id>')
@login_required
def apply(job_id):
    if current_user.role != 'worker':
        return "Access denied"

    existing = Application.query.filter_by(
        worker_id=current_user.id,
        job_id=job_id
    ).first()

    if not existing:
        db.session.add(Application(worker_id=current_user.id, job_id=job_id))
        db.session.commit()

    return redirect('/dashboard')


@app.route('/applications/<int:job_id>')
@login_required
def view_applications(job_id):
    job = Job.query.get_or_404(job_id)

    if job.employer_id != current_user.id:
        return "Access denied"

    apps = Application.query.filter_by(job_id=job_id).all()
    return render_template('applications.html', applications=apps, job=job)


@app.route('/upload_resume', methods=['GET','POST'])
@login_required
def upload_resume():
    if current_user.role != 'worker':
        return "Access denied"

    form = ResumeForm()

    if form.validate_on_submit():
        file = form.resume.data

        if file and allowed_file(file.filename):
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)

            if mime not in [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]:
                return "Invalid file"

            filename = secure_filename(file.filename)
            path = os.path.join('resumes', f"{current_user.id}_{filename}")

            file.save(path)
            current_user.resume = path
            db.session.commit()

            return redirect('/dashboard')

        return "Invalid format"

    return render_template('upload_resume.html', form=form)

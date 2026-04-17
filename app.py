import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from models import db, Employer, Worker, Job, Resume, Application


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# DB config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload config
UPLOAD_FOLDER = 'resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================
# Helpers
# =========================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
# HOME
# =========================
@app.route('/')
def index():
    return render_template('index.html')


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if role == 'employer':
            if Employer.query.filter_by(email=email).first():
                return "Employer already exists"

            user = Employer(company_name=request.form['name'], email=email, password=password)

        else:
            if Worker.query.filter_by(email=email).first():
                return "Worker already exists"

            user = Worker(full_name=request.form['name'], email=email, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Employer.query.filter_by(email=email).first()
        role = 'employer'

        if not user:
            user = Worker.query.filter_by(email=email).first()
            role = 'worker'

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = role
            return redirect('/dashboard')

        return "Incorrect credentials"

    return render_template('login.html')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================
# DASHBOARD
# =========================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] == 'employer':
        jobs = Job.query.filter_by(employer_id=session['user_id']).all()
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


# =========================
# POST JOB (EMPLOYER)
# =========================
@app.route('/post_job', methods=['POST'])
def post_job():
    if 'user_id' not in session or session['role'] != 'employer':
        return redirect('/login')

    job = Job(
        title=request.form['title'],
        description=request.form['description'],
        employer_id=session['user_id']
    )

    db.session.add(job)
    db.session.commit()

    return redirect('/dashboard')


# =========================
# APPLY JOB (WORKER)
# =========================
@app.route('/apply/<int:job_id>')
def apply(job_id):
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')

    existing = Application.query.filter_by(
        worker_id=session['user_id'],
        job_id=job_id
    ).first()

    if not existing:
        db.session.add(Application(
            worker_id=session['user_id'],
            job_id=job_id
        ))
        db.session.commit()

    return redirect('/dashboard')


# =========================
# VIEW APPLICATIONS (EMPLOYER)
# =========================
@app.route('/applications/<int:job_id>')
def view_applications(job_id):
    if 'user_id' not in session or session['role'] != 'employer':
        return redirect('/login')

    job = Job.query.get_or_404(job_id)

    if job.employer_id != session['user_id']:
        return "Access Denied"

    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template('applications.html', applications=applications, job=job)


# =========================
# UPLOAD RESUME (WORKER)
# =========================
@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')

    if request.method == 'POST':
        file = request.files.get('resume')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                f"{session['user_id']}_{filename}"
            )

            file.save(filepath)

            resume = Resume(
                title="My Resume",
                skills="",
                experience="",
                education="",
                file_path=filepath,
                worker_id=session['user_id']
            )

            db.session.add(resume)
            db.session.commit()

            return redirect('/dashboard')

        return "Invalid file type"

    return render_template('upload_resume.html')


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)

import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Job, Application
from sqlalchemy import or_

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            return "The user already exists"

        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect('/dashboard')
        else:
            return 'Incorrect data'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] == 'employer':
        jobs = Job.query.filter_by(employer_id=session['user_id']).all()
        return render_template('dashboard_employer.html', jobs=jobs)
    else:
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
def post_job():
    if 'user_id' not in session or session['role'] != 'employer':
        return redirect('/login')

    title = request.form['title']
    description = request.form['description']

    job = Job(title=title, description=description, employer_id=session['user_id'])
    db.session.add(job)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/apply/<int:job_id>')
def apply(job_id):
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')

    existing = Application.query.filter_by(worker_id=session['user_id'], job_id=job_id).first()
    if not existing:
        application = Application(worker_id=session['user_id'], job_id=job_id)
        db.session.add(application)
        db.session.commit()
    return redirect('/dashboard')

@app.route('/applications/<int:job_id>')
def view_applications(job_id):
    if 'user_id' not in session or session['role'] != 'employer':
        return redirect('/login')

    job = Job.query.get_or_404(job_id)

    if job.employer_id != session['user_id']:
        return "Access Denied"

    applications = Application.query.filter_by(job_id=job_id).all()
    return render_template('applications.html', applications=applications, job=job)

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        file = request.files.get('resume')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{user.id}_{filename}")
            file.save(filepath)
            user.resume = filepath
            db.session.commit()
            return redirect('/dashboard')
        else:
            return "Unsupported file format"

    return render_template('upload_resume.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
 
 
    
 

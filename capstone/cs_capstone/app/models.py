from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_employer = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs_posted = db.relationship('Job', backref='poster', lazy='dynamic')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    jobs = db.relationship('Job', backref='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(120))
    salary_range = db.Column(db.String(100))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    is_remote = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic')
    skills = db.relationship('Skill', secondary='job_skills', backref=db.backref('jobs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company.name}>'

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='applied')  # applied, reviewed, interviewed, offered, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    
    def __repr__(self):
        return f'<Application {self.id} for Job {self.job_id} by User {self.user_id}>'

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)
    
    def __repr__(self):
        return f'<Skill {self.name}>'

# Association table for many-to-many relationship between Job and Skill
job_skills = db.Table('job_skills',
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

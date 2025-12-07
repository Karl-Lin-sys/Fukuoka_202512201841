from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=120)])
    salary_range = StringField('Salary Range (e.g., $50,000 - $70,000)', 
                             validators=[Length(max=100)])
    job_type = SelectField('Job Type', 
                         choices=[
                             ('full-time', 'Full-time'),
                             ('part-time', 'Part-time'),
                             ('contract', 'Contract'),
                             ('temporary', 'Temporary'),
                             ('internship', 'Internship'),
                             ('freelance', 'Freelance')
                         ], 
                         validators=[DataRequired()])
    is_remote = BooleanField('This is a remote position')
    skills = StringField('Required Skills (comma separated)', 
                        validators=[Optional()])
    submit = SubmitField('Post Job')

class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', 
                               validators=[DataRequired(), Length(min=50, max=2000)])
    resume = FileField('Resume (PDF, DOC, DOCX)', 
                      validators=[FileRequired(), FileAllowed(['pdf', 'doc', 'docx'], 
                                                           'Only PDF, DOC and DOCX files are allowed')])
    submit = SubmitField('Submit Application')

class JobSearchForm(FlaskForm):
    q = StringField('Keywords', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    job_type = SelectField('Job Type', 
                         choices=[
                             ('', 'Any'),
                             ('full-time', 'Full-time'),
                             ('part-time', 'Part-time'),
                             ('contract', 'Contract'),
                             ('temporary', 'Temporary'),
                             ('internship', 'Internship'),
                             ('freelance', 'Freelance')
                         ], 
                         validators=[Optional()])
    submit = SubmitField('Search')

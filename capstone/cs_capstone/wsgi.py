from app import create_app, db
from app.models import User, Job, Company, Application, Skill

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Job': Job, 
        'Company': Company, 
        'Application': Application,
        'Skill': Skill
    }

if __name__ == '__main__':
    app.run(debug=True)

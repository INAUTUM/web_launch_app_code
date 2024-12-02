from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20), nullable=False)
    code = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Task {self.id}: {self.language}>"
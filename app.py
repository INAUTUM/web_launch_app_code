from flask import Flask, request, jsonify, render_template, redirect, url_for
from database import db, Task
import subprocess
import tempfile
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Создание базы данных при старте
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    language = request.form['language']
    code = request.form['code']
    task = Task(language=language, code=code)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/run_task/<int:task_id>', methods=['POST'])
def run_task(task_id):
    task = Task.query.get(task_id)
    
    if task:
        if task.language == 'python':
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as py_file:
                py_file.write(task.code.encode())
                py_file_path = py_file.name
            command = f"python3 {py_file_path}"
        elif task.language == 'cpp':
            with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as cpp_file:
                cpp_file.write(task.code.encode())
                cpp_file_path = cpp_file.name
            command = f"g++ {cpp_file_path} -o {cpp_file_path.replace('.cpp', '')} && {cpp_file_path.replace('.cpp', '')}"
        
        try:
            execution_result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = execution_result.stdout
            error = execution_result.stderr
        finally:
            # Удаление временных файлов
            if task.language == 'python':
                os.remove(py_file_path)
            elif task.language == 'cpp':
                os.remove(cpp_file_path)
                os.remove(cpp_file_path.replace('.cpp', ''))
                
        return jsonify({'output': output, 'error': error})

    return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
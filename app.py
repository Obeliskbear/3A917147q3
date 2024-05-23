import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'mydb.db')

def connect_db():
    return sqlite3.connect(DB_FILE)

@app.route('/')
def index():
    if 'idno' not in session:
        return redirect(url_for('login'))
    else:
        try:
            conn = connect_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM member WHERE idno = ?", (session['idno'],))
            user = cursor.fetchone()
            conn.close()
            return render_template('index.html', user=user)
        except Exception as e:
            with open('error.log', 'a') as f:
                f.write(str(e) + '\n')
            return render_template('error.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        idno = request.form['idno']
        pwd = request.form['pwd']
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM member WHERE idno = ? AND pwd = ?", (idno, pwd))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['idno'] = idno
                return redirect(url_for('index'))
            else:
                error = "請輸入正確的帳號密碼"
                return render_template('login.html', error=error)
        except Exception as e:
            with open('error.log', 'a') as f:
                f.write(str(e) + '\n')
            return render_template('error.html')
    else:
        return render_template('login.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'idno' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE member SET nm=?, birth=?, blood=?, phone=?, email=? WHERE idno=?",
                               (request.form['nm'], request.form['birth'], request.form['blood'],
                                request.form['phone'], request.form['email'], session['idno']))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            except Exception as e:
                with open('error.log', 'a') as f:
                    f.write(str(e) + '\n')
                return render_template('error.html')
        else:
            try:
                conn = connect_db()
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM member WHERE idno = ?", (session['idno'],))
                user = cursor.fetchone()
                conn.close()
                return render_template('edit.html', user=user)
            except Exception as e:
                with open('error.log', 'a') as f:
                    f.write(str(e) + '\n')
                return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop('idno', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

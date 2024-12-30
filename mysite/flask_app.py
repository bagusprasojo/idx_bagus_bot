from flask import Flask, render_template, session, redirect, url_for  
from auth import auth_bp  # Import blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Untuk sesi, pastikan mengganti dengan key yang lebih aman

# Mendaftarkan blueprint untuk autentikasi
app.register_blueprint(auth_bp)

# Dekorator untuk memeriksa apakah pengguna sudah login
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))  # Redirect ke halaman login jika belum login
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def homepage():
    username = session.get('username')
    return render_template('index.html', username=username)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/daftar_pengakses')
@login_required
def daftar_pengakses():
    return render_template('daftar_pengakses.html')

@app.route('/daftar_berita')
@login_required
def daftar_berita():
    return render_template('daftar_berita.html')

@app.route('/keterbukaan_informasi')
@login_required
def keterbukaan_informasi():
    return render_template('keterbukaan_informasi.html')

if __name__ == '__main__':
    app.run(debug=True)

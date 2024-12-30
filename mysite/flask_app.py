from flask import Flask, render_template, session, redirect, url_for  
from auth import auth_bp  # Import blueprint
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Untuk sesi, pastikan mengganti dengan key yang lebih aman

# Mendaftarkan blueprint untuk autentikasi
app.register_blueprint(auth_bp)

# Koneksi ke database MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

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
    # Koneksi ke database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Menggunakan dictionary agar hasil query mudah dipakai
    
    # Query untuk mengambil 10 data terakhir
    cursor.execute("""
        select a.user_telegram_id, a.user_telegram_username, a.tgl_akses, a.menu from tb_akses a
        ORDER BY a.tgl_akses desc limit 20
    """)
    
    # Ambil hasil query
    aksess = cursor.fetchall()
    
    # Tutup koneksi database
    cursor.close()
    conn.close()

    return render_template('daftar_pengakses.html', aksess=aksess)

@app.route('/daftar_berita')
@login_required
def daftar_berita():
    # Koneksi ke database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Menggunakan dictionary agar hasil query mudah dipakai
    
    # Query untuk mengambil 10 data terakhir
    cursor.execute("""
        SELECT kode_emiten, tanggal, id FROM tb_news 
        ORDER BY tanggal DESC, id desc LIMIT 20
    """)
    
    # Ambil hasil query
    berita = cursor.fetchall()
    
    # Tutup koneksi database
    cursor.close()
    conn.close()

    return render_template('daftar_berita.html', beritas=berita)

@app.route('/keterbukaan_informasi')
@login_required
def keterbukaan_informasi():
    return render_template('keterbukaan_informasi.html')

if __name__ == '__main__':
    app.run(debug=True)

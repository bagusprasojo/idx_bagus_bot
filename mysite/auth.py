from flask import Blueprint, render_template, request, redirect, url_for, session

# Membuat blueprint untuk autentikasi
auth_bp = Blueprint('auth', __name__)

# Contoh data pengguna (bisa diganti dengan data dari database)
users = {
    "admin": "admin",  # username: password
}

# Route untuk halaman login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Cek apakah username dan password valid
        if username in users and users[username] == password:
            session['username'] = username  # Simpan username di session
            return redirect(url_for('homepage'))  # Redirect ke homepage setelah login berhasil
        else:
            return "Login Gagal! Username atau Password salah."

    return render_template('login.html')  # Jika GET, tampilkan halaman login

# Route untuk logout
@auth_bp.route('/logout')
def logout():
    session.pop('username', None)  # Hapus session
    return redirect(url_for('homepage'))  # Redirect ke homepage setelah logout

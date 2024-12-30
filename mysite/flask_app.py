from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/daftar_pengakses')
def daftar_pengakses():
    return render_template('daftar_pengakses.html')

@app.route('/daftar_berita')
def daftar_berita():
    return render_template('daftar_berita.html')

@app.route('/keterbukaan_informasi')
def keterbukaan_informasi():
    return render_template('keterbukaan_informasi.html')

if __name__ == '__main__':
    app.run(debug=True)

# api.py
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

# Membuat blueprint untuk API
api_bp = Blueprint('api', __name__)

# Inisialisasi SQLAlchemy
db = SQLAlchemy()

# Model
class TipeEnum(Enum):
    keterbukaan = "keterbukaan"
    pengumuman = "pengumuman"
    


class Pengumuman(db.Model):
    __tablename__ = 'tb_pengumuman'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode_emiten = db.Column(db.String(50), nullable=False)
    no_pengumuman = db.Column(db.String(255), nullable=True)
    tgl_pengumuman = db.Column(db.DateTime, nullable=True)
    judul_pengumuman = db.Column(db.Text, nullable=True)
    jenis_pengumuman = db.Column(db.String(255), nullable=True)
    perihal_pengumuman = db.Column(db.String(255), nullable=True)
    tipe = db.Column(db.Enum(TipeEnum), nullable=False)

class Pengumuman_Attachment(db.Model):
    __tablename__ = 'tb_pengumuman_attachment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pdf = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    original_name = db.Column(db.String(255), nullable=True)

    id_pengumuman = db.Column(db.Integer, db.ForeignKey('tb_pengumuman.id'), nullable=False)

class News(db.Model):
    __tablename__ = 'tb_news'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode_emiten = db.Column(db.String(50), nullable=False)
    tanggal = db.Column(db.DateTime, nullable=False)

class News_Detail(db.Model):
    __tablename__ = 'tb_news_detail'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    snippet = db.Column(db.Text, nullable=True)

    tb_news_id = db.Column(db.Integer, db.ForeignKey('tb_news.id'), nullable=False)


class Profile(db.Model):
    __tablename__ = 'tb_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode_emiten = db.Column(db.String(50), nullable=False)
    nama_emiten = db.Column(db.String(255), nullable=False)
    alamat = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    sektor = db.Column(db.String(100), nullable=True)
    sub_sektor = db.Column(db.String(100), nullable=True)
    telepon = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(255), nullable=True)

# Model untuk tabel Sekretaris
class Sekretaris(db.Model):
    __tablename__ = 'tb_sekretaris'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(255), nullable=False)
    telepon = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    hp = db.Column(db.String(50), nullable=True)
    fax = db.Column(db.String(50), nullable=True)

    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

# Endpoint untuk memproses JSON
@api_bp.route('/process-json', methods=['POST'])
def process_json():
    try:
        # Mendapatkan data JSON dari request
        data = request.get_json()

        # Memproses data Profiles
        profiles = data.get('Profiles', [])
        for profile_data in profiles:
            profile = Profile.query.filter_by(kode_emiten=profile_data['KodeEmiten']).first()

            if profile:
                profile.nama_emiten = profile_data['NamaEmiten']
                profile.alamat = profile_data.get('Alamat')
                profile.email = profile_data.get('Email')
                profile.sektor = profile_data.get('Sektor')
                profile.sub_sektor = profile_data.get('SubIndustri')
                profile.telepon = profile_data.get('Telepon')
                profile.website = profile_data.get('Website')
            else:
                profile = Profile(
                    kode_emiten=profile_data['KodeEmiten'],
                    nama_emiten=profile_data['NamaEmiten'],
                    alamat=profile_data.get('Alamat'),
                    email=profile_data.get('Email'),
                    sektor=profile_data.get('Sektor'),
                    sub_sektor=profile_data.get('SubIndustri'),
                    telepon=profile_data.get('Telepon'),
                    website=profile_data.get('Website')
                )

            db.session.add(profile)
            db.session.flush()

            Sekretaris.query.filter_by(id_profile=profile.id).delete()

        # Memproses data Sekretaris
        sekretaris_list = data.get('Sekretaris', [])
        for sekretaris_data in sekretaris_list:
            sekretaris = Sekretaris(
                nama=sekretaris_data['Nama'],
                telepon=sekretaris_data.get('Telepon'),
                email=sekretaris_data.get('Email'),
                hp=sekretaris_data.get('HP'),
                fax=sekretaris_data.get('Fax'),
                id_profile = profile.id
            )
            db.session.add(sekretaris)

        # Menyimpan perubahan ke database
        db.session.commit()

        return jsonify({"message": "Data processed and saved successfully"}), 201

    except Exception as e:
        # Jika terjadi kesalahan, rollback perubahan
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

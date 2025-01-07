# api.py
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from sqlalchemy.inspection import inspect

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
@api_bp.route('/process-json-profile', methods=['POST'])
def process_json_profile():
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


@api_bp.route('/process-json-keterbukaan', methods=['POST'])
def process_json_keterbukaan():
    try:
        # Mendapatkan data JSON dari request
        data = request.get_json()

        # Memproses data Profiles
        replies = data.get('Replies', [])
        for reply_data in replies:
            pengumuman_data = reply_data['pengumuman']
            
            pengumuman = Pengumuman.query.filter(
                Pengumuman.kode_emiten == pengumuman_data['Kode_Emiten'].strip(),
                Pengumuman.no_pengumuman == pengumuman_data['NoPengumuman'].strip()
            ).first()
            
            print(pengumuman)

            if pengumuman:                
                pengumuman.kode_emiten = pengumuman_data['Kode_Emiten'].strip()
                pengumuman.no_pengumuman = pengumuman_data['NoPengumuman'].strip()
                pengumuman.tgl_pengumuman = pengumuman_data['TglPengumuman']
                pengumuman.judul_pengumuman = pengumuman_data['JudulPengumuman'].strip()
                pengumuman.jenis_pengumuman = pengumuman_data['JenisPengumuman'].strip()
                pengumuman.perihal_pengumuman = pengumuman_data['PerihalPengumuman'].strip()
                pengumuman.tipe = 'keterbukaan'                
            else:                
                pengumuman = Pengumuman(
                    kode_emiten = pengumuman_data['Kode_Emiten'].strip(),
                    no_pengumuman = pengumuman_data['NoPengumuman'].strip(),
                    tgl_pengumuman = pengumuman_data['TglPengumuman'],
                    judul_pengumuman = pengumuman_data['JudulPengumuman'].strip(),
                    jenis_pengumuman = pengumuman_data['JenisPengumuman'].strip(),
                    perihal_pengumuman = pengumuman_data['PerihalPengumuman'].strip(),
                    tipe= 'keterbukaan'
                )

                db.session.add(pengumuman)

            # Panggil fungsi commit untuk menyimpan perubahan
            db.session.flush()
            Pengumuman_Attachment.query.filter_by(id_pengumuman=pengumuman.id).delete()

            attachments_data = reply_data['attachments']
            for item in attachments_data:
                attachment = Pengumuman_Attachment(
                    pdf = item['PDFFilename'].strip(),
                    url = item['FullSavePath'].strip(),
                    original_name = item['OriginalFilename'].strip(),
                    id_pengumuman = pengumuman.id
                )

                db.session.add(attachment)


        db.session.commit()


        return jsonify({"message": "Data processed and saved successfully"}), 201

    except Exception as e:
        # Jika terjadi kesalahan, rollback perubahan
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

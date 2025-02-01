# api.py
from datetime import datetime
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
    fax = db.Column(db.String(60), nullable=True)
    sektor = db.Column(db.String(100), nullable=True)
    sub_sektor = db.Column(db.String(100), nullable=True)
    telepon = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    industri = db.Column(db.String(100), nullable=True)
    sub_industri = db.Column(db.String(100), nullable=True)
    kegiatan_usaha_utama=db.Column(db.Text, nullable=True)


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

class Direktur(db.Model):
    __tablename__ = 'tb_direktur'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(255), nullable=False)
    jabatan = db.Column(db.String(255), nullable=True)
    afiliasi = db.Column(db.String(255), nullable=True)
    
    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

class Komisaris(db.Model):
    __tablename__ = 'tb_komisaris'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(255), nullable=False)
    jabatan = db.Column(db.String(255), nullable=True)
    independen = db.Column(db.String(255), nullable=True)
    
    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

class KomiteAudit(db.Model):
    __tablename__ = 'tb_komite_audit'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(255), nullable=False)
    jabatan = db.Column(db.String(255), nullable=True)
    
    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

class PemegangSaham(db.Model):
    __tablename__ = 'tb_pemegang_saham'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jumlah = db.Column(db.Integer, nullable=True)
    kategori = db.Column(db.String(50), nullable=True)    
    nama = db.Column(db.String(255), nullable=True)
    pengendali = db.Column(db.String(50), nullable=True)
    # persentase = db.Column(db.Double(255), nullable=True)
    persentase = db.Column(db.Numeric(precision=10, scale=2))
    
    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

class AnakPerusahaan(db.Model):
    __tablename__ = 'tb_anak_perusahaan'

    id = db.Column(db.Integer, primary_key=True)
    bidang_usaha = db.Column(db.String(100), nullable=False)
    jumlah_aset = db.Column(db.Numeric(precision=15, scale=2), nullable=False)  # Precision 15 dan scale 2 untuk angka desimal
    lokasi = db.Column(db.String(100), nullable=False)
    mata_uang = db.Column(db.String(10), nullable=False)
    nama = db.Column(db.String(255), nullable=False)
    persentase = db.Column(db.Numeric(precision=5, scale=2), nullable=False)  # Persentase, biasanya 0-100
    satuan = db.Column(db.String(50), nullable=False)
    status_operasi = db.Column(db.String(50), nullable=True)
    tahun_komersil = db.Column(db.String(4), nullable=False)

    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

class Dividen(db.Model):
    __tablename__ = 'tb_dividen'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    jenis = db.Column(db.String(50), nullable=False)
    tahun_buku = db.Column(db.String(4), nullable=False)  # Tahun buku disimpan sebagai string
    total_saham_bonus = db.Column(db.Numeric(precision=15, scale=2), nullable=False, default=0.0)  # Saham bonus
    cash_dividen_per_saham_mu = db.Column(db.String(10), nullable=True)  # Mata uang cash dividen per saham
    cash_dividen_per_saham = db.Column(db.Numeric(precision=15, scale=2), nullable=False, default=0.0)  # Cash dividen per saham
    tanggal_cum = db.Column(db.DateTime, nullable=False)
    tanggal_ex_reguler_dan_negosiasi = db.Column(db.DateTime, nullable=False)
    tanggal_dps = db.Column(db.DateTime, nullable=False)
    tanggal_pembayaran = db.Column(db.DateTime, nullable=False)
    rasio1 = db.Column(db.Numeric(precision=5, scale=2), nullable=False, default=0.0)  # Rasio 1
    rasio2 = db.Column(db.Numeric(precision=5, scale=2), nullable=False, default=0.0)  # Rasio 2
    cash_dividen_total_mu = db.Column(db.String(10), nullable=True)  # Mata uang total cash dividen
    cash_dividen_total = db.Column(db.Numeric(precision=18, scale=2), nullable=False, default=0.0)  # Total cash dividen

    id_profile = db.Column(db.Integer, db.ForeignKey('tb_profiles.id'), nullable=False)

# Endpoint untuk memproses JSON
def process_json_profile_sekretaris(data, id_profile):

    print(f"proses sekretaris id_profile: {id_profile}")
    Sekretaris.query.filter_by(id_profile=id_profile).delete()

    # Memproses data Sekretaris
    sekretaris_list = data.get('Sekretaris', [])
    for sekretaris_data in sekretaris_list:
        sekretaris = Sekretaris(
            nama=sekretaris_data['Nama'],
            telepon=sekretaris_data.get('Telepon'),
            email=sekretaris_data.get('Email'),
            hp=sekretaris_data.get('HP'),
            fax=sekretaris_data.get('Fax'),
            id_profile = id_profile
        )
        db.session.add(sekretaris)

def process_json_profile_direktur(data, id_profile):

    print(f"proses direktur id_profile: {id_profile}")
    Direktur.query.filter_by(id_profile=id_profile).delete()

    # Memproses data Sekretaris
    direktur_list = data.get('Direktur', [])
    for direktur_data in direktur_list:
        direktur = Direktur(
            nama=direktur_data['Nama'],
            jabatan=direktur_data.get('Jabatan'),
            afiliasi=direktur_data.get('Afiliasi'),
            id_profile = id_profile
        )
        db.session.add(direktur)

def process_json_profile_komisaris(data, id_profile):

    print(f"proses komisaris id_profile: {id_profile}")
    Komisaris.query.filter_by(id_profile=id_profile).delete()

    # Memproses data komisaris
    komisaris_list = data.get('Komisaris', [])
    for komisaris_data in komisaris_list:
        komisaris = Komisaris(
            nama=komisaris_data['Nama'],
            jabatan=komisaris_data.get('Jabatan'),
            independen=komisaris_data.get('Independen'),
            id_profile = id_profile
        )
        db.session.add(komisaris)

def process_json_profile_komite_audit(data, id_profile):

    print(f"proses komite audit id_profile: {id_profile}")
    KomiteAudit.query.filter_by(id_profile=id_profile).delete()

    # Memproses data komisaris
    komite_audit_list = data.get('KomiteAudit', [])
    for komite_audit_data in komite_audit_list:
        komite_audit = KomiteAudit(
            nama=komite_audit_data['Nama'],
            jabatan=komite_audit_data.get('Jabatan'),
            id_profile = id_profile
        )
        db.session.add(komite_audit)

def process_json_profile_pemegang_saham(data, id_profile):

    PemegangSaham.query.filter_by(id_profile=id_profile).delete()

    pemegang_saham_list = data.get('PemegangSaham', [])
    for pemegang_saham_data in pemegang_saham_list:
        
        pemegang_saham = PemegangSaham(
            jumlah = int(pemegang_saham_data['Jumlah']),
            kategori=pemegang_saham_data['Kategori'],
            nama=pemegang_saham_data['Nama'],
            pengendali=pemegang_saham_data.get('Pengendali'),
            persentase=pemegang_saham_data.get('Persentase'),
            id_profile = id_profile
        )

        db.session.add(pemegang_saham)

def process_json_profile_anak_perusahaan(data, id_profile):
    AnakPerusahaan.query.filter_by(id_profile=id_profile).delete()
    anak_perusahaan_list = data.get('AnakPerusahaan', [])
    
    for anak_perusahaan_data in anak_perusahaan_list:
        
        anak_perusahaan = AnakPerusahaan(
            bidang_usaha=anak_perusahaan_data['BidangUsaha'],
            jumlah_aset=anak_perusahaan_data['JumlahAset'],
            lokasi=anak_perusahaan_data['Lokasi'],
            mata_uang=anak_perusahaan_data['MataUang'],
            nama=anak_perusahaan_data['Nama'],
            persentase=anak_perusahaan_data['Persentase'],
            satuan=anak_perusahaan_data['Satuan'],
            status_operasi=anak_perusahaan_data.get('StatusOperasi', ''),
            tahun_komersil=anak_perusahaan_data.get('TahunKomersil', '0'),
            id_profile=id_profile  # Menyimpan relasi dengan profile
        )

        db.session.add(anak_perusahaan)

def process_json_profile_dividen(data, id_profile):
    Dividen.query.filter_by(id_profile=id_profile).delete()

    dividen_list = data.get('Dividen', [])
    
    # Loop untuk memproses setiap data dividen
    for dividen_data in dividen_list:

        tanggal_invalid = datetime(1900, 1, 1)
        tanggal_dps = datetime.strptime(dividen_data['TanggalDPS'], '%Y-%m-%dT%H:%M:%S')
        if tanggal_dps == tanggal_invalid:
            tanggal_dps = None  # Set NULL di database

        tanggal_cum=datetime.strptime(dividen_data['TanggalCum'], '%Y-%m-%dT%H:%M:%S')
        if tanggal_cum == tanggal_invalid:
            tanggal_cum = None

        tanggal_ex_reguler_dan_negosiasi=datetime.strptime(dividen_data['TanggalExRegulerDanNegosiasi'], '%Y-%m-%dT%H:%M:%S')
        if tanggal_ex_reguler_dan_negosiasi == tanggal_invalid:
            tanggal_ex_reguler_dan_negosiasi = None

        tanggal_pembayaran=datetime.strptime(dividen_data['TanggalPembayaran'], '%Y-%m-%dT%H:%M:%S')
        if tanggal_pembayaran == tanggal_invalid:
            tanggal_pembayaran = None


        
        dividen = Dividen(
            nama=dividen_data['Nama'],
            jenis=dividen_data['Jenis'],
            tahun_buku=dividen_data['TahunBuku'],
            total_saham_bonus=dividen_data.get('TotalSahamBonus', 0.0),
            cash_dividen_per_saham_mu=dividen_data.get('CashDividenPerSahamMU', ''),
            cash_dividen_per_saham=dividen_data.get('CashDividenPerSaham', 0.0),
            tanggal_cum=tanggal_cum,
            tanggal_ex_reguler_dan_negosiasi=tanggal_ex_reguler_dan_negosiasi,
            tanggal_dps=tanggal_dps,
            tanggal_pembayaran=tanggal_pembayaran,
            rasio1=dividen_data.get('Rasio1', 0),
            rasio2=dividen_data.get('Rasio2', 0),
            cash_dividen_total_mu=dividen_data.get('CashDividenTotalMU', ''),
            cash_dividen_total=dividen_data.get('CashDividenTotal', 0.0),
            id_profile=id_profile  # Menyimpan relasi dengan profile
        )

        # Menambahkan objek dividen ke dalam session
        db.session.add(dividen)
    


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
                profile.fax = profile_data.get('Fax')
                profile.industri = profile_data.get('Industri')
                profile.sub_industri = profile_data.get('SubIndustri')
                profile.kegiatan_usaha_utama = profile_data.get('KegiatanUsahaUtama')
            else:
                profile = Profile(
                    kode_emiten=profile_data['KodeEmiten'],
                    nama_emiten=profile_data['NamaEmiten'],
                    alamat=profile_data.get('Alamat'),
                    email=profile_data.get('Email'),
                    sektor=profile_data.get('Sektor'),
                    sub_sektor=profile_data.get('SubIndustri'),
                    telepon=profile_data.get('Telepon'),
                    website=profile_data.get('Website'),
                    fax = profile_data.get('Fax'),
                    industri = profile_data.get('Industri'),
                    sub_industri = profile_data.get('SubIndustri'),
                    kegiatan_usaha_utama = profile_data.get('KegiatanUsahaUtama')
                )

                db.session.add(profile)

            db.session.flush()
            process_json_profile_sekretaris(data, profile.id)
            process_json_profile_direktur(data, profile.id)
            process_json_profile_komisaris(data, profile.id)
            process_json_profile_komite_audit(data, profile.id)
            process_json_profile_pemegang_saham(data, profile.id)
            process_json_profile_anak_perusahaan(data, profile.id)
            process_json_profile_dividen(data, profile.id)

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

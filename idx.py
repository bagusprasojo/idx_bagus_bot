import mysql.connector
from dotenv import load_dotenv
from googleapiclient.discovery import build
import webbrowser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder, ContextTypes, CallbackQueryHandler, CallbackContext

import json
import os
import sys
import requests
import time
from datetime import datetime, date

load_dotenv()

TOKEN = os.getenv("TOKEN")
api_key = os.getenv("api_key")
cx_key = os.getenv("cx_key")

host_ = os.getenv("host")
user_ = os.getenv("user")
password_ = os.getenv("password")
database_ = os.getenv("database")

if not TOKEN or not api_key or not cx_key:
    print("Error: Missing API Key or Token in environment variables.")
    sys.exit(1)


# Setup koneksi ke database MySQL
def get_db_connection():
    return mysql.connector.connect(
        host= host_,
        user= user_,
        password=password_,
        database=database_
    )

# Fungsi untuk mengecek apakah kode_emiten dan tanggal sudah ada di tb_news
def check_news_exists(kode_emiten):
    print(f'check_news_exists({kode_emiten})')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    cursor.execute("SELECT * FROM tb_news WHERE kode_emiten = %s AND tanggal = %s", (kode_emiten, today))
    result = cursor.fetchone()
    conn.close()
    return result

# Fungsi untuk menyimpan berita ke dalam tb_news dan tb_news_detail
def save_news(kode_emiten, hasil):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 

    # Simpan ke tb_news
    today = date.today()
    cursor.execute(
        "INSERT INTO tb_news (kode_emiten, tanggal) VALUES (%s, %s) ON DUPLICATE KEY UPDATE tanggal = %s",
        (kode_emiten, today, today)
    )
    conn.commit()

    # Ambil ID dari berita yang baru saja disimpan
    cursor.execute("SELECT id FROM tb_news WHERE kode_emiten = %s AND tanggal = %s", (kode_emiten, today))
    news_id = cursor.fetchone()['id']

    # Simpan hasil pencarian ke tb_news_detail
    for item in hasil:
        title = item['title']
        link = item['link']
        snippet = item['snippet']
        cursor.execute(
            "INSERT INTO tb_news_detail (tb_news_id, title, link, snippet) VALUES (%s, %s, %s, %s)",
            (news_id, title, link, snippet)
        )
    conn.commit()
    cursor.close()
    conn.close()


def simpan_log_akses(update: Update, menu, is_callback: bool = False):

    if (is_callback):
        user_id = 0
        username = "Callback"
    else:
        user_id = update.message.from_user.id
        username = update.message.from_user.username

    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 

    cursor.execute(
        "INSERT INTO tb_akses (user_telegram_id, user_telegram_username, tgl_akses, menu) VALUES (%s, %s, %s, %s)" , (user_id, username, current_time,menu)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi yang akan dijalankan ketika perintah /start dikirimkan
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    simpan_log_akses(update, 'start')

    await update.message.reply_text('Silakan manfaatkan BOT ini untuk keperluan Trading/Investing\n\nKetik /help untuk mendapatkan daftar perintah yang dipakai')

    
def get_profile(akode_emiten, akelompok):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("select * from tb_profiles a where a.kode_emiten = %s", (akode_emiten))
    profiles = cursor.fetchall()

    pesan_profile = "";
    for profile in profiles:
        pesan_profile = pesan_profile + f"<b>Kode : {profile['kode_emiten']}</b>\n"
        pesan_profile = pesan_profile + f"<b>Nama : {profile['Nama_emiten']}</b>\n"
        pesan_profile = pesan_profile + f"<b>Alamat : {profile['alamat']}</b>\n"


def get_emiten_by_jenis_pengumuman(akelompok, aindex):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()

    sfilter, sfilter_or = get_filter_pengumuman(akelompok)

    print(akelompok)
    print(sfilter)
    
    jml_baris = 10

    offset = (aindex - 1) * jml_baris
    
    cursor.execute("SELECT a.kode_emiten, max(a.tgl_pengumuman) as tgl_pengumuman "
                    + " FROM tb_pengumuman a " 
                    + " WHERE (a.judul_pengumuman like %s or a.judul_pengumuman like %s)"
                    + " GROUP BY a.kode_emiten " 
                    + " order by 2 desc " 
                    + " limit %s offset %s", (sfilter,sfilter_or, jml_baris, offset))
    keterbukaans = cursor.fetchall()
    

    nomor = offset
    pesan_pengumuman = ""
    keyboard = []

    for keterbukaan in keterbukaans:
        nomor += 1
        keyboard.append([
            InlineKeyboardButton(
                text=f"{nomor}. {keterbukaan['kode_emiten']} [Tanggal: {keterbukaan['tgl_pengumuman']}]",
                callback_data=f"keterbukaan {keterbukaan['kode_emiten']} {akelompok}"
            )
        ])

    if (aindex > 1):
        prev_index = aindex - 1
        keyboard.append([
            InlineKeyboardButton(
                text=f"Prev",
                callback_data=f"emiten {akelompok} {prev_index}"
            )
        ])

    next_index = aindex + 1
    keyboard.append([
        InlineKeyboardButton(
            text=f"Next",
            callback_data=f"emiten {akelompok} {next_index}"
        )
    ])
        
        
        

    cursor.close()
    conn.close()
    
    return InlineKeyboardMarkup(keyboard)

def get_filter_pengumuman(akelompok):
    sfilter = f'%{akelompok}%'
    sfilter_or = f'%{akelompok}%'

    if (akelompok == "PE"):
        sfilter = '%public expose%'
        sfilter_or = '%public expose%'
    elif (akelompok == "DIV"):
        sfilter = '%dividen%'
        sfilter_or = '%dividen%'
    elif (akelompok == "RUPS"):
        sfilter = '%rups%'
        sfilter_or = '%Rapat%Umum%Pemegang%Saham%'
    elif (akelompok == "LK"):
        sfilter = '%laporan%keuangan%'
        sfilter_or = '%laporan%keuangan%'

    return sfilter, sfilter_or


def get_pesan_pengumuman(akode_emiten, akelompok):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()

    sfilter, sfilter_or = get_filter_pengumuman(akelompok)

    print(akode_emiten)
    print(sfilter)
    print(sfilter_or)
    
    cursor.execute("SELECT * FROM tb_pengumuman WHERE kode_emiten like %s AND (judul_pengumuman like %s or judul_pengumuman like %s) order by tgl_pengumuman desc limit 10", (akode_emiten,sfilter, sfilter_or))
    keterbukaans = cursor.fetchall()
    

    nomor = 0
    pesan_pengumuman = ""
    for keterbukaan in keterbukaans:
        nomor = nomor + 1
        pesan_pengumuman = pesan_pengumuman + f"{nomor}.{keterbukaan['judul_pengumuman']} [Tanggal : {keterbukaan['tgl_pengumuman']}]\n"


        id_pengumuman = keterbukaan['id']
        print(f"ID Pengumuman : {id_pengumuman}")
        sql = "select * from tb_pengumuman_attachment where id_pengumuman = %s"
        print(sql, (id_pengumuman,))
        cursor.execute(sql, (id_pengumuman,))
        details = cursor.fetchall()
        print(details)
        
        if details:
            pesan_attachment = ""
            for detail in details:
                pesan_attachment = pesan_attachment + f"<a href='{detail['url']}'>{detail['original_name']}</a>\n"


            pesan_pengumuman = pesan_pengumuman + pesan_attachment + '\n'

        

    cursor.close()
    conn.close()
    
    return pesan_pengumuman


async def keterbukaan(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False) -> None:
    try:
        print("masuk sini")

        # Tentukan sumber pesan
        message = (
            update.callback_query.message if is_callback else update.message
        )



        if context.args:
            kode_emiten = context.args[0].upper()

            if len(context.args) > 1:
                kelompok = context.args[1].upper()
            else:
                kelompok = '%'

            pesan = f"<b>Keterbukaan Informasi Saham {kode_emiten} - {kelompok}</b>\n\n"
            pesan_pengumuman = get_pesan_pengumuman(kode_emiten, kelompok)
            if pesan_pengumuman:
                pesan += pesan_pengumuman

            # Balas pesan sesuai sumbernya
            if is_callback:
                print("Masuk Call Back")
                await message.edit_text(pesan, parse_mode='HTML')
            else:
                print("Masuk Biasa")
                print(pesan)
                await message.reply_text(pesan, parse_mode='HTML')
        else:
            error_msg = '<b>Please provide Emiten Code</b>'
            if is_callback:
                await message.edit_text(error_msg, parse_mode='HTML')
            else:
                await message.reply_text(error_msg, parse_mode='HTML')

        simpan_log_akses(update, 'keterbukaan', is_callback)
    except Exception as e:
        print(f"Error: {e}")
        error_msg = "Error happened, try again"
        if is_callback:
            await message.edit_text(error_msg)
        else:
            await message.reply_text(error_msg)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False) -> None:
    # Tentukan sumber pesan
    message = (
        update.callback_query.message if is_callback else update.message
    )

    try:
        if context.args:
            kode_emiten = context.args[0].upper()

            index = 1
            if len(context.args) > 1:
                index = int(context.args[1])

            pesan = get_profile(akelompok, "pe")

            # keyboard = get_emiten_by_jenis_pengumuman(kelompok, index)

            if is_callback:
                await message.edit_text(pesan, parse_mode='HTML', reply_markup=keyboard)
            else:
                await message.reply_text(pesan, parse_mode='HTML', reply_markup=keyboard)
        else:
            if is_callback:
                await message.edit_text('<b>Please provide Option Code</b>', parse_mode='HTML')
            else:
                await message.reply_text('<b>Please provide Option Code</b>', parse_mode='HTML')

        simpan_log_akses(update, 'profile', is_callback)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Error happened, try again")

async def emiten(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False) -> None:
    # Tentukan sumber pesan
    message = (
        update.callback_query.message if is_callback else update.message
    )

    try:
        if context.args:
            kelompok = context.args[0].upper()

            index = 1
            if len(context.args) > 1:
                index = int(context.args[1])

            pesan = f"<b>10 Emiten ke-{index} Dengan Opsi {kelompok}</b>\n\n"

            keyboard = get_emiten_by_jenis_pengumuman(kelompok, index)

            if is_callback:
                await message.edit_text(pesan, parse_mode='HTML', reply_markup=keyboard)
            else:
                await message.reply_text(pesan, parse_mode='HTML', reply_markup=keyboard)
        else:
            if is_callback:
                await message.edit_text('<b>Please provide Option Code</b>', parse_mode='HTML')
            else:
                await message.reply_text('<b>Please provide Option Code</b>', parse_mode='HTML')

        simpan_log_akses(update, 'emiten', is_callback)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Error happened, try again")

# Fungsi untuk membuka browser dengan URL yang diberikan oleh user
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if context.args:
            kode_emiten = context.args[0].upper()
            print(f"Request news {kode_emiten}")

            news_record = check_news_exists(kode_emiten)
            print(news_record)

            if not news_record:
                hasil = cari(kode_emiten, api_key, cx_key)
                print('Cari : ')
                print(hasil)

                save_news(kode_emiten, hasil)
                news_record = check_news_exists(kode_emiten)

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT title, link, snippet FROM tb_news_detail WHERE tb_news_id = %s",
                (news_record['id'],)
            )
            details = cursor.fetchall()
            conn.close()

            # Kirimkan hasil pencarian yang sudah ada
            for detail in details:
                title = f"<b>{detail['title']}</b>"
                link = f"<a href='{detail['link']}'>{title}</a>"
                snippet = f"{detail['snippet']}"
                await update.message.reply_text(f"{link}\n{snippet}\n", parse_mode='HTML')

            await update.message.reply_text(f'<i>Done showing news about {kode_emiten}!</i>', parse_mode='HTML')

            # for i, item in enumerate(hasil):
            #     title = f"<b>{item['title']}</b>"
            #     link = f"<a href='{item['link']}'>{title}</a>"
            #     snippet = f"{item['snippet']}"
                
            #     # Kirim pesan HTML
            #     await update.message.reply_text(f"{link}\n{snippet}\n", parse_mode='HTML')

            # await update.message.reply_text(f'<i>Done showing news about {kode_emiten}!</i>', parse_mode='HTML')
        else:
            await update.message.reply_text('<b>Please provide Emiten Code</b>', parse_mode='HTML')

        simpan_log_akses(update, 'news')
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Error happened, try again")

async def help(update, context):
    pesan = """
        Selamat datang!

        Daftar perintah yang tersedia:

        /start - Memulai bot dan memastikan kesiapan.
        /news [KODE_EMITIEN] - Mendapatkan berita tentang emiten tertentu.
        /keterbukaan [KODE_EMITIEN] - Mendapatkan keterbukaan informasi emiten tertentu.
        /keterbukaan [KODE_EMITIEN] [OPSI]- Mendapatkan keterbukaan informasi emiten tertentu khusus keterbukaan tertentu.        
        /emiten [OPSI] - Mendapatkan 10 daftar pertama emiten dengan aksi korporasi tertentu
        /emiten [OPSI] [INDEX]- Mendapatkan 10 daftar ke-INDEX emiten dengan aksi korporasi tertentu 

        OPSI : pe = public expose, div = dividen, rups = RUPS, lk = Laporan Keuangan
        INDEX : 1, 2, 3, 4, dst

        /help - Menampilkan pesan bantuan ini.

        Contoh penggunaan:
        /news TLKM
        /keterbukaan TLKM
        /keterbukaan TLKM pe

        /emiten pe
        /emiten pe 2
        /emiten pe 3

        /emiten div
        /emiten div 2
        /emiten div 3

        /emiten rups
        /emiten rups 2
        /emiten rups 3

        /emiten lk
        /emiten lk 2
        /emiten lk 3
        """

    await update.message.reply_text(pesan)

    simpan_log_akses(update, 'help')

def cari(query, api_key, cx_key, jumlah_hasil=10):
    print(f'Custom Search {query}')

    try:
        search_service = build("customsearch", "v1", developerKey=api_key)
        res = search_service.cse().list(q=query, cx=cx_key, num=jumlah_hasil, dateRestrict='d30', sort='date').execute()
        return res.get('items', [])
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()  # Menjawab callback query agar tidak menunggu

        # Ambil argumen dari callback data
        args = query.data.split(" ")
        context.args = args[1:]

        print("arg[0]")
        print(args[0])

        if (args[0] == "keterbukaan"):                    
            await keterbukaan(update, context, is_callback=True)
        elif (args[0] == "emiten"):
            await emiten(update, context, is_callback=True)
        else:
            await query.edit_message_text(text="Format callback data tidak valid.")
    except Exception as e:
        print(f"Error in callback: {e}")


# Fungsi utama untuk menjalankan bot
def main() -> None:
    try:
        application = (
            ApplicationBuilder()
            .token(TOKEN)
            .connect_timeout(10)  # Timeout koneksi
            .read_timeout(30)     # Timeout membaca data
            .build()
        )
        
        # Menambahkan handler untuk command /start
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("news", news))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("keterbukaan", keterbukaan))
        application.add_handler(CommandHandler("emiten", emiten))
        application.add_handler(CommandHandler("profile", profile))
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Memulai bot
        application.run_polling()
    except Exception as e:
        print(f"Terjadi error: {e}")

if __name__ == '__main__':
    print('BOT Telegram started')
    main()

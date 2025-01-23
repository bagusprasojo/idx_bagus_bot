import mysql.connector
from dotenv import load_dotenv
from googleapiclient.discovery import build
import webbrowser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder, ContextTypes

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


def simpan_log_akses(update: Update, menu):
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

    

def get_pesan_pengumuman(akode_emiten, akelompok):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()

    sfilter = '%'
    if (akelompok == "PE"):
        sfilter = '%public expose%'

    print(akode_emiten)
    print(sfilter)
    
    cursor.execute("SELECT * FROM tb_pengumuman WHERE kode_emiten = %s AND judul_pengumuman like %s order by tgl_pengumuman desc limit 10", (akode_emiten,sfilter))
    print("SELECT * FROM tb_pengumuman WHERE kode_emiten = %s AND judul_pengumuman like %s order by tgl_pengumuman desc limit 10", (akode_emiten,sfilter))
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


async def keterbukaan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if context.args:
            kode_emiten = context.args[0].upper()
                
            if (len(context.args) > 1):
                kelompok = context.args[1].upper()
            else:
                kelompok = '%'

            pesan = f"<b>Keterbukaan Informasi Saham {kode_emiten} </b>\n\n"
            pesa = pesan + """
            """

            pesan_pengumuman = get_pesan_pengumuman(kode_emiten, kelompok)
            if pesan_pengumuman:
                pesan = pesan + ' ' + pesan_pengumuman

            await update.message.reply_text(pesan, parse_mode='HTML')
            
        else:
            await update.message.reply_text('<b>Please provide Emiten Code</b>', parse_mode='HTML')

        simpan_log_akses(update, 'keterbukaan')
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Error happened, try again")

async def pengumuman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if context.args:
            kode_emiten = context.args[0].upper()
            pesan = f"<b>Pengumuman Saham {kode_emiten}</b>\n\n"
            pesa = pesan + """
            """

            pesan_pengumuman = get_pesan_pengumuman(kode_emiten, 'pengumuman')
            if pesan_pengumuman:
                pesan = pesan + ' ' + pesan_pengumuman

            await update.message.reply_text(pesan, parse_mode='HTML')
            
        else:
            await update.message.reply_text('<b>Please provide Emiten Code</b>', parse_mode='HTML')

        simpan_log_akses(update, 'pengumuman')
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
        /help - Menampilkan pesan bantuan ini.

        Contoh penggunaan:
        /news TLKM
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


# Fungsi utama untuk menjalankan bot
def main() -> None:
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
    application.add_handler(CommandHandler("pengumuman", pengumuman))
    
    # Memulai bot
    application.run_polling()

if __name__ == '__main__':
    print('BOT Telegram started')
    main()

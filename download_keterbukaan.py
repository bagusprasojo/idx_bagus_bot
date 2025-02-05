from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
import mysql.connector
from dotenv import load_dotenv
import os
import sys
import requests
import json
import datetime

# load_dotenv()

# host_ = os.getenv("host")
# user_ = os.getenv("user")
# password_ = os.getenv("password")
# database_ = os.getenv("database")

# # Setup koneksi ke database MySQL
# def get_db_connection():
#     return mysql.connector.connect(
#         host= host_,
#         user= user_,
#         password=password_,
#         database=database_
#     )


def proses_json_keterbukaan(filename):
  # Cek apakah file ada sebelum mencoba membukanya
  if not os.path.exists(filename):
      print(f"File {filename} tidak ditemukan!")
      return  # Keluar dari fungsi jika file tidak ditemukan

  # URL endpoint untuk memproses JSON
  url = "https://bagusprasojo.pythonanywhere.com/api/process-json-keterbukaan"
  # url = "http://localhost:5000/api/process-json-keterbukaan"

  # Nama file JSON yang telah disimpan sebelumnya
  # filename = '20240101_20241224_4.json'

  # Membaca file JSON
  with open(filename, 'r', encoding='utf-8') as file:
      data = json.load(file)

  # Payload adalah data yang dibaca dari file
  payload = data

  # Header untuk request
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YWRtaW46YWRtaW4='  # Sesuaikan dengan header yang dibutuhkan
  }

  # Mengirim request POST dengan JSON payload
  response = requests.post(url, headers=headers, json=payload)

  # Mencetak hasil response
  print(response.text)

def download_keterbukaan(aindex_from, atgl_awal, atgl_akhir, filename='isi'):
    driver = webdriver.Firefox()
    url = f"https://www.idx.co.id/primary/ListedCompany/GetAnnouncement?emitenType=s&indexFrom={aindex_from}&pageSize=20&dateFrom=19010101&dateTo={atgl_akhir}&lang=id&keyword="
    print(url)
    driver.get(url)


    data = json.loads(driver.find_element(By.TAG_NAME, "body").text.strip())  
    print(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4) 
    

    driver.close()


try:
    for i in range(1, 11):
        print(i)
        # Menghitung tgl_akhir (tanggal sekarang) dan tgl_awal (30 hari yang lalu)
        tgl_akhir = datetime.datetime.now().strftime('%Y%m%d')  # Tanggal sekarang dalam format YYYYMMDD
        tgl_awal = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d')  # 7 hari yang lalu       

        filename = f"keterbukaan/{tgl_awal}_{tgl_akhir}_{i}.json"
        print('Download ' + filename)
        download_keterbukaan(i,tgl_awal , tgl_akhir, filename)
        
        print('Proses ' + filename)
        proses_json_keterbukaan(filename)

except mysql.connector.Error as e:  # Menangkap kesalahan MySQL
    print(f"Kesalahan database: {e}")
except requests.exceptions.RequestException as e:  # Menangkap kesalahan HTTP
    print(f"Kesalahan HTTP: {e}")
except Exception as e:  # Menangkap semua kesalahan lainnya
    print(f"Kesalahan lain ya: {e}")
 
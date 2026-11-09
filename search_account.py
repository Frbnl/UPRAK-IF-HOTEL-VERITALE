from conn import konek, dbcursor, tampilkan
from datetime import datetime
import time as count

def search_by_id(guest_id):
    sql = "SELECT * FROM guests WHERE guest_id = %s"
    dbcursor.execute(sql, (guest_id,))
    konek.commit()
    result = dbcursor.fetchone()
    if result:
        print(f"Data tamu ditemukan: ID: {result[0]}, Nama: {result[1]}, Jenis Kelamin: {result[2]}, Negara: {result[3]}, Email: {result[4]}, Telepon: {result[5]}, Status Member: {result[6]}, Tanggal Registrasi: {result[7]}")
    else:
        print(f"Tamu dengan ID {guest_id} tidak ditemukan.")

def search_by_name(guest_name):
    sql = "SELECT * FROM guests WHERE guest_name = %s"
    dbcursor.execute(sql, (guest_name,))
    konek.commit()
    results = dbcursor.fetchall()
    if results:
        for result in results:
            print(f"Data tamu ditemukan: ID: {result[0]}, Nama: {result[1]}, Jenis Kelamin: {result[2]}, Negara: {result[3]}, Email: {result[4]}, Telepon: {result[5]}, Status Member: {result[6]}, Tanggal Registrasi: {result[7]}")
    else:
        print(f"Tamu dengan nama {guest_name} tidak ditemukan.")
        
def search_by_email(email):
    sql = "SELECT * FROM guests WHERE email = %s"
    dbcursor.execute(sql, (email,))
    konek.commit()
    result = dbcursor.fetchone()
    if result:
        print(f"Data tamu ditemukan: ID: {result[0]}, Nama: {result[1]}, Jenis Kelamin: {result[2]}, Negara: {result[3]}, Email: {result[4]}, Telepon: {result[5]}, Status Member: {result[6]}, Tanggal Registrasi: {result[7]}")
    else:
        print(f"Tamu dengan email {email} tidak ditemukan.")

def search_by_phone(phone):
    sql = "SELECT * FROM guests WHERE phone = %s"
    dbcursor.execute(sql, (phone,))
    konek.commit()
    result = dbcursor.fetchone()
    if result:
        print(f"Data tamu ditemukan: ID: {result[0]}, Nama: {result[1]}, Jenis Kelamin: {result[2]}, Negara: {result[3]}, Email: {result[4]}, Telepon: {result[5]}, Status Member: {result[6]}, Tanggal Registrasi: {result[7]}")
    else:
        print(f"Tamu dengan nomor telepon {phone} tidak ditemukan.")

def find_guest_account():
    print("\n--- Cari Berdasarkan... ---")
    print("1. ID Tamu")
    print("2. Nama Tamu")
    print("3. Email Tamu")
    print("4. Nomor Telepon Tamu")
    print("5. Kembali ke Menu Utama")
    pilihan_cari = input("Masukkan pilihan: ")
    if pilihan_cari == "1":
        guest_id = input("Masukkan ID tamu: ")
        search_by_id(guest_id)
    elif pilihan_cari == "2":
        guest_name = input("Masukkan nama tamu: ")
        search_by_name(guest_name)
    elif pilihan_cari == "3":
        email = input("Masukkan email tamu: ")
        search_by_email(email)
    elif pilihan_cari == "4":
        phone = input("Masukkan nomor telepon tamu: ")
        search_by_phone(phone)
    elif pilihan_cari == "5":
        return  # As it says, return to the main menu
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")
        find_guest_account()
    
    
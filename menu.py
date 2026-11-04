from conn import konek, dbcursor, tampilkan
from datetime import datetime

#CREATE HOTEL GUEST ACCOUNT
def create_guest_account():
    nama = input("Masukkan nama tamu: ")
    jk = input("Masukkan jenis kelamin tamu (L/P): ").upper()
    country = input("Masukkan negara tamu: ")
    member = input("Apakah tamu ingin menjadi member? (Y/N): ").upper()
    email = input("Masukkan email tamu: ")
    telpon = input("Masukkan nomor telepon tamu: ")
    register_date = datetime.now().strftime("%d %m %Y")

    sql = "INSERT INTO guests (guest_name, gender, country, email, phone, member_status, registered_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (nama, jk, country, email, telpon, member, register_date)
    dbcursor.execute(sql, val)
    konek.commit()
    print(f"Tamu {nama} berhasil ditambahkan dengan ID {dbcursor.lastrowid}.")
    
#MENU
print("\n===== HOTEL VERITALE =====")
print("1. Create Guest Account")
print("0. Exit")

#MENU LOOP
while True:
    pilihan = input("Masukkan pilihan: ")
    if pilihan == "1":
        create_guest_account()
    elif pilihan == "0":
        print("Terima kasih telah menggunakan program ini.")
        break
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")
from conn import konek, dbcursor, tampilkan
from search_account import search_by_id, find_guest_account
from booking_management import booking_menu
from room_management import room_menu
import time as count
from datetime import datetime


def timer(seconds):
    for i in range(seconds, 0, -1):
        print(f"Program akan kembali dalam {i} detik...", end="\\r")
        count.sleep(1)
    print(" " * 50, end="\\r")


def login():
    while True:
        print("\\n===== HOTEL VERITALE =====")
        print("1. Login as Admin")
        print("2. Continue as Guest")
        print("0. Exit")
        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":
            username = input("Username: ")
            password = input("Password: ")
            sql = "SELECT * FROM admins WHERE username = %s AND password = %s"
            dbcursor.execute(sql, (username, password))
            admin = dbcursor.fetchone()

            if admin:
                print("Login admin berhasil.")
                return "admin"
            else:
                print("Username atau password salah.")

        elif pilihan == "2":
            print("Anda masuk sebagai Guest.")
            return "guest"

        elif pilihan == "0":
            return "exit"

        else:
            print("Pilihan tidak valid.")


# CREATE HOTEL GUEST ACCOUNT
def create_guest_account():
    dbcursor.execute("SELECT MAX(CAST(guest_id AS UNSIGNED)) FROM guests")
    max_guest_id = dbcursor.fetchone()[0] or 0
    guest_id = int(max_guest_id) + 1

    while True:
        dbcursor.execute("SELECT 1 FROM guests WHERE guest_id = %s", (guest_id,))
        if dbcursor.fetchone() is None:
            break
        guest_id += 1

    nama = input("Masukkan nama tamu: ")
    jk = input("Masukkan jenis kelamin tamu (L/P): ").upper()
    country = input("Masukkan negara tamu: ")
    member = input("Apakah tamu ingin menjadi member? (Y/N): ").upper()
    email = input("Masukkan email tamu: ")
    telpon = input("Masukkan nomor telepon tamu: ")

    while True:
        register_date = input("Masukkan tanggal registrasi (YYYY-MM-DD HH:MM:SS): ")
        try:
            parsed_date = datetime.strptime(register_date, "%Y-%m-%d %H:%M:%S")
            if parsed_date.strftime("%Y-%m-%d %H:%M:%S") == register_date:
                break
        except ValueError:
            pass
        print("Format tanggal tidak sesuai. Silakan masukkan kembali dengan format YYYY-MM-DD HH:MM:SS.")

    sql = "INSERT INTO guests (guest_id, guest_name, gender, country, email, phone, member_status, registered_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (guest_id, nama, jk, country, email, telpon, member, register_date)
    dbcursor.execute(sql, val)
    konek.commit()
    print(f"Tamu {nama} berhasil ditambahkan dengan ID {guest_id}.")
    timer(3)


def view_guest_accounts():
    sql = "SELECT * FROM guests"
    dbcursor.execute(sql)
    results = dbcursor.fetchall()
    if results:
        print("\\n--- Daftar Akun Tamu ---")
        tampilkan(results)
    else:
        print("Tidak ada akun tamu yang ditemukan.")
    timer(3)


def update_guest_account():
    guest_id = input("Masukkan ID tamu yang ingin diperbarui: ")
    sql = "SELECT * FROM guests WHERE guest_id = %s"
    dbcursor.execute(sql, (guest_id,))
    result = dbcursor.fetchone()

    if result:
        result = list(result)
        print("Data tamu saat ini:")
        tampilkan([result])
        nama = input("Masukkan nama tamu baru (kosongkan jika tidak ingin mengubah): ")
        jk = input("Masukkan jenis kelamin tamu baru (L/P) (kosongkan jika tidak ingin mengubah): ").upper()
        country = input("Masukkan negara tamu baru (kosongkan jika tidak ingin mengubah): ")
        email = input("Masukkan email tamu baru (kosongkan jika tidak ingin mengubah): ")
        telpon = input("Masukkan nomor telepon tamu baru (kosongkan jika tidak ingin mengubah): ")
        member = input("Apakah tamu ingin menjadi member? (Y/N) (kosongkan jika tidak ingin mengubah): ").upper()

        if nama:
            result[1] = nama
        if jk:
            result[2] = jk
        if country:
            result[3] = country
        if email:
            result[4] = email
        if telpon:
            result[5] = telpon
        if member:
            result[6] = member

        sql_update = "UPDATE guests SET guest_name=%s, gender=%s, country=%s, email=%s, phone=%s, member_status=%s WHERE guest_id=%s"
        val_update = (result[1], result[2], result[3], result[4], result[5], result[6], guest_id)
        dbcursor.execute(sql_update, val_update)
        konek.commit()
        print(f"Akun tamu dengan ID {guest_id} berhasil diperbarui.")
    else:
        print(f"Tamu dengan ID {guest_id} tidak ditemukan.")
    timer(3)


def delete_guest():
    guest_id = input("Masukkan ID tamu yang ingin dihapus: ")
    sql = "SELECT * FROM guests WHERE guest_id = %s"
    dbcursor.execute(sql, (guest_id,))
    result = dbcursor.fetchone()

    if result:
        print("Data tamu yang akan dihapus:")
        tampilkan([result])
        confirm = input(f"Apakah Anda yakin ingin menghapus akun tamu {result[1]}? (Y/N): ").upper()
        if confirm == "Y":
            sql_delete = "DELETE FROM guests WHERE guest_id = %s"
            dbcursor.execute(sql_delete, (guest_id,))
            konek.commit()
            print(f"Akun tamu dengan ID {guest_id} berhasil dihapus.")
        else:
            print("Penghapusan dibatalkan.")
    else:
        print(f"Tamu dengan ID {guest_id} tidak ditemukan.")
    timer(3)


def find_guest_account():
    print("\\n--- Cari Berdasarkan... ---")
    print("1. ID Tamu")
    print("2. Nama Tamu")
    print("3. Email Tamu")
    print("4. Nomor Telepon Tamu")
    pilihan_cari = input("Masukkan pilihan: ")

    if pilihan_cari == "1":
        guest_id = input("Masukkan ID tamu: ")
        dbcursor.execute("SELECT * FROM guests WHERE guest_id = %s", (guest_id,))
        result = dbcursor.fetchone()
        if result:
            tampilkan([result])
        else:
            print(f"Tamu dengan ID {guest_id} tidak ditemukan.")
    elif pilihan_cari == "2":
        guest_name = input("Masukkan nama tamu: ")
        dbcursor.execute("SELECT * FROM guests WHERE guest_name = %s", (guest_name,))
        results = dbcursor.fetchall()
        if results:
            tampilkan(results)
        else:
            print(f"Tamu dengan nama {guest_name} tidak ditemukan.")
    elif pilihan_cari == "3":
        email = input("Masukkan email tamu: ")
        dbcursor.execute("SELECT * FROM guests WHERE email = %s", (email,))
        result = dbcursor.fetchone()
        if result:
            tampilkan([result])
        else:
            print(f"Tamu dengan email {email} tidak ditemukan.")
    elif pilihan_cari == "4":
        phone = input("Masukkan nomor telepon tamu: ")
        dbcursor.execute("SELECT * FROM guests WHERE phone = %s", (phone,))
        result = dbcursor.fetchone()
        if result:
            tampilkan([result])
        else:
            print(f"Tamu dengan nomor telepon {phone} tidak ditemukan.")
    else:
        print("Pilihan tidak valid.")


def guest_acc_management():
    while True:
        print("\\n--- Guest Account Management ---")
        print("1. Create guest account")
        print("2. View guest accounts")
        print("3. Update guest account")
        print("4. Delete guest account")
        print("5. Find guest account")
        print("0. Back to main menu")

        pilihan_submenu = input("Masukkan pilihan: ")
        if pilihan_submenu == "1":
            create_guest_account()
        elif pilihan_submenu == "2":
            view_guest_accounts()
        elif pilihan_submenu == "3":
            update_guest_account()
        elif pilihan_submenu == "4":
            delete_guest()
        elif pilihan_submenu == "5":
            find_guest_account()
        elif pilihan_submenu == "0":
            print("Kembali ke menu utama.")
            return
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")


# MAIN MENU
role = login()

if role == "admin":
    while True:
        print("\\n===== HOTEL VERITALE (ADMIN) =====")
        print("1. Guest account management")
        print("2. Booking management")
        print("3. Room management")
        print("0. Logout")

        pilihan = input("Masukkan pilihan: ")
        if pilihan == "1":
            guest_acc_management()
        elif pilihan == "2":
            booking_menu()
        elif pilihan == "3":
            room_menu("admin")
        elif pilihan == "0":
            print("Logout berhasil.")
            break
        else:
            print("Pilihan tidak valid.")

elif role == "guest":
    while True:
        print("\\n===== HOTEL VERITALE (GUEST) =====")
        print("1. View Rooms")
        print("0. Exit")

        pilihan = input("Masukkan pilihan: ")
        if pilihan == "1":
            room_menu("guest")
        elif pilihan == "0":
            print("Terima kasih telah menggunakan program ini.")
            break
        else:
            print("Pilihan tidak tersedia.")

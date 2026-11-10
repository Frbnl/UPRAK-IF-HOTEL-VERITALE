from conn import konek, dbcursor, tampilkan
from booking_management import booking_menu, create_booking
from room_management import room_menu, view_rooms
import time as count
from datetime import datetime


def timer(seconds):
    for i in range(seconds, 0, -1):
        print(f"Program akan kembali dalam {i} detik...", end="\r", flush=True)
        count.sleep(1)
    print("\r" + " " * 50 + "\r", end="", flush=True)


def login():
    while True:
        print("\n===== HOTEL VERITALE =====")
        print("1. Login as Admin")
        print("2. Login with Guest ID")
        print("3. Create Guest Account")
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
            guest_id = input("Masukkan ID tamu: ").strip()
            dbcursor.execute(
                "SELECT guest_id, guest_name FROM guests WHERE guest_id = %s",
                (guest_id,),
            )
            guest = dbcursor.fetchone()
            if guest:
                print(f"Selamat datang, {guest[1]}.")
                return ("guest", guest[0], guest[1])
            print("Akun tamu tidak ditemukan.")

        elif pilihan == "3":
            guest = create_guest_account()
            if guest:
                print(f"Selamat datang, {guest[1]}.")
                return ("guest", guest[0], guest[1])

        elif pilihan == "0":
            return "exit"

        else:
            print("Pilihan tidak valid.")


def create_guest_account():
    dbcursor.execute("SELECT MAX(CAST(guest_id AS UNSIGNED)) FROM guests")
    max_guest_id = dbcursor.fetchone()[0] or 0
    guest_id = int(max_guest_id) + 1

    while True:
        dbcursor.execute("SELECT 1 FROM guests WHERE guest_id = %s", (guest_id,))
        if dbcursor.fetchone() is None:
            break
        guest_id += 1

    nama = input("Masukkan nama tamu: ").strip()
    jk = input("Masukkan jenis kelamin tamu (L/P): ").strip().upper()
    country = input("Masukkan negara tamu: ").strip()
    member = input("Apakah tamu ingin menjadi member? (Y/N): ").strip().upper()
    email = input("Masukkan email tamu: ").strip()
    telpon = input("Masukkan nomor telepon tamu: ").strip()

    if (
        not all((nama, country, email, telpon))
        or jk not in ("L", "P")
        or member not in ("Y", "N")
    ):
        print("Data tidak valid. Akun tamu tidak dibuat.")
        return None

    register_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = (
        "INSERT INTO guests "
        "(guest_id, guest_name, gender, country, email, phone, member_status, registered_date) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    val = (guest_id, nama, jk, country, email, telpon, member, register_date)
    dbcursor.execute(sql, val)
    konek.commit()
    print(f"Tamu {nama} berhasil ditambahkan dengan ID {guest_id}.")
    return guest_id, nama


def view_guest_accounts():
    sql = "SELECT * FROM guests"
    dbcursor.execute(sql)
    results = dbcursor.fetchall()
    if results:
        print("\n--- Daftar Akun Tamu ---")
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
        dbcursor.execute(
            "SELECT 1 FROM bookings WHERE guest_id = %s LIMIT 1",
            (guest_id,),
        )
        if dbcursor.fetchone():
            print("Akun tamu tidak dapat dihapus karena sudah memiliki data booking.")
            timer(3)
            return

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
    print("\n--- Cari Berdasarkan... ---")
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

def guest_report():
    sql = """
    SELECT
        guests.guest_id,
        guests.guest_name,
        guests.email,
        guests.phone
    FROM guests
    LEFT JOIN bookings
        ON guests.guest_id = bookings.guest_id
    WHERE bookings.booking_id IS NULL
    """
    dbcursor.execute(sql)
    results = dbcursor.fetchall()

    if results:
        print("\n--- Guest Report: Guests Without Booking ---")
        tampilkan(results)
    else:
        print("Semua tamu sudah memiliki booking.")
    timer(3)


def guest_acc_management():
    while True:
        print("\n--- Guest Account Management ---")
        print("1. Create guest account")
        print("2. View guest accounts")
        print("3. Update guest account")
        print("4. Delete guest account")
        print("5. Find guest account")
        print("6. Guest booking report")
        print("0. Back to main menu")

        pilihan_submenu = input("Masukkan pilihan: ")
        if pilihan_submenu == "1":
            create_guest_account()
            timer(3)
        elif pilihan_submenu == "2":
            view_guest_accounts()
        elif pilihan_submenu == "3":
            update_guest_account()
        elif pilihan_submenu == "4":
            delete_guest()
        elif pilihan_submenu == "5":
            find_guest_account()
        elif pilihan_submenu == "6":
            guest_report()
        elif pilihan_submenu == "0":
            print("Kembali ke menu utama.")
            return
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")


def view_guest_booking(guest_id):
    sql = """
    SELECT
        bookings.booking_id,
        guests.guest_name,
        rooms.room_id,
        rooms.room_type,
        bookings.check_in,
        bookings.check_out,
        bookings.nights,
        bookings.total_payment,
        bookings.payment_method,
        bookings.booking_status
    FROM bookings
    INNER JOIN guests
        ON bookings.guest_id = guests.guest_id
    INNER JOIN rooms
        ON bookings.room_id = rooms.room_id
    WHERE bookings.guest_id = %s
    """
    dbcursor.execute(sql, (guest_id,))
    bookings = dbcursor.fetchall()
    if bookings:
        print("\n--- Booking Saya ---")
        tampilkan(bookings)
    else:
        print("Belum ada booking untuk akun ini.")


def main():
    session = login()

    if session == "admin":
        while True:
            print("\n===== HOTEL VERITALE (ADMIN) =====")
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

    elif isinstance(session, tuple) and session[0] == "guest":
        guest_id, guest_name = session[1:]
        while True:
            print(f"\n===== HOTEL VERITALE ({guest_name}) =====")
            print("1. View Rooms")
            print("2. Create Booking")
            print("3. View My Bookings")
            print("4. View My Account")
            print("0. Exit")

            pilihan = input("Masukkan pilihan: ")
            if pilihan == "1":
                view_rooms()
            elif pilihan == "2":
                create_booking(guest_id)
            elif pilihan == "3":
                view_guest_booking(guest_id)
            elif pilihan == "4":
                dbcursor.execute("SELECT * FROM guests WHERE guest_id = %s", (guest_id,))
                guest = dbcursor.fetchone()
                if guest:
                    print("\n--- Akun Saya ---")
                    tampilkan([guest])
                else:
                    print("Akun tamu tidak lagi tersedia.")
            elif pilihan == "0":
                print("Terima kasih telah menggunakan program ini.")
                break
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")


if __name__ == "__main__":
    main()

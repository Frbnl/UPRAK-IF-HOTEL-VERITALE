from conn import konek, dbcursor, tampilkan
import time as count


def timer(seconds):
    for i in range(seconds, 0, -1):
        print(f"Program akan kembali dalam {i} detik...", end="\r", flush=True)
        count.sleep(1)
    print("\r" + " " * 50 + "\r", end="", flush=True)


def view_rooms():
    sql = "SELECT * FROM rooms"
    dbcursor.execute(sql)
    results = dbcursor.fetchall()
    if results:
        print("\n--- Daftar Kamar ---")
        tampilkan(results)
    else:
        print("Tidak ada kamar yang ditemukan.")
    timer(3)


def add_room():
    dbcursor.execute("SELECT MAX(CAST(room_id AS UNSIGNED)) FROM rooms")
    max_room_id = dbcursor.fetchone()[0] or 0
    room_id = int(max_room_id) + 1

    while True:
        dbcursor.execute("SELECT 1 FROM rooms WHERE room_id = %s", (room_id,))
        if dbcursor.fetchone() is None:
            break
        room_id += 1

    room_type = input("Masukkan tipe kamar: ")
    floor = input("Masukkan lantai kamar: ")
    bed_type = input("Masukkan tipe tempat tidur: ")
    price = input("Masukkan harga per malam: ")
    capacity = input("Masukkan kapasitas kamar: ")
    status = input("Masukkan status kamar (Available/Occupied): ").strip().capitalize()

    if status not in ("Available", "Occupied"):
        print("Status kamar tidak valid.")
        return

    sql = "INSERT INTO rooms (room_id, room_type, floor, bed_type, price_per_night, capacity, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (room_id, room_type, floor, bed_type, price, capacity, status)
    dbcursor.execute(sql, val)
    konek.commit()
    print(f"Kamar {room_id} berhasil ditambahkan.")
    timer(3)


def update_room():
    room_number = input("Masukkan nomor kamar yang ingin diperbarui: ")
    sql = "SELECT * FROM rooms WHERE room_id = %s"
    dbcursor.execute(sql, (room_number,))
    result = dbcursor.fetchone()

    if result:
        print("Data kamar saat ini:")
        tampilkan([result])

        new_room_type = input("Masukkan tipe kamar baru (kosongkan jika tetap): ")
        new_floor = input("Masukkan lantai baru (kosongkan jika tetap): ")
        new_bed_type = input("Masukkan tipe tempat tidur baru (kosongkan jika tetap): ")
        new_price = input("Masukkan harga baru (kosongkan jika tetap): ")
        new_capacity = input("Masukkan kapasitas baru (kosongkan jika tetap): ")
        new_status = input("Masukkan status baru (Available/Occupied, kosongkan jika tetap): ").strip()

        if new_status:
            new_status = new_status.capitalize()
            if new_status not in ("Available", "Occupied"):
                print("Status kamar tidak valid.")
                return

        updates = []
        values = []

        if new_room_type:
            updates.append("room_type = %s")
            values.append(new_room_type)
        if new_floor:
            updates.append("floor = %s")
            values.append(new_floor)
        if new_bed_type:
            updates.append("bed_type = %s")
            values.append(new_bed_type)
        if new_price:
            updates.append("price_per_night = %s")
            values.append(new_price)
        if new_capacity:
            updates.append("capacity = %s")
            values.append(new_capacity)
        if new_status:
            updates.append("status = %s")
            values.append(new_status)

        if updates:
            sql_update = f"UPDATE rooms SET {', '.join(updates)} WHERE room_id = %s"
            values.append(room_number)
            dbcursor.execute(sql_update, tuple(values))
            konek.commit()
            print(f"Kamar {room_number} berhasil diperbarui.")
        else:
            print("Tidak ada perubahan yang dimasukkan.")
    else:
        print(f"Kamar dengan nomor {room_number} tidak ditemukan.")

    timer(3)


def delete_room():
    room_number = input("Masukkan nomor kamar yang ingin dihapus: ")

    dbcursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_number,))
    result = dbcursor.fetchone()

    if result:
        print("Data kamar yang akan dihapus:")
        tampilkan([result])

        dbcursor.execute("SELECT 1 FROM bookings WHERE room_id = %s", (room_number,))
        if dbcursor.fetchone():
            print("Kamar tidak dapat dihapus karena sudah memiliki data booking.")
            timer(3)
            return

        confirm = input("Apakah Anda yakin ingin menghapus kamar ini? (Y/N): ").upper()
        if confirm == "Y":
            dbcursor.execute("DELETE FROM rooms WHERE room_id = %s", (room_number,))
            konek.commit()
            print(f"Kamar {room_number} berhasil dihapus.")
        else:
            print("Penghapusan dibatalkan.")
    else:
        print(f"Kamar dengan nomor {room_number} tidak ditemukan.")

    timer(3)


def room_menu(role):
    while True:
        print("\n--- Room Management Menu ---")
        print("1. View Rooms")

        if role == "admin":
            print("2. Add Room")
            print("3. Update Room")
            print("4. Delete Room")

        print("0. Back to Main Menu")
        choice = input("Masukkan pilihan: ")

        if choice == "1":
            view_rooms()
        elif choice == "2" and role == "admin":
            add_room()
        elif choice == "3" and role == "admin":
            update_room()
        elif choice == "4" and role == "admin":
            delete_room()
        elif choice == "0":
            break
        else:
            print("Pilihan tidak tersedia atau akses ditolak.")

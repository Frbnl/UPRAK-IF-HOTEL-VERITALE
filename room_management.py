from conn import konek, dbcursor, tampilkan
from datetime import datetime
import time as count
def timer(seconds):
    for i in range(seconds, 0, -1):
        print(f"Program akan kembali dalam {i} detik...", end="\r")
        count.sleep(1)
    print(" " * 50, end="\r")  # Clear the line after countdown

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
    status = input("Masukkan status kamar (Available/Occupied): ").upper()

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
        print(
            f"Data kamar ditemukan: ID Kamar: {result[0]}, "
            f"Tipe Kamar: {result[1]}, Harga: {result[4]}, Status: {result[6]}"
        )
        new_room_type = input("Masukkan tipe kamar baru (kosongkan jika tidak ingin mengubah): ")
        new_price = input("Masukkan harga kamar baru (kosongkan jika tidak ingin mengubah): ")
        new_status = input("Masukkan status kamar baru (Available/Occupied, kosongkan jika tidak ingin mengubah): ")

        updates = []
        values = []
        if new_room_type:
            updates.append("room_type = %s")
            values.append(new_room_type)
        if new_price:
            updates.append("price_per_night = %s")
            values.append(new_price)
        if new_status:
            updates.append("status = %s")
            values.append(new_status)

        if updates:
            sql_update = f"UPDATE rooms SET {', '.join(updates)} WHERE room_id = %s"
            dbcursor.execute(sql_update, (*values, room_number))
            konek.commit()
            print(f"Kamar {room_number} berhasil diperbarui.")
        else:
            print("Tidak ada perubahan yang dimasukkan.")
    else:
        print(f"Kamar dengan nomor {room_number} tidak ditemukan.")
    timer(3)
def room_menu():
    while True:
        print("\n--- Room Management Menu ---")
        print("1. View Rooms")
        print("2. Add Room Type")
        print("3. Update Room")
        print("4. Delete Room")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            view_rooms()
        elif choice == "2":
            add_room()
        elif choice == "3":
            update_room()
        elif choice == "4":
            delete_room()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")
from datetime import datetime

from conn import konek, dbcursor, tampilkan


def _read_date(prompt, current=None):
    while True:
        value = input(prompt).strip()
        if not value and current is not None:
            return current
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            print("Format tanggal tidak sesuai. Gunakan YYYY-MM-DD.")


def _room_price(room_id):
    dbcursor.execute(
        "SELECT price_per_night FROM rooms WHERE room_id = %s",
        (room_id,),
    )
    result = dbcursor.fetchone()
    return result[0] if result else None


def _room_has_conflict(room_id, check_in, check_out, booking_id=None):
    sql = (
        "SELECT 1 FROM bookings "
        "WHERE room_id = %s "
        "AND check_in < %s AND check_out > %s "
        "AND COALESCE(booking_status, '') NOT IN ('Checked Out', 'Cancelled')"
    )
    parameters = [room_id, check_out, check_in]
    if booking_id is not None:
        sql += " AND booking_id <> %s"
        parameters.append(booking_id)
    dbcursor.execute(sql, tuple(parameters))
    return dbcursor.fetchone() is not None


def create_booking(guest_id=None):
    if guest_id is None:
        guest_id = input("Masukkan ID tamu: ").strip()
    guest_id = str(guest_id).strip()
    check_in = _read_date("Masukkan tanggal check-in (YYYY-MM-DD): ")
    check_out = _read_date("Masukkan tanggal check-out (YYYY-MM-DD): ")

    if not guest_id:
        print("ID tamu wajib diisi.")
        return
    if check_out <= check_in:
        print("Tanggal check-out harus setelah tanggal check-in.")
        return

    dbcursor.execute("SELECT 1 FROM guests WHERE guest_id = %s", (guest_id,))
    if dbcursor.fetchone() is None:
        print(f"Tamu dengan ID {guest_id} tidak ditemukan.")
        return

    dbcursor.execute(
        "SELECT rooms.room_id, rooms.room_type, rooms.price_per_night "
        "FROM rooms "
        "WHERE rooms.status = 'Available' AND rooms.price_per_night IS NOT NULL "
        "AND NOT EXISTS ("
        "SELECT 1 FROM bookings "
        "WHERE bookings.room_id = rooms.room_id "
        "AND bookings.check_in < %s AND bookings.check_out > %s "
        "AND COALESCE(bookings.booking_status, '') "
        "NOT IN ('Checked Out', 'Cancelled')"
        ") ORDER BY rooms.room_id",
        (check_out, check_in),
    )
    available_rooms = dbcursor.fetchall()
    if not available_rooms:
        print("Tidak ada kamar yang tersedia pada tanggal tersebut.")
        return

    print("\n--- Kamar Tersedia ---")
    tampilkan(available_rooms)
    room_id = input("Pilih ID kamar: ").strip()
    selected_room = next(
        (room for room in available_rooms if str(room[0]) == room_id),
        None,
    )
    if selected_room is None:
        print("ID kamar tidak termasuk dalam daftar kamar yang tersedia.")
        return

    nights = (check_out - check_in).days
    total_payment = selected_room[2] * nights
    channel = input("Masukkan channel booking: ").strip()
    print("Pilih metode pembayaran:")
    print("1. QRIS")
    print("2. Bank Transfer")
    payment_choice = input("Masukkan pilihan: ").strip()
    payment_methods = {"1": "QRIS", "2": "Bank Transfer"}
    if payment_choice not in payment_methods:
        print("Pilihan metode pembayaran tidak valid.")
        return
    payment_method = payment_methods[payment_choice]

    dbcursor.execute("SELECT MAX(CAST(booking_id AS UNSIGNED)) FROM bookings")
    max_booking_id = dbcursor.fetchone()[0] or 0
    booking_id = int(max_booking_id) + 1
    while True:
        dbcursor.execute(
            "SELECT 1 FROM bookings WHERE booking_id = %s",
            (booking_id,),
        )
        if dbcursor.fetchone() is None:
            break
        booking_id += 1

    sql = (
        "INSERT INTO bookings "
        "(booking_id, guest_id, room_id, check_in, check_out, nights, channel, "
        "total_payment, payment_method, booking_status, rating) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    values = (
        booking_id,
        guest_id,
        room_id,
        check_in,
        check_out,
        nights,
        channel,
        total_payment,
        payment_method,
        "Booked",
        None,
    )
    dbcursor.execute(sql, values)
    konek.commit()
    print(f"Booking {booking_id} berhasil dibuat untuk {nights} malam.")


def view_bookings():
    sql = """
    SELECT
        bookings.booking_id,
        guests.guest_name,
        rooms.room_id,
        rooms.room_type,
        bookings.check_in,
        bookings.check_out,
        bookings.total_payment,
        bookings.booking_status
    FROM bookings
    INNER JOIN guests
        ON bookings.guest_id = guests.guest_id
    INNER JOIN rooms
        ON bookings.room_id = rooms.room_id
    """
    dbcursor.execute(sql)
    results = dbcursor.fetchall()

    if results:
        print("\n--- Daftar Booking ---")
        tampilkan(results)
    else:
        print("Tidak ada booking yang ditemukan.")


def update_booking():
    booking_id = input("Masukkan ID booking yang ingin diperbarui: ").strip()
    dbcursor.execute(
        "SELECT booking_id, guest_id, room_id, check_in, check_out, nights, "
        "channel, total_payment, payment_method, booking_status, rating "
        "FROM bookings WHERE booking_id = %s",
        (booking_id,),
    )
    booking = dbcursor.fetchone()
    if booking is None:
        print(f"Booking dengan ID {booking_id} tidak ditemukan.")
        return

    print("Data booking saat ini:")
    tampilkan([booking])
    guest_id = input("ID tamu baru (kosongkan untuk tetap): ").strip() or booking[1]
    room_id = input("ID kamar baru (kosongkan untuk tetap): ").strip() or booking[2]
    check_in = _read_date(
        "Tanggal check-in baru (YYYY-MM-DD, kosongkan untuk tetap): ",
        booking[3],
    )
    check_out = _read_date(
        "Tanggal check-out baru (YYYY-MM-DD, kosongkan untuk tetap): ",
        booking[4],
    )
    channel = input("Channel baru (kosongkan untuk tetap): ").strip() or booking[6]
    payment_method = (
        input("Metode pembayaran baru (kosongkan untuk tetap): ").strip()
        or booking[8]
    )

    if check_out <= check_in:
        print("Tanggal check-out harus setelah tanggal check-in.")
        return

    dbcursor.execute("SELECT 1 FROM guests WHERE guest_id = %s", (guest_id,))
    if dbcursor.fetchone() is None:
        print(f"Tamu dengan ID {guest_id} tidak ditemukan.")
        return

    price_per_night = _room_price(room_id)
    if price_per_night is None:
        print(f"Kamar dengan ID {room_id} tidak ditemukan atau belum memiliki harga.")
        return

    if _room_has_conflict(room_id, check_in, check_out, booking_id):
        print("Kamar sudah memiliki booking pada rentang tanggal tersebut.")
        return

    nights = (check_out - check_in).days
    total_payment = price_per_night * nights
    dbcursor.execute(
        "UPDATE bookings SET guest_id = %s, room_id = %s, check_in = %s, "
        "check_out = %s, nights = %s, channel = %s, total_payment = %s, "
        "payment_method = %s WHERE booking_id = %s",
        (
            guest_id,
            room_id,
            check_in,
            check_out,
            nights,
            channel,
            total_payment,
            payment_method,
            booking_id,
        ),
    )
    konek.commit()
    print(f"Booking {booking_id} berhasil diperbarui.")


def check_out_booking():
    booking_id = input("Masukkan ID booking yang akan check-out: ").strip()
    dbcursor.execute(
        "SELECT booking_status FROM bookings WHERE booking_id = %s",
        (booking_id,),
    )
    booking = dbcursor.fetchone()
    if booking is None:
        print(f"Booking dengan ID {booking_id} tidak ditemukan.")
        return
    if booking[0] == "Checked Out":
        print(f"Booking {booking_id} sudah berstatus Checked Out.")
        return

    dbcursor.execute(
        "UPDATE bookings SET booking_status = %s WHERE booking_id = %s",
        ("Checked Out", booking_id),
    )
    konek.commit()
    print(f"Booking {booking_id} berhasil di-check-out.")


def booking_menu():
    while True:
        print("\n--- Booking Management ---")
        print("1. Create booking")
        print("2. View bookings")
        print("3. Update booking")
        print("4. Check out")
        print("0. Back to main menu")
        pilihan_booking = input("Masukkan pilihan: ")
        if pilihan_booking == "1":
            create_booking()
        elif pilihan_booking == "2":
            view_bookings()
        elif pilihan_booking == "3":
            update_booking()
        elif pilihan_booking == "4":
            check_out_booking()
        elif pilihan_booking == "0":
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

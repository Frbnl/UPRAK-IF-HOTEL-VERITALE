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


def create_booking():
    booking_id = input("Masukkan ID booking: ").strip()
    guest_id = input("Masukkan ID tamu: ").strip()
    room_id = input("Masukkan ID kamar: ").strip()
    check_in = _read_date("Masukkan tanggal check-in (YYYY-MM-DD): ")
    check_out = _read_date("Masukkan tanggal check-out (YYYY-MM-DD): ")

    if not booking_id or not guest_id or not room_id:
        print("ID booking, tamu, dan kamar wajib diisi.")
        return
    if check_out <= check_in:
        print("Tanggal check-out harus setelah tanggal check-in.")
        return

    dbcursor.execute("SELECT 1 FROM bookings WHERE booking_id = %s", (booking_id,))
    if dbcursor.fetchone():
        print(f"Booking dengan ID {booking_id} sudah ada.")
        return

    dbcursor.execute("SELECT 1 FROM guests WHERE guest_id = %s", (guest_id,))
    if dbcursor.fetchone() is None:
        print(f"Tamu dengan ID {guest_id} tidak ditemukan.")
        return

    price_per_night = _room_price(room_id)
    if price_per_night is None:
        print(f"Kamar dengan ID {room_id} tidak ditemukan atau belum memiliki harga.")
        return

    if _room_has_conflict(room_id, check_in, check_out):
        print("Kamar sudah memiliki booking pada rentang tanggal tersebut.")
        return

    nights = (check_out - check_in).days
    total_payment = price_per_night * nights
    channel = input("Masukkan channel booking: ").strip()
    payment_method = input("Masukkan metode pembayaran: ").strip()

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
    dbcursor.execute("SELECT * FROM bookings")
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

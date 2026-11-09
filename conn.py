import mysql.connector

konek = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hotel_veritale"
)
dbcursor = konek.cursor()
if dbcursor:    
    print("Koneksi ke database berhasil.")
    
def tampilkan(results):
    print(" | ".join(dbcursor.column_names))
    print("-" * 60)
    for baris in results:
        print(" | ".join("NULL" if x is None else str(x) for x in baris))

def menu_template():
    print("\n===== HOTEL VERITALE =====")
    print("1. Guest account management")
    print("0. Exit")

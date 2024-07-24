import tkinter as tk
from tkinter import messagebox
import sqlite3
import shutil
from datetime import datetime

# Veritabanı bağlantısı ve tablo oluşturma
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    type TEXT,
    category TEXT,
    amount REAL,
    date TEXT,
    description TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY,
    category TEXT,
    amount REAL
)
''')
conn.commit()
conn.close()

# Pencere oluşturma
root = tk.Tk()
root.title("Kişisel Finans Yönetimi")

# Gelir ve gider girişi için alanlar
tk.Label(root, text="Tür (Gelir/Gider):").grid(row=0, column=0)
type_entry = tk.Entry(root)
type_entry.grid(row=0, column=1)

tk.Label(root, text="Kategori:").grid(row=1, column=0)
category_entry = tk.Entry(root)
category_entry.grid(row=1, column=1)

tk.Label(root, text="Miktar:").grid(row=2, column=0)
amount_entry = tk.Entry(root)
amount_entry.grid(row=2, column=1)

tk.Label(root, text="Tarih (YYYY-MM-DD):").grid(row=3, column=0)
date_entry = tk.Entry(root)
date_entry.grid(row=3, column=1)

tk.Label(root, text="Açıklama:").grid(row=4, column=0)
description_entry = tk.Entry(root)
description_entry.grid(row=4, column=1)


# Gelir ve gider ekleme fonksiyonu
def add_transaction():
    type_ = type_entry.get().strip()
    category = category_entry.get().strip()
    amount = amount_entry.get().strip()
    date = date_entry.get().strip()
    description = description_entry.get().strip()

    if type_ not in ["Gelir", "Gider"]:
        messagebox.showerror("Hata", "Tür sadece 'Gelir' veya 'Gider' olabilir!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Hata", "Miktar sayısal bir değer olmalıdır!")
        return

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (type, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                   (type_, category, amount, date, description))
    conn.commit()
    conn.close()

    messagebox.showinfo("Başarılı", "İşlem eklendi!")


tk.Button(root, text="Ekle", command=add_transaction).grid(row=5, column=1)


# Kategori bazında özetleme fonksiyonu
def show_category_summary():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    rows = cursor.fetchall()
    conn.close()

    summary = "Kategori Bazında Toplamlar:\n"
    for row in rows:
        summary += f"{row[0]}: {row[1]}\n"

    messagebox.showinfo("Kategori Özeti", summary)


tk.Button(root, text="Kategori Özeti Göster", command=show_category_summary).grid(row=6, column=1)


# Bütçe belirleme fonksiyonu
def set_budget():
    category = category_entry.get().strip()
    budget = amount_entry.get().strip()

    try:
        budget = float(budget)
    except ValueError:
        messagebox.showerror("Hata", "Bütçe sayısal bir değer olmalıdır!")
        return

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO budgets (category, amount) VALUES (?, ?)", (category, budget))
    conn.commit()
    conn.close()

    messagebox.showinfo("Başarılı", f"{category} kategorisi için bütçe belirlendi!")


tk.Button(root, text="Bütçe Belirle", command=set_budget).grid(row=7, column=1)


# Kategori bazında harcamaları görüntüleme fonksiyonu
def show_expenses_by_category():
    category = category_entry.get().strip()

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT amount, date, description FROM transactions WHERE type='Gider' AND category=?", (category,))
    rows = cursor.fetchall()
    conn.close()

    summary = f"{category} Kategorisi İçin Harcamalar:\n"
    for row in rows:
        summary += f"{row[1]} - {row[0]} TL - {row[2]}\n"

    messagebox.showinfo("Kategori Harcamaları", summary)


tk.Button(root, text="Kategori Harcamalarını Göster", command=show_expenses_by_category).grid(row=8, column=1)


# Veritabanını yedekleme fonksiyonu
def backup_database():
    shutil.copy('finance.db', 'finance_backup.db')
    messagebox.showinfo("Yedekleme", "Veritabanı yedeklendi!")


tk.Button(root, text="Veritabanı Yedekle", command=backup_database).grid(row=9, column=1)


# Aylık özet raporları fonksiyonu
def show_monthly_summary():
    now = datetime.now()
    month = now.strftime("%Y-%m")

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND type='Gider'", (f'{month}%',))
    total_expenses = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND type='Gelir'", (f'{month}%',))
    total_income = cursor.fetchone()[0] or 0
    conn.close()

    summary = f"Bu Ay Toplam Gelir: {total_income}\nBu Ay Toplam Gider: {total_expenses}\nNet: {total_income - total_expenses}"
    messagebox.showinfo("Aylık Özeti", summary)


tk.Button(root, text="Aylık Özeti Göster", command=show_monthly_summary).grid(row=10, column=1)

# Arayüz döngüsü
root.mainloop()

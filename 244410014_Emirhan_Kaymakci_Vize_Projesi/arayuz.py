import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

def baglan():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Kooperatif_Sistemi"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Hata", str(err))
        return None

def uyeleri_listele():
    for row in tablo_uyeler.get_children():
        tablo_uyeler.delete(row)
    conn = baglan()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT uye_id, tc_no, ad, soyad, telefon, durum FROM Uyeler")
        for kayit in cursor.fetchall():
            tablo_uyeler.insert("", tk.END, values=kayit)
        cursor.close()
        conn.close()

def odemeleri_listele():
    for row in tablo_odemeler.get_children():
        tablo_odemeler.delete(row)
    conn = baglan()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tc_no, ad, soyad, ay, belirlenen_tutar, odenen_tutar, odeme_tarihi FROM V_Odeme_Gecmisi")
        for kayit in cursor.fetchall():
            tablo_odemeler.insert("", tk.END, values=kayit)
        cursor.close()
        conn.close()

def uye_ekle():
    tc = entry_tc.get()
    ad = entry_ad.get()
    soyad = entry_soyad.get()
    tel = entry_tel.get()
    
    if not tc or not ad or not soyad:
        messagebox.showwarning("Uyarı", "Eksik bilgi girmeyiniz!")
        return
    
    if len(tc) != 11 or not tc.isdigit():
        messagebox.showerror("Doğrulama Hatası", "TC No 11 haneli ve rakam olmalıdır!")
        return

    conn = baglan()
    if conn:
        cursor = conn.cursor()
        sql = "INSERT INTO Uyeler (tc_no, ad, soyad, telefon) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(sql, (tc, ad, soyad, tel))
            conn.commit()
            messagebox.showinfo("Başarılı", "Yeni üye sisteme kaydedildi!")
            entry_tc.delete(0, tk.END)
            entry_ad.delete(0, tk.END)
            entry_soyad.delete(0, tk.END)
            entry_tel.delete(0, tk.END)
            uyeleri_listele()
            combobox_guncelle()
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", str(err))
        finally:
            cursor.close()
            conn.close()

def uye_sil():
    secili = tablo_uyeler.selection()
    if not secili:
        messagebox.showwarning("Uyarı", "Silmek istediğiniz üyeyi tablodan seçiniz!")
        return
    
    cevap = messagebox.askyesno("Onay", "Seçili üyeyi ve tüm mali kayıtlarını silmek istediğinize emin misiniz?")
    if cevap:
        uye_id = tablo_uyeler.item(secili)['values'][0]
        conn = baglan()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM Uyeler WHERE uye_id = %s", (uye_id,))
                conn.commit()
                messagebox.showinfo("İşlem Tamam", "Üye sistemden tamamen kaldırıldı.")
                uyeleri_listele()
                odemeleri_listele()
                combobox_guncelle()
            except mysql.connector.Error as err:
                messagebox.showerror("Hata", str(err))
            finally:
                cursor.close()
                conn.close()

def combobox_guncelle():
    conn = baglan()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT uye_id, ad, soyad FROM Uyeler WHERE durum='Aktif'")
        cmb_uye['values'] = [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
        cursor.execute("SELECT donem_id, ay, yil FROM Aidat_Donemleri")
        cmb_donem['values'] = [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
        cursor.close()
        conn.close()

def odeme_al():
    s_uye = cmb_uye.get()
    s_donem = cmb_donem.get()
    tutar = entry_tutar.get()
    makbuz = entry_makbuz.get()
    
    if not s_uye or not s_donem or not tutar or not makbuz:
        messagebox.showwarning("Uyarı", "Lütfen tüm ödeme alanlarını doldurun!")
        return
        
    u_id = s_uye.split(" - ")[0]
    d_id = s_donem.split(" - ")[0]
    tarih = date.today().strftime("%Y-%m-%d")
    
    conn = baglan()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.callproc('Yeni_Odeme_Ekle', (u_id, d_id, tutar, tarih, makbuz))
            conn.commit()
            messagebox.showinfo("Başarılı", "Tahsilat sisteme işlendi.")
            entry_tutar.delete(0, tk.END)
            entry_makbuz.delete(0, tk.END)
            odemeleri_listele()
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", str(err))
        finally:
            cursor.close()
            conn.close()

def giris_kontrol():
    if entry_sifre.get() == "1234":
        pencere_login.destroy()
        ana_panel_ac()
    else:
        messagebox.showerror("Hatalı Şifre", "Giriş yetkiniz yok!")

def ana_panel_ac():
    global tablo_uyeler, tablo_odemeler, entry_tc, entry_ad, entry_soyad, entry_tel, cmb_uye, cmb_donem, entry_tutar, entry_makbuz
    
    ana_pencere = tk.Tk()
    ana_pencere.title("Kooperatif Yönetim Sistemi - Yetkili Paneli")
    ana_pencere.geometry("1000x650")

    notebook = ttk.Notebook(ana_pencere)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    sekme_uye = ttk.Frame(notebook)
    sekme_aidat = ttk.Frame(notebook)
    notebook.add(sekme_uye, text=" Üye İşlemleri ")
    notebook.add(sekme_aidat, text=" Aidat & Tahsilat ")

    f_uye_ust = tk.Frame(sekme_uye)
    f_uye_ust.pack(pady=15)
    tk.Label(f_uye_ust, text="TC No:").grid(row=0, column=0, padx=5, pady=5)
    entry_tc = tk.Entry(f_uye_ust, width=20)
    entry_tc.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(f_uye_ust, text="Ad:").grid(row=0, column=2, padx=5, pady=5)
    entry_ad = tk.Entry(f_uye_ust, width=20)
    entry_ad.grid(row=0, column=3, padx=5, pady=5)
    tk.Label(f_uye_ust, text="Soyad:").grid(row=1, column=0, padx=5, pady=5)
    entry_soyad = tk.Entry(f_uye_ust, width=20)
    entry_soyad.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(f_uye_ust, text="Telefon:").grid(row=1, column=2, padx=5, pady=5)
    entry_tel = tk.Entry(f_uye_ust, width=20)
    entry_tel.grid(row=1, column=3, padx=5, pady=5)
    
    btn_f = tk.Frame(sekme_uye)
    btn_f.pack(pady=5)
    tk.Button(btn_f, text="Sisteme Kaydet", bg="#28a745", fg="white", width=20, command=uye_ekle).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_f, text="Seçili Üyeyi Sil", bg="#dc3545", fg="white", width=20, command=uye_sil).pack(side=tk.LEFT, padx=10)

    cols = ("ID", "TC", "Ad", "Soyad", "Telefon", "Durum")
    tablo_uyeler = ttk.Treeview(sekme_uye, columns=cols, show="headings", height=15)
    for c in cols:
        tablo_uyeler.heading(c, text=c)
        tablo_uyeler.column(c, width=150, anchor=tk.CENTER)
    tablo_uyeler.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    f_aidat_ust = tk.Frame(sekme_aidat)
    f_aidat_ust.pack(pady=15)
    tk.Label(f_aidat_ust, text="Üye:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    cmb_uye = ttk.Combobox(f_aidat_ust, width=30, state="readonly")
    cmb_uye.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(f_aidat_ust, text="Dönem:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    cmb_donem = ttk.Combobox(f_aidat_ust, width=30, state="readonly")
    cmb_donem.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(f_aidat_ust, text="Tutar (TL):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_tutar = tk.Entry(f_aidat_ust, width=33)
    entry_tutar.grid(row=2, column=1, padx=5, pady=5)
    tk.Label(f_aidat_ust, text="Makbuz:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry_makbuz = tk.Entry(f_aidat_ust, width=33)
    entry_makbuz.grid(row=3, column=1, padx=5, pady=5)
    tk.Button(f_aidat_ust, text="Tahsilatı Kaydet", bg="#007bff", fg="white", width=30, command=odeme_al).grid(row=4, column=0, columnspan=2, pady=10)

    cols_a = ("TC No", "Ad", "Soyad", "Ay", "Beklenen", "Ödenen", "Tarih")
    tablo_odemeler = ttk.Treeview(sekme_aidat, columns=cols_a, show="headings", height=15)
    for c in cols_a:
        tablo_odemeler.heading(c, text=c)
        tablo_odemeler.column(c, width=130, anchor=tk.CENTER)
    tablo_odemeler.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    uyeleri_listele()
    odemeleri_listele()
    combobox_guncelle()
    ana_pencere.mainloop()

pencere_login = tk.Tk()
pencere_login.title("Sistem Girişi")
pencere_login.geometry("300x180")
tk.Label(pencere_login, text="Yönetici Şifresi", font=("Arial", 12, "bold")).pack(pady=15)
entry_sifre = tk.Entry(pencere_login, show="*", width=20, justify='center')
entry_sifre.pack(pady=5)
tk.Button(pencere_login, text="Giriş Yap", bg="#333", fg="white", width=15, command=giris_kontrol).pack(pady=15)

pencere_login.mainloop()
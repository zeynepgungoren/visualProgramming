import sys
import os
import platform
import subprocess
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QDateEdit, QMessageBox, QGridLayout, QGroupBox,
    QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt, QDate
from functools import partial

# PDF Oluşturma ve Otomatik Açma Fonksiyonu
def pdf_olustur(otel_bilgileri, kisi_bilgileri, toplam_gun_sayisi):
    filename = "Rezervasyon_Detayı.pdf"
    # Font yükleme
    font_path = os.path.join(os.path.dirname(__file__), "Arial.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        font_name = 'Arial'
    else:
        font_name = "Helvetica"

    # PDF belgesi ve stil
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontName = font_name
    title_style.fontSize = 18
    title_style.textColor = colors.HexColor("#000000")

    elements = []

    # Başlık
    elements.append(Paragraph("Rezervasyon Detayları", title_style))
    elements.append(Spacer(1, 12))

    # Tablo verisi
    data = [
        ["Özellik", "Değer"],
        ["Otel", otel_bilgileri['isim']],
        ["Günlük Fiyat", f"{otel_bilgileri['fiyat']} ₺"],
        ["Kişi Sayısı", str(kisi_bilgileri['kisi_sayisi'])],
        ["Gün Sayısı", str(toplam_gun_sayisi)],
        ["Kişiler", "\n".join(kisi_bilgileri['kisiler'])],
        ["Toplam Tutar", f"{otel_bilgileri['fiyat'] * kisi_bilgileri['kisi_sayisi'] * toplam_gun_sayisi} ₺"]
    ]

    # Tablo stil
    table = Table(data, colWidths=[150, 350])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#030703")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), font_name),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F1F8E9")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#388E3C")),
        ('FONTNAME', (0,1), (-1,-1), font_name),
        ('FONTSIZE', (0,1), (-1,-1), 12),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
    ])
    table.setStyle(style)

    elements.append(table)

    # PDF oluşturma
    doc.build(elements)

    # Otomatik açma
    try:
        if platform.system() == 'Windows':
            os.startfile(filename)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', filename])
        else:
            subprocess.call(['xdg-open', filename])
    except Exception as e:
        print(f"PDF açılamadı: {e}")

# Ana Pencere: Hoşgeldiniz
class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rezervasyon")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget { background-color: #f0f5f0; font-family: Arial; font-size: 20px; }
            QLabel { color: #2E7D32; font-weight: bold; }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 10px;
                padding: 15px 30px; font-size: 18px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Hoş Geldiniz!")
        label.setAlignment(Qt.AlignCenter)
        label1 = QLabel("Otelinizi seçmeye başlayabilirsiniz")
        label1.setAlignment(Qt.AlignCenter)
        start_button = QPushButton("Başla")
        start_button.clicked.connect(self.go_next)
        layout.addWidget(label)
        layout.addWidget(label1)
        layout.addWidget(start_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def go_next(self):
        self.next_window = Window2()
        self.next_window.show()
        self.close()

# Şehir ve Otel Seçimi
class Window2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Şehir ve Otel Seçimi")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget { background-color: #e8f5e9; font-family: 'Segoe UI'; font-size: 16px; }
            QLabel { color: #388e3c; font-weight: bold; }
            QComboBox, QSpinBox {
                color: #388e3c; font-size: 18px; padding: 10px;
                border-radius: 10px; background-color: #f1f8e9;
            }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px;
                padding: 12px 25px; font-size: 18px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        layout = QVBoxLayout()

        self.combo_sehir = QComboBox()
        self.combo_sehir.addItems(["Şehir Seçiniz...", "İstanbul", "Ankara", "İzmir"])

        self.combo_otel = QComboBox()
        self.combo_otel.addItems(["Otel Türü Seçiniz...", "3 Yıldız", "4 Yıldız", "5 Yıldız"])

        self.spin_kişi = QSpinBox()
        self.spin_kişi.setRange(1, 10)
        self.spin_kişi.setSuffix(" Kişi")
        self.spin_label = QLabel("Kişi Sayısı: 1")
        self.spin_kişi.valueChanged.connect(lambda: self.spin_label.setText(f"Kişi Sayısı: {self.spin_kişi.value()}"))

        self.btn_devam = QPushButton("Devam Et")
        self.btn_devam.clicked.connect(self.proceed)

        layout.addWidget(QLabel("Şehir Seçiniz:"))
        layout.addWidget(self.combo_sehir)
        layout.addWidget(QLabel("Otel Türü Seçiniz:"))
        layout.addWidget(self.combo_otel)
        layout.addWidget(QLabel("Kaç Kişi Kalacak?"))
        layout.addWidget(self.spin_kişi)
        layout.addWidget(self.spin_label)
        layout.addWidget(self.btn_devam, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def proceed(self):
        sehir = self.combo_sehir.currentText()
        otel = self.combo_otel.currentText()
        kisi = self.spin_kişi.value()
        if sehir.startswith("Şehir") or otel.startswith("Otel") or sehir == "Şehir Seçiniz..." or otel == "Otel Türü Seçiniz...":
            QMessageBox.warning(self, "Eksik Seçim", "Lütfen tüm alanları doldurun.")
            return
        self.next_win = DateWindow(sehir, otel, kisi)
        self.next_win.show()
        self.close()

# Tarih ve Gün Sayısı
class DateWindow(QMainWindow):
    def __init__(self, sehir, otel, kisi):
        super().__init__()
        self.setWindowTitle("Tarih Seçimi")
        self.setGeometry(100, 100, 800, 600)
        self.sehir = sehir
        self.otel = otel
        self.kisi = kisi
        self.add_back_button()
        self.setStyleSheet("""
            QWidget { background-color: #e8f5e9; font-family: 'Segoe UI'; font-size: 16px; }
            QLabel { color: #388e3c; font-weight: bold; }
            QDateEdit {
                font-size: 18px; padding: 10px; border-radius: 10px;
                background-color: #f1f8e9; border: 1px solid #388e3c;
            }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px;
                padding: 12px 25px; font-size: 18px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        layout = QVBoxLayout()

        label_info = QLabel(f"Şehir: {sehir}\nOtel: {otel}\nKişi: {kisi}")
        label_info.setAlignment(Qt.AlignCenter)

        self.date_giris = QDateEdit(QDate.currentDate())
        self.date_giris.setCalendarPopup(True)
        self.date_cikis = QDateEdit(QDate.currentDate().addDays(1))
        self.date_cikis.setCalendarPopup(True)

        self.btn_devam = QPushButton("Devam Et")
        self.btn_devam.clicked.connect(self.proceed)

        layout.addWidget(label_info)
        layout.addWidget(QLabel("Giriş Tarihi:"))
        layout.addWidget(self.date_giris)
        layout.addWidget(QLabel("Çıkış Tarihi:"))
        layout.addWidget(self.date_cikis)
        layout.addWidget(self.btn_devam, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def proceed(self):
        giris = self.date_giris.date()
        cikis = self.date_cikis.date()
        days_between = giris.daysTo(cikis)
        if days_between <= 0:
            QMessageBox.critical(self, "Hata", "Çıkış tarihi, giriş tarihinden sonra olmalı.")
            return
        giris_str = giris.toString("yyyy-MM-dd")
        cikis_str = cikis.toString("yyyy-MM-dd")
        self.next_window = HotelSelectionWindow(self.sehir, self.otel, giris_str, cikis_str, self.kisi, days_between)
        self.next_window.show()
        self.close()

    def add_back_button(self):
        back_btn = QPushButton("< Geri")
        back_btn.setFixedSize(80, 30)
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 14px; }")
        back_layout = QHBoxLayout()
        back_layout.addWidget(back_btn)
        back_layout.addStretch()
        main_widget = QWidget()
        main_widget.setLayout(back_layout)
        self.setCentralWidget(main_widget)

    def go_back(self):
        self.close()
        self.parent_window = Window2()
        self.parent_window.show()

# Otel Seçimi
class HotelSelectionWindow(QMainWindow):
    def __init__(self, sehir, otel_tipi, giris_tarih, cikis_tarih, kisi_sayisi, gun_sayisi):
        super().__init__()
        self.setWindowTitle("Otel Seçimi")
        self.setGeometry(100, 100, 900, 700)
        self.sehir = sehir
        self.otel_tipi = otel_tipi
        self.giris_tarih = giris_tarih
        self.cikis_tarih = cikis_tarih
        self.kisi_sayisi = kisi_sayisi
        self.gun_sayisi = gun_sayisi

        self.oteller = self.get_hotels(sehir, otel_tipi)
        self.setStyleSheet("""
            QWidget { background-color: #e8f5e9; font-family: 'Segoe UI'; font-size: 16px; }
            QLabel { color: #388e3c; font-weight: bold; }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px;
                padding: 10px 20px; font-size: 16px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)

        main_layout = QVBoxLayout()

        label_info = QLabel(f"{sehir} - {otel_tipi}\n{giris_tarih} - {cikis_tarih}\nKişi: {kisi_sayisi}\nGün: {gun_sayisi}")
        label_info.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label_info)

        # Otelleri listele
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout()
        self.scroll_widget.setLayout(self.scroll_layout)

        for i, otel in enumerate(self.oteller):
            group = QGroupBox()
            vbox = QVBoxLayout()
            lbl_isim = QLabel(otel["isim"])
            lbl_isim.setAlignment(Qt.AlignCenter)
            lbl_fiyat = QLabel(f"Günlük: {otel['fiyat']} ₺")
            lbl_fiyat.setAlignment(Qt.AlignCenter)
            btn_seç = QPushButton("Bu Oteli Seç")
            btn_seç.clicked.connect(partial(self.open_details_window, otel))
            vbox.addWidget(lbl_isim)
            vbox.addWidget(lbl_fiyat)
            vbox.addWidget(btn_seç)
            group.setLayout(vbox)
            self.scroll_layout.addWidget(group, i // 2, i % 2)

        main_layout.addWidget(self.scroll_widget)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def get_hotels(self, sehir, otel_tipi):
        # Örnek veriler
        return [
            {"isim": "Otel 1", "fiyat": 1000},
            {"isim": "Otel 2", "fiyat": 1200},
            {"isim": "Otel 3", "fiyat": 1500},
        ]

    def open_details_window(self, otel):
        self.details_window = OtelDetaylariWindow(otel, self.kisi_sayisi, self.gun_sayisi)
        self.details_window.show()

    def add_back_button(self):
        back_btn = QPushButton("< Geri")
        back_btn.setFixedSize(80, 30)
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 14px; }")
        layout = self.layout()
        back_layout = QHBoxLayout()
        back_layout.addWidget(back_btn)
        back_layout.addStretch()
        widget = QWidget()
        widget.setLayout(back_layout)
        layout.insertWidget(0, widget)

    def go_back(self):
        self.close()
        self.parent_window = DateWindow(self.sehir, self.otel_tipi, self.giris_tarih, self.cikis_tarih, self.kisi_sayisi)
        self.parent_window.show()

# Otel Detayları ve Kişi Bilgileri
class OtelDetaylariWindow(QMainWindow):
    def __init__(self, otel, kisi_sayisi, gun_sayisi):
        super().__init__()
        self.setWindowTitle("Otel Detayları")
        self.setGeometry(150, 150, 700, 700)
        self.otel = otel
        self.kisi_sayisi = kisi_sayisi
        self.gun_sayisi = gun_sayisi
        self.kisi_inputs = []

        self.setStyleSheet("""
            QWidget { background-color: #f0f5f0; font-family: Arial; font-size: 16px; }
            QLabel { color: #2E7D32; font-weight: bold; }
            QLineEdit {
                font-size: 14px; padding: 8px; border-radius: 8px; border: 1px solid #388e3c;
            }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px;
                padding: 10px 20px; font-size: 16px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Otel: {otel['isim']}"))
        layout.addWidget(QLabel(f"Günlük Fiyat: {otel['fiyat']} ₺"))
        layout.addWidget(QLabel(f"Kişi Sayısı: {self.kisi_sayisi}"))
        layout.addWidget(QLabel(f"Gün Sayısı: {self.gun_sayisi}"))

        for i in range(kisi_sayisi):
            name_edit = QLineEdit()
            name_edit.setPlaceholderText(f"Kişi {i+1} - İsim")
            phone_edit = QLineEdit()
            phone_edit.setPlaceholderText(f"Kişi {i+1} - Telefon")
            email_edit = QLineEdit()
            email_edit.setPlaceholderText(f"Kişi {i+1} - E-posta")
            self.kisi_inputs.append((name_edit, phone_edit, email_edit))
            layout.addWidget(name_edit)
            layout.addWidget(phone_edit)
            layout.addWidget(email_edit)
            if i != kisi_sayisi - 1:
                layout.addSpacing(15)

        self.btn_rezervasyon = QPushButton("Rezervasyonu Tamamla")
        self.btn_rezervasyon.clicked.connect(self.submit_reservation)
        layout.addWidget(self.btn_rezervasyon, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def submit_reservation(self):
        # Kişi bilgileri
        kisiler = [f"{n.text()}, {p.text()}, {e.text()}" for n, p, e in self.kisi_inputs]
        otel_bilgileri = {
            'isim': self.otel['isim'],
            'fiyat': self.otel['fiyat']
        }
        kisi_bilgileri = {
            'kisi_sayisi': self.kisi_sayisi,
            'kisiler': kisiler
        }
        toplam_gun_sayisi = self.gun_sayisi
        # Rezervasyon Onay
        self.onay_window = RezervasyonOnayWindow(otel_bilgileri, kisi_bilgileri, toplam_gun_sayisi)
        self.onay_window.show()
        self.close()

    def add_back_button(self):
        back_btn = QPushButton("< Geri")
        back_btn.setFixedSize(80, 30)
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 14px; }")
        layout = QVBoxLayout()
        layout.addWidget(back_btn)
        container = QWidget()
        container.setLayout(layout)
        self.layout().insertWidget(0, container)

    def go_back(self):
        self.close()
        # Geri dönüş
        self.parent_window = HotelSelectionWindow(
            sehir='', otel_tipi='', giris_tarih='', cikis_tarih='', kisi_sayisi=1, gun_sayisi=1
        )
        # Burada uygun önceki sayfaya referans verilmeli

# Rezervasyon Onay Ekranı
class RezervasyonOnayWindow(QMainWindow):
    def __init__(self, otel_bilgileri, kisi_bilgileri, toplam_gun_sayisi):
        super().__init__()
        self.setWindowTitle("Rezervasyon Onay")
        self.setGeometry(150, 150, 700, 700)
        self.setStyleSheet("""
            QWidget { background-color: #f0f5f0; font-family: Arial; font-size: 16px; }
            QLabel { color: #2E7D32; font-weight: bold; font-size: 16px; }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px;
                padding: 10px 20px; font-size: 16px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>Otel:</b> {otel_bilgileri['isim']}"))
        layout.addWidget(QLabel(f"<b>Günlük Fiyat:</b> {otel_bilgileri['fiyat']} ₺"))
        layout.addWidget(QLabel(f"<b>Kişi Sayısı:</b> {kisi_bilgileri['kisi_sayisi']}"))
        layout.addWidget(QLabel(f"<b>Gün Sayısı:</b> {toplam_gun_sayisi}"))

        for idx, kisi in enumerate(kisi_bilgileri['kisiler']):
            layout.addWidget(QLabel(f"<b>Kişi {idx+1}:</b> {kisi}"))

        toplam_fiyat = otel_bilgileri['fiyat'] * kisi_bilgileri['kisi_sayisi'] * toplam_gun_sayisi
        lbl_toplam = QLabel(f"<b>Toplam Ödenecek Tutar:</b> {toplam_fiyat} ₺")
        lbl_toplam.setStyleSheet("font-size: 18px; color: #d32f2f; margin-top: 15px;")
        layout.addWidget(lbl_toplam, alignment=Qt.AlignCenter)

        # PDF'e Dönüştür Butonu
        btn_pdf = QPushButton("PDF'e Dönüştür")
        btn_pdf.clicked.connect(lambda: pdf_olustur(otel_bilgileri, kisi_bilgileri, toplam_gun_sayisi))
        layout.addWidget(btn_pdf, alignment=Qt.AlignCenter)

        # Ödeme Yap Butonu
        btn_ode = QPushButton("Ödeme Yap")
        btn_ode.clicked.connect(lambda: self.odaOdemeSayfasinaGec(toplam_fiyat))
        layout.addWidget(btn_ode, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def odaOdemeSayfasinaGec(self, toplam_fiyat):
        self.odeme_window = OdemeEkrani(toplam_fiyat)
        self.odeme_window.show()

# Odeme Ekranı
class OdemeEkrani(QMainWindow):
    def __init__(self, toplam_tutar):
        super().__init__()
        self.toplam_tutar = toplam_tutar
        self.setWindowTitle("Ödeme Ekranı")
        self.setGeometry(300, 300, 500, 400)
        self.setStyleSheet("""
            QWidget { background-color: #f0f5f0; font-family: Arial; font-size: 16px; }
            QLabel { color: #2E7D32; font-weight: bold; font-size: 14px; }
            QLineEdit {
                font-size: 14px; padding: 8px; border-radius: 8px; border: 1px solid #388e3c;
            }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px 20px; font-size: 16px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        layout = QVBoxLayout()

        lbl_toplam = QLabel(f"Toplam Tutar: {self.toplam_tutar} ₺")
        lbl_toplam.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_toplam)

        self.kart_numarasi = QLineEdit()
        self.kart_numarasi.setPlaceholderText("Kart Numarası (16 haneli)")
        layout.addWidget(QLabel("Kart Numarası:"))
        layout.addWidget(self.kart_numarasi)

        self.kart_tarihi = QLineEdit()
        self.kart_tarihi.setPlaceholderText("Son Kullanma Tarihi (AA/YY)")
        layout.addWidget(QLabel("Son Kullanma Tarihi:"))
        layout.addWidget(self.kart_tarihi)

        self.cvv = QLineEdit()
        self.cvv.setPlaceholderText("CVV (3 haneli)")
        layout.addWidget(QLabel("CVV:"))
        layout.addWidget(self.cvv)

        btn_odeme = QPushButton("Ödeme Yap")
        btn_odeme.clicked.connect(self.odeme_tamamla)
        layout.addWidget(btn_odeme, alignment=Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def odeme_tamamla(self):
        kart_no = self.kart_numarasi.text().strip()
        tarih = self.kart_tarihi.text().strip()
        cvv = self.cvv.text().strip()

        if not kart_no or not tarih or not cvv:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return
        if len(kart_no) != 16 or not kart_no.isdigit():
            QMessageBox.warning(self, "Hatalı Kart Numarası", "Kart numarası 16 haneli olmalı.")
            return
        if len(cvv) != 3 or not cvv.isdigit():
            QMessageBox.warning(self, "Hatalı CVV", "CVV 3 haneli olmalı.")
            return

        QMessageBox.information(self, "Başarılı", "Ödeme işlemi başarıyla tamamlandı!")
        self.close()

# SQL Bağlantısı ve Veri Kaydı
def db_baglanti():
    conn = sqlite3.connect('rezervasyonlar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rezervasyon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            otel TEXT,
            fiyat REAL,
            kisi_sayisi INTEGER,
            gun_sayisi INTEGER,
            toplam_tutar REAL,
            kisiler TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn, cursor

def kaydet_veri(conn, cursor, otel, fiyat, kisi_sayisi, gun_sayisi, kisiler_list):
    toplam_fiyat = fiyat * kisi_sayisi * gun_sayisi
    kisiler_str = "\n".join(kisiler_list)
    cursor.execute('''
        INSERT INTO Rezervasyon (otel, fiyat, kisi_sayisi, gun_sayisi, toplam_tutar, kisiler)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (otel, fiyat, kisi_sayisi, gun_sayisi, toplam_fiyat, kisiler_str))
    conn.commit()

# Uygulamayı başlat
if __name__ == '__main__':
    app = QApplication(sys.argv)
    conn, cursor = db_baglanti()

    # Ana ekran
    window = WelcomeWindow()
    window.show()

    sys.exit(app.exec_())
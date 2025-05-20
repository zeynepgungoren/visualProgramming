import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QFontComboBox, QSpinBox
)
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.uic import loadUi

class MetinDuzenleyici(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('mainwindow.ui', self)

        # Dinamik olarak font seçici ve boyut kutusunu araç çubuğuna ekle
        self.fontComboBox = QFontComboBox()
        self.fontSizeSpinBox = QSpinBox()
        self.fontSizeSpinBox.setRange(8, 72)
        self.fontSizeSpinBox.setValue(12)

        self.toolBar.addWidget(self.fontComboBox)
        self.toolBar.addWidget(self.fontSizeSpinBox)

        # Menü sinyalleri
        self.actionYeni.triggered.connect(self.yeni_dosya)
        self.actionAc.triggered.connect(self.dosya_ac)
        self.actionKaydet.triggered.connect(self.dosya_kaydet)
        self.actionFarkliKaydet.triggered.connect(self.dosya_farkli_kaydet)
        self.actionCikis.triggered.connect(self.close)
        self.actionKes.triggered.connect(self.textEdit.cut)
        self.actionKopyala.triggered.connect(self.textEdit.copy)
        self.actionYapistir.triggered.connect(self.textEdit.paste)
        self.actionGeriAl.triggered.connect(self.textEdit.undo)
        self.actionIleriAl.triggered.connect(self.textEdit.redo)

        # Araç çubuğu sinyalleri
        self.actionBold.triggered.connect(self.format_metin)
        self.actionItalic.triggered.connect(self.format_metin)
        self.actionUnderline.triggered.connect(self.format_metin)
        self.fontComboBox.currentFontChanged.connect(self.font_degistir)
        self.fontSizeSpinBox.valueChanged.connect(self.boyut_degistir)

        self.dosya_yolu = None

    def yeni_dosya(self):
        self.textEdit.clear()
        self.dosya_yolu = None
        self.setWindowTitle("Basit Metin Düzenleyici")

    def dosya_ac(self):
        dosya_adi, _ = QFileDialog.getOpenFileName(self, "Metin Dosyası Aç", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)")
        if dosya_adi:
            with open(dosya_adi, 'r', encoding='utf-8') as dosya:
                self.textEdit.setText(dosya.read())
            self.dosya_yolu = dosya_adi
            self.setWindowTitle(f"{self.dosya_yolu} - Basit Metin Düzenleyici")

    def dosya_kaydet(self):
        if self.dosya_yolu is None:
            self.dosya_farkli_kaydet()
        else:
            try:
                with open(self.dosya_yolu, 'w', encoding='utf-8') as dosya:
                    dosya.write(self.textEdit.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken bir hata oluştu: {e}")

    def dosya_farkli_kaydet(self):
        dosya_adi, _ = QFileDialog.getSaveFileName(self, "Dosyayı Farklı Kaydet", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)")
        if dosya_adi:
            try:
                with open(dosya_adi, 'w', encoding='utf-8') as dosya:
                    dosya.write(self.textEdit.toPlainText())
                self.dosya_yolu = dosya_adi
                self.setWindowTitle(f"{self.dosya_yolu} - Basit Metin Düzenleyici")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken bir hata oluştu: {e}")

    def format_metin(self):
        format_ = QTextCharFormat()
        font = self.textEdit.currentFont()
        font.setBold(self.actionBold.isChecked())
        font.setItalic(self.actionItalic.isChecked())
        format_.setFontUnderline(self.actionUnderline.isChecked())
        format_.setFont(font)
        self.textEdit.mergeCurrentCharFormat(format_)

    def font_degistir(self, font):
        format_ = QTextCharFormat()
        format_.setFont(font)
        self.textEdit.mergeCurrentCharFormat(format_)

    def boyut_degistir(self, size):
        format_ = QTextCharFormat()
        font = self.textEdit.currentFont()
        font.setPointSize(size)
        format_.setFont(font)
        self.textEdit.mergeCurrentCharFormat(format_)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = MetinDuzenleyici()
    pencere.show()
    sys.exit(app.exec_())

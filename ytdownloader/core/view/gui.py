import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import yt_dlp as youtube_dl

class FormatSearchThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.finished.emit(info['formats'])
        except Exception as e:
            self.error.emit(str(e))

class DownTubeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DownTube")
        self.setMinimumSize(800, 500)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ingresa la URL del video...")
        layout.addWidget(self.url_input)
        
        # Botón para buscar formatos
        self.buscar_btn = QPushButton("Buscar Formatos")
        self.buscar_btn.clicked.connect(self.buscar_formatos)
        layout.addWidget(self.buscar_btn)
        
        # Tabla de formatos
        self.tabla_formatos = QTableWidget()
        self.tabla_formatos.setColumnCount(5)
        self.tabla_formatos.setHorizontalHeaderLabels(["ID", "Extensión", "Resolución", "Tamaño", "Tipo"])
        layout.addWidget(self.tabla_formatos)
        
        # Barra de progreso
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Botón de descarga
        self.descargar_btn = QPushButton("Descargar")
        self.descargar_btn.clicked.connect(self.descargar)
        self.descargar_btn.setEnabled(False)
        layout.addWidget(self.descargar_btn)
        
        self.formatos = []
        self.search_thread = None

    def buscar_formatos(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL")
            return
            
        # Deshabilitar el botón mientras busca
        self.buscar_btn.setEnabled(False)
        self.buscar_btn.setText("Buscando...")
        
        # Crear y configurar el thread
        self.search_thread = FormatSearchThread(url)
        self.search_thread.finished.connect(self.on_search_complete)
        self.search_thread.error.connect(self.on_search_error)
        self.search_thread.start()

    def on_search_complete(self, formatos):
        self.formatos = formatos
        
        # Actualizar tabla
        self.tabla_formatos.setRowCount(len(self.formatos))
        for i, f in enumerate(self.formatos):
            filesize = f.get('filesize', 'N/A')
            if filesize != 'N/A':
                filesize = f"{filesize/1024/1024:.1f}MB"
                
            items = [
                f.get('format_id', 'N/A'),
                f.get('ext', 'N/A'),
                f.get('resolution', 'N/A'),
                filesize,
                f.get('format_note', 'N/A')
            ]
            
            for j, item in enumerate(items):
                self.tabla_formatos.setItem(i, j, QTableWidgetItem(str(item)))
        
        self.descargar_btn.setEnabled(True)
        self.buscar_btn.setEnabled(True)
        self.buscar_btn.setText("Buscar Formatos")

    def on_search_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"Error al obtener formatos: {error_msg}")
        self.buscar_btn.setEnabled(True)
        self.buscar_btn.setText("Buscar Formatos")

    def descargar(self):
        selected_rows = self.tabla_formatos.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Por favor selecciona un formato")
            return
            
        # Obtener el format_id de la fila seleccionada
        row = selected_rows[0].row()
        format_id = self.tabla_formatos.item(row, 0).text()
        
        ydl_opts = {
            'format': format_id,
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url_input.text()])
            QMessageBox.information(self, "Éxito", "Descarga completada!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la descarga: {str(e)}")
        
        self.progress.setValue(0)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Intentar obtener el porcentaje directamente
                if '_percent_str' in d:
                    p = d['_percent_str'].replace('%','').strip()
                    self.progress.setValue(int(float(p)))
                # Alternativa: calcular el porcentaje usando bytes
                elif 'downloaded_bytes' in d and 'total_bytes' in d:
                    p = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.progress.setValue(int(p))
            except (ValueError, ZeroDivisionError):
                pass

def main():
    app = QApplication(sys.argv)
    window = DownTubeGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
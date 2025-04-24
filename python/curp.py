import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import cv2
import pytesseract
import re

# Configuración de Tesseract (ajusta la ruta según tu instalación)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Lista para almacenar registros de CURPs
registros_curp = []

# Expresión regular para validar formato de CURP
patron_curp = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$')

class CURPProcessor:
    def __init__(self):
        self.config_tesseract = '--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def preprocesar_imagen(self, ruta_imagen):
        """Preprocesa la imagen para mejorar el reconocimiento de texto"""
        try:
            # Leer la imagen
            imagen = cv2.imread(ruta_imagen)
            if imagen is None:
                raise ValueError("No se pudo cargar la imagen")
            
            # Convertir a escala de grises
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbral adaptativo
            umbral = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Redimensionar para mejor reconocimiento (opcional)
            # umbral = cv2.resize(umbral, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            return umbral
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar imagen: {str(e)}")
            return None

    def extraer_curp(self, ruta_imagen):
        """Extrae texto de la imagen y busca una CURP válida"""
        try:
            # Preprocesar imagen
            imagen_procesada = self.preprocesar_imagen(ruta_imagen)
            if imagen_procesada is None:
                return None
            
            # Usar Tesseract para OCR
            texto = pytesseract.image_to_string(imagen_procesada, config=self.config_tesseract)
            
            # Limpiar el texto y buscar posibles CURPs
            lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
            
            # Buscar una cadena que coincida con el patrón de CURP
            for linea in lineas:
                # Eliminar espacios y caracteres no válidos
                candidato = ''.join(c for c in linea if c.isalnum()).upper()
                
                # Verificar si coincide con el patrón de CURP
                if patron_curp.match(candidato):
                    return candidato
            
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error al extraer CURP: {str(e)}")
            return None

# Instancia global del procesador de CURP
procesador_curp = CURPProcessor()

def seleccionar_imagen_curp():
    """Permite al usuario seleccionar una imagen con una CURP"""
    ruta_imagen = filedialog.askopenfilename(
        title="Seleccionar imagen de CURP",
        filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    
    if ruta_imagen:
        curp_detectada = procesador_curp.extraer_curp(ruta_imagen)
        
        if curp_detectada:
            # Preguntar por el nombre asociado a la CURP
            nombre = simpledialog.askstring(
                "Registrar información",
                f"CURP detectada: {curp_detectada}\n\nIngrese el nombre completo:"
            )
            
            if nombre:
                registros_curp.append({"CURP": curp_detectada, "Nombre": nombre})
                messagebox.showinfo("Éxito", "CURP registrada correctamente")
                mostrar_registros()
            else:
                messagebox.showwarning("Advertencia", "No se ingresó nombre, registro cancelado")
        else:
            messagebox.showerror("Error", "No se pudo detectar una CURP válida en la imagen")

def mostrar_registros():
    """Muestra una ventana con todos los registros de CURPs"""
    # Verificar si la ventana ya está abierta
    if hasattr(mostrar_registros, 'ventana_registros') and mostrar_registros.ventana_registros:
        mostrar_registros.ventana_registros.destroy()

    ventana_registros = tk.Toplevel(root)
    ventana_registros.title("Registros de CURPs")
    ventana_registros.geometry("600x400")
    
    tk.Label(ventana_registros, 
             text="Registros de CURPs", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    # Crear un frame con scroll para los registros
    frame = tk.Frame(ventana_registros)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Mostrar los registros
    if not registros_curp:
        tk.Label(scrollable_frame, text="No hay registros disponibles").pack(pady=10)
    else:
        for idx, registro in enumerate(registros_curp, 1):
            tk.Label(scrollable_frame, 
                    text=f"{idx}. Nombre: {registro['Nombre']}\n   CURP: {registro['CURP']}",
                    font=("Arial", 12),
                    justify=tk.LEFT,
                    anchor="w").pack(fill=tk.X, pady=5, padx=5)
    
    # Guardar referencia de la ventana
    mostrar_registros.ventana_registros = ventana_registros

def abrir_registro():
    """Abre la ventana de registro"""
    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Registro de CURP")
    ventana_registro.geometry("400x200")
    ventana_registro.configure(bg="#f0f0f0")
    
    tk.Label(ventana_registro, 
             text="Registrar nueva CURP", 
             font=("Arial", 14, "bold"),
             bg="#f0f0f0").pack(pady=20)
    
    btn_estilo = {
        'font': ('Arial', 12),
        'bg': '#4CAF50',
        'fg': 'white',
        'activebackground': '#45a049',
        'padx': 20,
        'pady': 10
    }
    
    btn_subir = tk.Button(ventana_registro, 
                         text="Subir Imagen de CURP", 
                         command=seleccionar_imagen_curp,
                         **btn_estilo)
    btn_subir.pack(pady=10)

# Crear ventana principal
root = tk.Tk()
root.title("Sistema de Detección de CURP")
root.geometry("500x300")
root.configure(bg="#f0f0f0")

# Estilo para la ventana principal
tk.Label(root, 
         text="Sistema de Detección de CURP", 
         font=("Arial", 20, "bold"),
         bg="#f0f0f0").pack(pady=30)

btn_estilo_principal = {
    'font': ('Arial', 14),
    'bg': '#2196F3',
    'fg': 'white',
    'activebackground': '#0b7dda',
    'width': 25,
    'pady': 10
}

tk.Button(root, 
          text="Registrar nueva CURP", 
          command=abrir_registro,
          **btn_estilo_principal).pack(pady=10)

tk.Button(root, 
          text="Ver registros de CURPs", 
          command=mostrar_registros,
          **btn_estilo_principal).pack(pady=10)

# Ejecutar la aplicación
root.mainloop()
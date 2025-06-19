"""
Programa gráfico para manejo de audio estéreo y mono usando Tkinter.
Autor: [Tu nombre]
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import simpleaudio as sa
import os

from estereo import estereo2mono, mono2estereo, codEstereo, decEstereo


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("APA-T6: Manejo de Señales Estéreo")
        self.geometry("700x400")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.add_tabs()

    def add_tabs(self):
        self.tab1 = EstereoAMonoTab(self.notebook)
        self.tab2 = MonoAEstereoTab(self.notebook)
        self.tab3 = CodificaTab(self.notebook)
        self.tab4 = DecodificaTab(self.notebook)

        self.notebook.add(self.tab1, text="Estéreo a Mono")
        self.notebook.add(self.tab2, text="Mono a Estéreo")
        self.notebook.add(self.tab3, text="Codifica Estéreo")
        self.notebook.add(self.tab4, text="Descodifica Estéreo")


class EstereoAMonoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.ficEste = ""
        self.ficMono = ""

        self.label = ttk.Label(self, text="Conversión de estéreo a mono")
        self.label.pack(pady=10)

        self.btn_cargar = ttk.Button(self, text="Seleccionar archivo estéreo", command=self.seleccionar_estereo)
        self.btn_cargar.pack()

        self.canal_var = tk.IntVar(value=2)
        for i, txt in enumerate(["Canal Izquierdo", "Canal Derecho", "Semisuma (L+R)/2", "Semidiferencia (L-R)/2"]):
            ttk.Radiobutton(self, text=txt, variable=self.canal_var, value=i).pack(anchor="w")

        self.btn_convertir = ttk.Button(self, text="Convertir y guardar", command=self.convertir)
        self.btn_convertir.pack(pady=10)

        self.btn_escuchar = ttk.Button(self, text="Escuchar salida", command=self.escuchar_salida)
        self.btn_escuchar.pack()

    def seleccionar_estereo(self):
        self.ficEste = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if self.ficEste:
            messagebox.showinfo("Archivo seleccionado", f"{self.ficEste}")

    def convertir(self):
        if not self.ficEste:
            messagebox.showerror("Error", "Debe seleccionar un archivo de entrada")
            return
        self.ficMono = filedialog.asksaveasfilename(defaultextension=".wav")
        if self.ficMono:
            estereo2mono(self.ficEste, self.ficMono, canal=self.canal_var.get())
            messagebox.showinfo("Éxito", f"Archivo guardado en {self.ficMono}")

    def escuchar_salida(self):
        if self.ficMono and os.path.exists(self.ficMono):
            sa.WaveObject.from_wave_file(self.ficMono).play()
        else:
            messagebox.showerror("Error", "No hay archivo de salida disponible")


class MonoAEstereoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.ficIzq = ""
        self.ficDer = ""
        self.ficEste = ""

        ttk.Button(self, text="Seleccionar canal izquierdo", command=self.sel_izq).pack()
        ttk.Button(self, text="Seleccionar canal derecho", command=self.sel_der).pack()

        ttk.Button(self, text="Convertir y guardar", command=self.convertir).pack(pady=10)
        ttk.Button(self, text="Escuchar salida", command=self.escuchar).pack()

    def sel_izq(self):
        self.ficIzq = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

    def sel_der(self):
        self.ficDer = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

    def convertir(self):
        if not self.ficIzq or not self.ficDer:
            messagebox.showerror("Error", "Selecciona ambos canales mono")
            return
        self.ficEste = filedialog.asksaveasfilename(defaultextension=".wav")
        if self.ficEste:
            mono2estereo(self.ficIzq, self.ficDer, self.ficEste)
            messagebox.showinfo("Éxito", f"Archivo estéreo guardado en {self.ficEste}")

    def escuchar(self):
        if self.ficEste and os.path.exists(self.ficEste):
            sa.WaveObject.from_wave_file(self.ficEste).play()
        else:
            messagebox.showerror("Error", "Archivo de salida no disponible")


class CodificaTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.ficEste = ""
        self.ficCod = ""

        ttk.Button(self, text="Seleccionar archivo estéreo", command=self.sel_este).pack()
        ttk.Button(self, text="Codificar y guardar", command=self.codificar).pack(pady=10)

    def sel_este(self):
        self.ficEste = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

    def codificar(self):
        if not self.ficEste:
            messagebox.showerror("Error", "Archivo no seleccionado")
            return
        self.ficCod = filedialog.asksaveasfilename(defaultextension=".wav")
        if self.ficCod:
            codEstereo(self.ficEste, self.ficCod)
            messagebox.showinfo("Éxito", f"Archivo codificado guardado en {self.ficCod}")


class DecodificaTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.ficCod = ""
        self.ficEste = ""

        ttk.Button(self, text="Seleccionar archivo codificado", command=self.sel_cod).pack()
        ttk.Button(self, text="Decodificar y guardar", command=self.decodificar).pack(pady=10)

    def sel_cod(self):
        self.ficCod = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

    def decodificar(self):
        if not self.ficCod:
            messagebox.showerror("Error", "Archivo no seleccionado")
            return
        self.ficEste = filedialog.asksaveasfilename(defaultextension=".wav")
        if self.ficEste:
            decEstereo(self.ficCod, self.ficEste)
            messagebox.showinfo("Éxito", f"Archivo estéreo guardado en {self.ficEste}")


if __name__ == '__main__':
    app = App()
    app.mainloop()

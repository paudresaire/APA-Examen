
import tkinter as tk
from tkinter import filedialog
from horas import normalizaHoras 

def main():
    tk.Tk().withdraw()

    print("Selecciona el fichero de entrada...")
    ficText = filedialog.askopenfilename(title="Selecciona el fichero de entrada",
                                         filetypes=[("Text files", "*.txt")])
    if not ficText:
        print("No se seleccionó ningún fichero de entrada.")
        return

    print("Selecciona el nombre del fichero de salida...")
    ficNorm = filedialog.asksaveasfilename(title="Guardar fichero normalizado como...",
                                           defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt")])
    if not ficNorm:
        print("No se seleccionó ningún fichero de salida.")
        return

    normalizaHoras(ficText, ficNorm)
    print(f"Normalización completada. Archivo guardado como: {ficNorm}")

if __name__ == "__main__":
    main()

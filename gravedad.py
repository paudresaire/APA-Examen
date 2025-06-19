import tkinter as tk
import math

class Cuerpo:
    def __init__(self, x, y, vx, vy, masa, color, size, forma, cola):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.masa = masa
        self.color = color
        self.size = size
        self.forma = forma
        self.cola = cola
        self.trayectoria = []

    def actualizar(self, cuerpos, G, dt, limites):
        ax, ay = 0, 0
        for otro in cuerpos:
            if otro != self:
                dx = otro.x - self.x
                dy = otro.y - self.y
                dist2 = dx**2 + dy**2 + 1e-4
                f = G * otro.masa / dist2
                d = math.sqrt(dist2)
                ax += f * dx / d
                ay += f * dy / d
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if not (-limites < self.x < limites):
            self.x = max(min(self.x, limites), -limites)
            self.vx = -self.vx * 0.7
        if not (-limites < self.y < limites):
            self.y = max(min(self.y, limites), -limites)
            self.vy = -self.vy * 0.7

        self.trayectoria.append((self.x, self.y))
        if len(self.trayectoria) > self.cola:
            self.trayectoria.pop(0)

class Simulador:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Simulador de Cuerpos Sometidos a Atracción Gravitatoria")
        self.canvas = tk.Canvas(self.ventana, bg='#000040', width=900, height=600)
        self.canvas.pack(side=tk.LEFT)
        self.panel = tk.Frame(self.ventana, bg='black')
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.cuerpos = []
        self.G = tk.DoubleVar(value=1.0)
        self.dt = tk.DoubleVar(value=0.1)
        self.fps = tk.DoubleVar(value=30.0)
        self.corriendo = False
        self.escala = 20
        self.limites = 900 // (2 * self.escala)

        self.crear_panel_control()
        self.ventana.protocol("WM_DELETE_WINDOW", self.ventana.destroy)
        self.ventana.mainloop()

    def crear_panel_control(self):
        tk.Button(self.panel, text="Crear Cuerpo", command=self.abrir_config_cuerpo).pack(pady=5)
        tk.Button(self.panel, text="Crear Sistema Órbita", command=self.crear_sistema_orbital).pack(pady=5)
        tk.Button(self.panel, text="Inicia", bg='black', fg='lime', command=self.iniciar).pack(pady=5)
        tk.Button(self.panel, text="Reinicia", bg='black', fg='yellow', command=self.reiniciar).pack(pady=5)
        tk.Button(self.panel, text="Reset", bg='black', fg='orange', command=self.resetear).pack(pady=5)
        tk.Button(self.panel, text="Termina", bg='black', fg='red', command=self.ventana.destroy).pack(pady=5)

        tk.Label(self.panel, text="Constante Gravitatoria:", fg='white', bg='black').pack()
        tk.Scale(self.panel, variable=self.G, from_=0.01, to=5.0, resolution=0.01, orient=tk.HORIZONTAL).pack()
        tk.Label(self.panel, text="FPS (reproducción):", fg='white', bg='black').pack()
        tk.Scale(self.panel, variable=self.fps, from_=1, to=60, resolution=1, orient=tk.HORIZONTAL).pack()
        tk.Label(self.panel, text="Incremento Temporal:", fg='white', bg='black').pack()
        tk.Scale(self.panel, variable=self.dt, from_=0.01, to=2.0, resolution=0.01, orient=tk.HORIZONTAL).pack()

    def abrir_config_cuerpo(self):
        top = tk.Toplevel(self.ventana)
        top.title("Crear Cuerpo")
        top.configure(bg='black')

        entries = {}
        for campo in ["x", "y", "vx", "vy", "masa", "size", "cola"]:
            tk.Label(top, text=campo, fg='white', bg='black').pack()
            e = tk.Entry(top)
            e.insert(0, "0" if campo not in ["masa", "size", "cola"] else "1")
            e.pack()
            entries[campo] = e

        colores = ["yellow", "red", "green", "white", "cyan", "magenta"]
        formas = ["*", "o", "+", "x"]
        color_var = tk.StringVar(value=colores[0])
        forma_var = tk.StringVar(value=formas[0])
        tk.Label(top, text="Color", fg='white', bg='black').pack()
        tk.OptionMenu(top, color_var, *colores).pack()
        tk.Label(top, text="Forma", fg='white', bg='black').pack()
        tk.OptionMenu(top, forma_var, *formas).pack()

        vista_id = None
        def mostrar(event=None):
            nonlocal vista_id
            try:
                x = float(entries['x'].get())
                y = float(entries['y'].get())
                size = int(entries['size'].get())
                forma = forma_var.get()
                color = color_var.get()
                cx, cy = self.espacio_a_canvas(x, y)
                if forma == '*':
                    vista_id = self.canvas.create_text(cx, cy, text='*', fill=color, font=('Arial', size))
                else:
                    vista_id = self.canvas.create_oval(cx - size, cy - size, cx + size, cy + size, fill=color)
            except:
                pass

        def ocultar(event=None):
            nonlocal vista_id
            if vista_id:
                self.canvas.delete(vista_id)
                vista_id = None

        def crear():
            try:
                cuerpo = Cuerpo(
                    float(entries['x'].get()),
                    float(entries['y'].get()),
                    float(entries['vx'].get()),
                    float(entries['vy'].get()),
                    float(entries['masa'].get()),
                    color_var.get(),
                    int(entries['size'].get()),
                    forma_var.get(),
                    int(entries['cola'].get())
                )
                self.cuerpos.append(cuerpo)
                top.destroy()
            except:
                pass

        mostrar_btn = tk.Button(top, text="Mostrar", bg='gray')
        mostrar_btn.pack(pady=5)
        mostrar_btn.bind('<ButtonPress>', mostrar)
        mostrar_btn.bind('<ButtonRelease>', ocultar)
        tk.Button(top, text="Aceptar", command=crear, bg='green', fg='white').pack(pady=10)
        tk.Button(top, text="Salir", command=top.destroy, bg='red', fg='white').pack(pady=5)

    def crear_sistema_orbital(self):
        sol = Cuerpo(0, 0, 0, 0, 1000, 'yellow', 10, 'o', 300)
        planeta = Cuerpo(10, 0, 0, 7.1, 1, 'cyan', 5, 'o', 300)
        self.cuerpos.append(sol)
        self.cuerpos.append(planeta)
        self.dibujar()

    def iniciar(self):
        if not self.corriendo:
            self.corriendo = True
            self.simular()

    def simular(self):
        if not self.corriendo:
            return
        for cuerpo in self.cuerpos:
            cuerpo.actualizar(self.cuerpos, self.G.get(), self.dt.get(), self.limites)
        self.dibujar()
        delay = int(1000 / self.fps.get())
        self.ventana.after(delay, self.simular)

    def dibujar(self):
        self.canvas.delete("all")
        for cuerpo in self.cuerpos:
            x, y = self.espacio_a_canvas(cuerpo.x, cuerpo.y)
            if cuerpo.forma == '*':
                self.canvas.create_text(x, y, text='*', fill=cuerpo.color, font=('Arial', cuerpo.size))
            else:
                self.canvas.create_oval(x - cuerpo.size, y - cuerpo.size, x + cuerpo.size, y + cuerpo.size, fill=cuerpo.color)
            if len(cuerpo.trayectoria) > 1:
                coords = [self.espacio_a_canvas(px, py) for px, py in cuerpo.trayectoria]
                for i in range(len(coords) - 1):
                    self.canvas.create_line(*coords[i], *coords[i + 1], fill=cuerpo.color)

    def espacio_a_canvas(self, x, y):
        return x * self.escala + 450, -y * self.escala + 300

    def reiniciar(self):
        self.corriendo = False
        for cuerpo in self.cuerpos:
            cuerpo.trayectoria.clear()
        self.dibujar()

    def resetear(self):
        self.corriendo = False
        self.cuerpos.clear()
        self.dibujar()

if __name__ == '__main__':
    Simulador()

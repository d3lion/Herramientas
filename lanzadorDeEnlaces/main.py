import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import keyboard
import webbrowser
import json
import os
import subprocess
import sys
from datetime import datetime
import threading
import time

try:
    from plyer import notification
except ImportError:
    notification = None

class ShortcutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lanzador de Enlaces Pro")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        
        # Configurar icono (si existe)
        if os.path.exists("icons/app.ico"):
            self.root.iconbitmap("icons/app.ico")
        
        # Variables
        self.enlaces = {}
        self.perfil_actual = "default"
        self.escuchando = False
        self.tecla_presionada = False
        self.modo_reemplazo = tk.BooleanVar(value=True)
        self.modo_incognito = tk.BooleanVar(value=False)
        
        # Archivo de configuración
        self.config_file = "config.json"
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar datos
        self.cargar_enlaces()
        
        # Iniciar escucha de teclas
        self.iniciar_escucha()
        
        # Configurar cierre limpio
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica completa"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🚀 Lanzador de Enlaces por Teclas", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, pady=(0, 15))
        
        # --- Sección de Configuración de Perfil ---
        perfil_frame = ttk.LabelFrame(main_frame, text="Perfil", padding="5")
        perfil_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(perfil_frame, text="Perfil actual:").grid(row=0, column=0, padx=5)
        self.perfil_label = ttk.Label(perfil_frame, text="default", font=('Arial', 10, 'bold'))
        self.perfil_label.grid(row=0, column=1, padx=5)
        
        ttk.Button(perfil_frame, text="Nuevo Perfil", 
                  command=self.crear_perfil).grid(row=0, column=2, padx=5)
        ttk.Button(perfil_frame, text="Cargar Perfil", 
                  command=self.cargar_perfil).grid(row=0, column=3, padx=5)
        
        # --- Sección de Añadir Enlace ---
        add_frame = ttk.LabelFrame(main_frame, text="Añadir Nuevo Enlace", padding="10")
        add_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Tecla
        ttk.Label(add_frame, text="Tecla (ej: f1, a, 1):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.tecla_var = tk.StringVar()
        tecla_entry = ttk.Entry(add_frame, textvariable=self.tecla_var, width=15)
        tecla_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        # URL
        ttk.Label(add_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(add_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        # Botón Añadir
        ttk.Button(add_frame, text="➕ Añadir Enlace", 
                  command=self.agregar_enlace).grid(row=2, column=0, columnspan=2, pady=10)
        
        add_frame.columnconfigure(1, weight=1)
        
        # --- Opciones de Apertura ---
        options_frame = ttk.LabelFrame(main_frame, text="Opciones", padding="5")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Modo Reemplazo (reutilizar pestaña)", 
                       variable=self.modo_reemplazo).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="Modo Incógnito", 
                       variable=self.modo_incognito).pack(side=tk.LEFT, padx=10)
        
        # --- Lista de Enlaces ---
        list_frame = ttk.LabelFrame(main_frame, text="Enlaces Configurados", padding="5")
        list_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview con scrollbar
        tree_frame = ttk.Frame(list_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Tecla", "URL", "Usos"), 
                                show="headings", height=8)
        self.tree.heading("Tecla", text="Tecla", anchor=tk.W)
        self.tree.heading("URL", text="URL", anchor=tk.W)
        self.tree.heading("Usos", text="Usos", anchor=tk.CENTER)
        self.tree.column("Tecla", width=80)
        self.tree.column("URL", width=350)
        self.tree.column("Usos", width=60)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # --- Botones de Acción ---
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="🗑️ Eliminar Seleccionado", 
                  command=self.eliminar_enlace).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧹 Limpiar Todo", 
                  command=self.limpiar_todo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 Exportar", 
                  command=self.exportar_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📥 Importar", 
                  command=self.importar_config).pack(side=tk.LEFT, padx=5)
        
        # --- Estado y Ayuda ---
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(status_frame, text="✅ Aplicación activa - Presiona las teclas configuradas", 
                                     font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Label(status_frame, text="|  🛑 Presiona ESC para salir", 
                 font=('Arial', 9)).pack(side=tk.RIGHT)
        
        # Configurar grid para que se expanda
        main_frame.rowconfigure(4, weight=1)
        
        # Bind de eventos
        self.tree.bind('<Double-Button-1>', self.editar_enlace)
    
    def iniciar_escucha(self):
        """Inicia la escucha de teclas en un hilo separado"""
        def escuchar():
            self.escuchando = True
            while self.escuchando:
                try:
                    # Escuchar teclas especiales y normales
                    evento = keyboard.read_event(suppress=False)
                    if evento.event_type == keyboard.KEY_DOWN:
                        tecla = evento.name
                        # Si es ESC, salir
                        if tecla == 'esc':
                            self.root.after(0, self.on_closing)
                            break
                        # Si es una tecla configurada
                        if tecla in self.enlaces:
                            self.root.after(0, self.abrir_url, tecla)
                except Exception as e:
                    print(f"Error en escucha: {e}")
                    break
        
        hilo = threading.Thread(target=escuchar, daemon=True)
        hilo.start()
    
    def agregar_enlace(self):
        """Añade un nuevo enlace a la configuración"""
        tecla = self.tecla_var.get().strip().lower()
        url = self.url_var.get().strip()
        
        if not tecla or not url:
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos")
            return
        
        # Validar URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if tecla in self.enlaces:
            if not messagebox.askyesno("Sobrescribir", 
                                     f"La tecla '{tecla}' ya tiene un enlace asignado.\n¿Quieres sobrescribirlo?"):
                return
        
        self.enlaces[tecla] = {"url": url, "usos": 0}
        self.guardar_enlaces()
        self.actualizar_lista()
        
        # Limpiar campos
        self.tecla_var.set("")
        self.url_var.set("")
        
        self.mostrar_notificacion("Éxito", f"Enlace asignado a la tecla '{tecla}'")
        self.actualizar_estado(f"✅ Enlace '{tecla}' añadido correctamente")
    
    def abrir_url(self, tecla):
        """Abre la URL asociada a una tecla"""
        if tecla in self.enlaces:
            url = self.enlaces[tecla]["url"]
            
            # Incrementar contador de usos
            self.enlaces[tecla]["usos"] += 1
            self.guardar_enlaces()
            self.actualizar_lista()
            
            # Abrir en el navegador según modo
            try:
                if self.modo_incognito.get():
                    # Modo incógnito (Chrome)
                    try:
                        subprocess.Popen(['chrome', '--incognito', url])
                    except:
                        # Fallback a Firefox
                        subprocess.Popen(['firefox', '--private-window', url])
                else:
                    # Modo normal
                    if self.modo_reemplazo.get():
                        webbrowser.open(url, new=0)  # Reutilizar pestaña
                    else:
                        webbrowser.open_new_tab(url)  # Nueva pestaña
                
                self.mostrar_notificacion("Enlace Abierto", f"Abriendo: {url}")
                self.actualizar_estado(f"🌐 Abriendo '{url}' (tecla: {tecla})")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{str(e)}")
        else:
            self.mostrar_notificacion("Error", f"No hay enlace para la tecla '{tecla}'", error=True)
    
    def eliminar_enlace(self):
        """Elimina el enlace seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor, selecciona un enlace para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este enlace?"):
            tecla = self.tree.item(seleccion[0])['values'][0]
            del self.enlaces[tecla]
            self.guardar_enlaces()
            self.actualizar_lista()
            self.actualizar_estado(f"🗑️ Enlace '{tecla}' eliminado")
    
    def editar_enlace(self, event):
        """Permite editar un enlace con doble clic"""
        seleccion = self.tree.selection()
        if seleccion:
            tecla = self.tree.item(seleccion[0])['values'][0]
            url = self.tree.item(seleccion[0])['values'][1]
            self.tecla_var.set(tecla)
            self.url_var.set(url)
            self.actualizar_estado(f"✏️ Editando enlace '{tecla}'")
    
    def limpiar_todo(self):
        """Limpia todos los enlaces"""
        if not self.enlaces:
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar TODOS los enlaces?"):
            self.enlaces = {}
            self.guardar_enlaces()
            self.actualizar_lista()
            self.actualizar_estado("🧹 Todos los enlaces eliminados")
    
    def actualizar_lista(self):
        """Actualiza la lista de enlaces en la interfaz"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Añadir enlaces
        for tecla, datos in sorted(self.enlaces.items()):
            self.tree.insert("", tk.END, values=(tecla, datos["url"], datos.get("usos", 0)))
    
    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=mensaje)
        # Resetear después de 5 segundos
        self.root.after(5000, lambda: self.status_label.config(
            text="✅ Aplicación activa - Presiona las teclas configuradas"
        ))
    
    def guardar_enlaces(self):
        """Guarda los enlaces en el archivo JSON"""
        datos = {
            "perfil": self.perfil_actual,
            "enlaces": self.enlaces,
            "fecha_actualizacion": datetime.now().isoformat()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{str(e)}")
    
    def cargar_enlaces(self):
        """Carga los enlaces desde el archivo JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                self.enlaces = datos.get("enlaces", {})
                self.perfil_actual = datos.get("perfil", "default")
                self.perfil_label.config(text=self.perfil_actual)
                self.actualizar_lista()
                self.actualizar_estado(f"📂 Perfil '{self.perfil_actual}' cargado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la configuración:\n{str(e)}")
    
    def crear_perfil(self):
        """Crea un nuevo perfil"""
        nombre = tk.simpledialog.askstring("Nuevo Perfil", "Nombre del nuevo perfil:")
        if nombre:
            self.perfil_actual = nombre
            self.enlaces = {}
            self.perfil_label.config(text=nombre)
            self.guardar_enlaces()
            self.actualizar_lista()
            self.actualizar_estado(f"✨ Nuevo perfil '{nombre}' creado")
    
    def cargar_perfil(self):
        """Carga un perfil existente"""
        if not os.path.exists(self.config_file):
            messagebox.showwarning("Sin perfiles", "No hay perfiles guardados")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Mostrar diálogo para seleccionar perfil (simplificado)
            perfiles = [self.perfil_actual]
            # En una versión más completa, se podrían listar todos los perfiles
            # Por ahora solo mostramos el actual
            messagebox.showinfo("Perfil Actual", f"Perfil cargado: {self.perfil_actual}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el perfil:\n{str(e)}")
    
    def exportar_config(self):
        """Exporta la configuración a un archivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"shortcuts_{self.perfil_actual}_{datetime.now().strftime('%Y%m%d')}.json"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "perfil": self.perfil_actual,
                        "enlaces": self.enlaces,
                        "fecha_exportacion": datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Éxito", f"Configuración exportada a:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar:\n{str(e)}")
    
    def importar_config(self):
        """Importa una configuración desde un archivo"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                # Preguntar si sobrescribir o añadir
                if self.enlaces:
                    if not messagebox.askyesno("Sobrescribir", 
                                             "¿Quieres sobrescribir los enlaces actuales?\n"
                                             "(Selecciona 'No' para añadir los nuevos)"):
                        # Añadir sin sobrescribir
                        for tecla, datos_enlace in datos.get("enlaces", {}).items():
                            if tecla not in self.enlaces:
                                self.enlaces[tecla] = datos_enlace
                    else:
                        # Sobrescribir
                        self.enlaces = datos.get("enlaces", {})
                else:
                    self.enlaces = datos.get("enlaces", {})
                
                self.guardar_enlaces()
                self.actualizar_lista()
                self.actualizar_estado("📥 Configuración importada correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo importar:\n{str(e)}")
    
    def mostrar_notificacion(self, titulo, mensaje, error=False):
        """Muestra una notificación del sistema"""
        if notification:
            try:
                notification.notify(
                    title=titulo,
                    message=mensaje,
                    timeout=3
                )
            except:
                pass
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.escuchando = False
        self.guardar_enlaces()
        self.root.destroy()
        sys.exit(0)

def main():
    """Función principal"""
    root = tk.Tk()
    app = ShortcutApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pyperclip
import os
from datetime import datetime
import threading
import time

class ClipboardLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Logger Pro")
        self.root.geometry("800x650")
        
        # Variables de estado
        self.is_running = False
        self.data = []
        self.columns = []
        self.file_path = None
        self.file_format = tk.StringVar(value="csv")
        self.delimiter = tk.StringVar(value=",")
        self.encoding = tk.StringVar(value="utf-8")
        self.last_clipboard = ""
        self.paused = False
        self.column_count = tk.IntVar(value=3)
        
        # Variables para controlar el llenado por columnas
        self.current_row_index = -1
        self.current_column_index = 0
        self.current_row_data = {}
        self.waiting_for_first_copy = True  # Espera el primer Ctrl+C después de ejecutar
        
        self.setup_ui()
        self.start_monitoring()
        
    def setup_ui(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ===== SECCIÓN DE CONFIGURACIÓN =====
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Ruta del archivo
        ttk.Label(config_frame, text="Ruta de destino:").grid(row=0, column=0, sticky=tk.W)
        self.path_entry = ttk.Entry(config_frame, width=50)
        self.path_entry.grid(row=0, column=1, padx=5)
        ttk.Button(config_frame, text="Seleccionar", command=self.select_path).grid(row=0, column=2)
        
        # Formato y columnas
        ttk.Label(config_frame, text="Formato:").grid(row=1, column=0, sticky=tk.W, pady=5)
        format_combo = ttk.Combobox(config_frame, textvariable=self.file_format, 
                                   values=["csv", "json", "xml"], state="readonly", width=10)
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        ttk.Label(config_frame, text="Nº Columnas:").grid(row=1, column=2, sticky=tk.W, padx=10)
        ttk.Spinbox(config_frame, from_=1, to=20, textvariable=self.column_count, 
                   width=5, command=self.update_columns).grid(row=1, column=3, sticky=tk.W)
        
        # Nombres de columnas
        self.columns_frame = ttk.Frame(config_frame)
        self.columns_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        self.column_entries = []
        self.update_columns()
        
        # Opciones avanzadas
        ttk.Label(config_frame, text="Delimitador CSV:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(config_frame, textvariable=self.delimiter, width=5).grid(row=3, column=1, sticky=tk.W)
        ttk.Label(config_frame, text="Encoding:").grid(row=3, column=2, sticky=tk.W, padx=10)
        ttk.Combobox(config_frame, textvariable=self.encoding, 
                    values=["utf-8", "latin-1", "cp1252"], state="readonly", width=10).grid(row=3, column=3, sticky=tk.W)
        
        # ===== SECCIÓN DE CONTROL =====
        control_frame = ttk.LabelFrame(main_frame, text="Control", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.play_btn = ttk.Button(control_frame, text="▶ Play", command=self.toggle_play)
        self.play_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="⏸ Pausa", command=self.toggle_pause, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="↩ Deshacer último", command=self.undo_last).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="🗑 Limpiar datos", command=self.clear_data).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="📊 Nueva fila", command=self.start_new_row).grid(row=0, column=4, padx=5)
        
        # Contador
        self.counter_label = ttk.Label(control_frame, text="Registros: 0")
        self.counter_label.grid(row=0, column=5, padx=20)
        
        # Estado de la fila actual
        self.row_status_label = ttk.Label(control_frame, text="Estado: Esperando")
        self.row_status_label.grid(row=0, column=6, padx=10)
        
        # ===== SECCIÓN DE VISTA PREVIA =====
        preview_frame = ttk.LabelFrame(main_frame, text="Vista previa del portapapeles", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=4, width=80, state="disabled")
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scroll_preview = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        scroll_preview.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_text['yscrollcommand'] = scroll_preview.set
        
        # ===== SECCIÓN DE DATOS CAPTURADOS =====
        data_frame = ttk.LabelFrame(main_frame, text="Datos capturados", padding="10")
        data_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # TreeView para mostrar datos
        columns = ("#", "Fecha", "Datos")
        self.tree = ttk.Treeview(data_frame, columns=columns, show="headings", height=10)
        self.tree.heading("#", text="ID")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Datos", text="Datos")
        
        self.tree.column("#", width=40)
        self.tree.column("Fecha", width=150)
        self.tree.column("Datos", width=450)
        
        scroll_tree = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_tree.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar peso de los frames
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=2)
        
        # Variables para monitoreo
        self.monitor_thread = None
        self.stop_monitor = False
        
    def update_columns(self):
        # Limpiar entries existentes
        for entry in self.column_entries:
            entry.destroy()
        self.column_entries.clear()
        
        # Crear nuevos entries para nombres de columnas
        ttk.Label(self.columns_frame, text="Nombres de columnas:").grid(row=0, column=0, padx=5)
        
        for i in range(self.column_count.get()):
            entry = ttk.Entry(self.columns_frame, width=15)
            entry.grid(row=0, column=i+1, padx=2)
            entry.insert(0, f"Columna_{i+1}")
            self.column_entries.append(entry)
    
    def on_format_change(self, event=None):
        pass
    
    def select_path(self):
        file_types = []
        format_type = self.file_format.get()
        if format_type == "csv":
            file_types = [("CSV files", "*.csv"), ("All files", "*.*")]
        elif format_type == "json":
            file_types = [("JSON files", "*.json"), ("All files", "*.*")]
        elif format_type == "xml":
            file_types = [("XML files", "*.xml"), ("All files", "*.*")]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=file_types
        )
        if file_path:
            self.file_path = file_path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
            
            # Si hay datos guardados, guardar en la nueva ruta
            if self.data:
                self.save_data()
    
    def start_new_row(self):
        """Inicia una nueva fila manualmente"""
        if not self.is_running:
            return
        
        self.current_row_index = len(self.data)
        self.current_row_data = {}
        self.current_column_index = 0
        self.waiting_for_first_copy = True  # Esperar el primer Ctrl+C
        
        # Actualizar estado
        next_col = self.columns[self.current_column_index] if self.columns else "Columna_1"
        self.row_status_label.config(text=f"📝 Copia para: {next_col}")
    
    def toggle_play(self):
        if not self.file_path:
            messagebox.showerror("Error", "Por favor selecciona una ruta de destino")
            return
        
        # Verificar que los nombres de columnas no estén vacíos
        column_names = [entry.get().strip() for entry in self.column_entries]
        if any(not name for name in column_names):
            messagebox.showerror("Error", "Todos los nombres de columnas deben tener un valor")
            return
        
        self.columns = column_names
        
        if not self.is_running:
            self.is_running = True
            self.paused = False
            self.waiting_for_first_copy = True  # Esperar el primer Ctrl+C
            self.play_btn.config(text="⏹ Stop")
            self.pause_btn.config(state="normal", text="⏸ Pausa")
            self.counter_label.config(text=f"Registros: {len(self.data)}")
            
            # Iniciar una nueva fila
            self.current_row_index = len(self.data)
            self.current_row_data = {}
            self.current_column_index = 0
            next_col = self.columns[0] if self.columns else "Columna_1"
            self.row_status_label.config(text=f"📝 Copia para: {next_col}")
            
        else:
            self.is_running = False
            self.paused = False
            self.play_btn.config(text="▶ Play")
            self.pause_btn.config(state="disabled", text="⏸ Pausa")
            self.row_status_label.config(text="⏹ Detenido")
            
            # Si hay datos en la fila actual incompleta, guardarlos si tiene al menos una columna
            if self.current_row_data and len(self.current_row_data) > 0:
                # Rellenar columnas faltantes con vacío
                for col in self.columns:
                    if col not in self.current_row_data:
                        self.current_row_data[col] = ""
                self.data.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data': self.current_row_data.copy()
                })
                self.current_row_data = {}
                self.current_row_index = -1
                self.update_treeview()
                self.counter_label.config(text=f"Registros: {len(self.data)}")
            
            # Guardar datos al detener
            if self.data:
                self.save_data()
    
    def toggle_pause(self):
        if not self.is_running:
            return
        
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ Reanudar")
            self.play_btn.config(state="disabled")
            self.row_status_label.config(text="⏸ En pausa")
        else:
            self.pause_btn.config(text="⏸ Pausa")
            self.play_btn.config(state="normal")
            if self.current_row_index >= 0:
                next_col = self.columns[self.current_column_index] if self.current_column_index < len(self.columns) else "Completado"
                self.row_status_label.config(text=f"📝 Copia para: {next_col}")
            else:
                self.row_status_label.config(text="🔄 Esperando nueva fila")
    
    def undo_last(self):
        if not self.data:
            return
        
        removed = self.data.pop()
        self.update_treeview()
        self.counter_label.config(text=f"Registros: {len(self.data)}")
        # Guardar después de deshacer
        if self.data:
            self.save_data()
        else:
            # Si no hay datos, eliminar el archivo o dejarlo vacío
            if self.file_path and os.path.exists(self.file_path):
                try:
                    os.remove(self.file_path)
                except:
                    pass
    
    def clear_data(self):
        if not self.data:
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar todos los datos?"):
            self.data.clear()
            self.current_row_data = {}
            self.current_row_index = -1
            self.update_treeview()
            self.counter_label.config(text="Registros: 0")
            self.row_status_label.config(text="🗑 Datos limpiados")
            # Eliminar archivo si existe
            if self.file_path and os.path.exists(self.file_path):
                try:
                    os.remove(self.file_path)
                except:
                    pass
    
    def start_monitoring(self):
        # Iniciar hilo de monitoreo
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()
    
    def monitor_clipboard(self):
        while not self.stop_monitor:
            if self.is_running and not self.paused:
                try:
                    current = pyperclip.paste()
                    if current and current != self.last_clipboard:
                        self.last_clipboard = current
                        # Solo procesar si no estamos esperando el primer copiado
                        if not self.waiting_for_first_copy:
                            self.root.after(0, self.process_clipboard, current)
                        else:
                            # Primer copiado después de ejecutar - solo actualizar vista previa
                            self.waiting_for_first_copy = False
                            self.root.after(0, self.update_preview, current)
                except Exception as e:
                    print(f"Error al leer portapapeles: {e}")
            time.sleep(0.3)
    
    def update_preview(self, content):
        """Actualiza la vista previa sin procesar el dato"""
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, content)
        self.preview_text.config(state="disabled")
        
        # Mostrar que se ha capturado pero no se ha guardado (primer copiado)
        self.row_status_label.config(text=f"📋 Capturado: {content[:30]}... (no guardado)")
    
    def process_clipboard(self, content):
        """Procesa el contenido del portapapeles para rellenar una columna"""
        # Actualizar vista previa
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, content)
        self.preview_text.config(state="disabled")
        
        # Si no hay una fila en proceso, iniciar una nueva
        if self.current_row_index == -1 or self.current_column_index >= len(self.columns):
            self.current_row_index = len(self.data)
            self.current_row_data = {}
            self.current_column_index = 0
        
        # Rellenar la columna actual
        col_name = self.columns[self.current_column_index]
        self.current_row_data[col_name] = content
        
        # Mostrar qué columna se llenó
        self.row_status_label.config(text=f"✅ {col_name}: {content[:30]}...")
        
        # Avanzar al siguiente columna
        self.current_column_index += 1
        
        # Verificar si se completó la fila
        if self.current_column_index >= len(self.columns):
            # Fila completada, guardar
            self.data.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data': self.current_row_data.copy()
            })
            
            # Actualizar vista
            self.update_treeview()
            self.counter_label.config(text=f"Registros: {len(self.data)}")
            
            # GUARDAR INMEDIATAMENTE DESPUÉS DE CADA FILA
            self.save_data()
            
            # Preparar para nueva fila
            self.current_row_data = {}
            self.current_row_index = -1
            self.current_column_index = 0
            
            self.row_status_label.config(text="🎉 Fila completada! Iniciando nueva...")
            
            # Iniciar nueva fila automáticamente
            self.root.after(100, self.start_new_row)
    
    def update_treeview(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Mostrar últimos 100 registros
        start = max(0, len(self.data) - 100)
        for i, record in enumerate(self.data[start:], start=start+1):
            # Mostrar datos resumidos
            data_str = ', '.join([f"{k}:{v}" for k, v in record['data'].items()])
            self.tree.insert("", "end", values=(i, record['timestamp'], data_str[:100] + "..." if len(data_str) > 100 else data_str))
    
    def save_data(self):
        """Guarda los datos en el archivo seleccionado"""
        if not self.file_path or not self.data:
            return
        
        try:
            # Asegurar que la ruta del directorio existe
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            if self.file_format.get() == "csv":
                self.save_csv()
            elif self.file_format.get() == "json":
                self.save_json()
            elif self.file_format.get() == "xml":
                self.save_xml()
            
            # Actualizar estado
            self.root.title(f"Clipboard Logger Pro - Guardado: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo: {str(e)}")
    
    def save_csv(self):
        with open(self.file_path, 'w', encoding=self.encoding.get(), newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp'] + self.columns, 
                                   delimiter=self.delimiter.get())
            writer.writeheader()
            for record in self.data:
                row = {'timestamp': record['timestamp']}
                row.update(record['data'])
                writer.writerow(row)
    
    def save_json(self):
        with open(self.file_path, 'w', encoding=self.encoding.get()) as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def save_xml(self):
        root = ET.Element("data")
        for record in self.data:
            item = ET.SubElement(root, "record")
            ET.SubElement(item, "timestamp").text = record['timestamp']
            data_elem = ET.SubElement(item, "data")
            for key, value in record['data'].items():
                field = ET.SubElement(data_elem, key)
                field.text = str(value) if value else ""
        
        # Formatear XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        with open(self.file_path, 'w', encoding=self.encoding.get()) as f:
            f.write(pretty_xml)
    
    def __del__(self):
        self.stop_monitor = True
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardLoggerApp(root)
    root.mainloop()
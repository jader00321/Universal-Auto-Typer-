# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Universal Auto-Typer v4.3
# Creado para automatizar clics y escritura en cualquier aplicación.
# ADVERTENCIA: El uso de este software para violar los términos de servicio
# de cualquier plataforma es responsabilidad exclusiva del usuario.
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import random
import threading
import json
import os
import sys
from datetime import datetime
from ttkthemes import ThemedTk

# --- NUEVO: Función para encontrar recursos (como el icono) en el .exe ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Clase para Tooltips (Mensajes de Ayuda emergentes) ---
class ToolTip:
    """
    Crea una pequeña ventana de ayuda que aparece cuando el mouse
    se posa sobre un widget (botón, campo de texto, etc.).
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#333333", foreground="white", relief='solid', borderwidth=1,
                         font=("Helvetica", "9", "normal"))
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

# --- Clase Principal de la Aplicación ---
class AutoTyperApp:
    """
    Clase que construye y gestiona toda la interfaz gráfica y la lógica del bot.
    """
    def __init__(self, root):
        # --- Configuración Inicial de la Ventana ---
        self.root = root
        self.root.title("Universal Auto-Typer v4.3")
        self.root.geometry("500x750")
        self.root.resizable(False, False)
        # MODIFICACIÓN: Se establece el icono de la ventana.
        try:
            self.root.iconbitmap(resource_path("bot-icono.ico"))
        except tk.TclError:
            print("Icono no encontrado. Asegúrate de que 'bot-icono.ico' está en la misma carpeta.")
        
        # --- Variables de Estado del Bot ---
        self.coords_target = None
        self.coords_send = None
        self.bot_thread = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.countdown_job = None
        self.time_settings = {'min': 5, 'max': 15}

        # --- Aplicación de Estilo y Tema Oscuro ---
        self.style = ttk.Style()
        self.style.theme_use('equilux') 
        self.root.configure(bg=self.style.lookup('TFrame', 'background'))
        self.style.configure("TButton", padding=8, font=('Helvetica', 10, 'bold'))
        self.style.configure("Success.TButton", background="#2a9d8f")
        self.style.configure("Warning.TButton", background="#f4a261")
        self.style.configure("Danger.TButton", background="#e76f51")

        # --- Construcción de la Interfaz ---
        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        """Crea la barra de menú superior (Archivo)."""
        self.menubar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Guardar Perfil", command=self.save_profile)
        self.file_menu.add_command(label="Cargar Perfil", command=self.load_profile)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.menubar.add_cascade(label="Archivo", menu=self.file_menu)
        self.root.config(menu=self.menubar)

    def create_widgets(self):
        """Crea y organiza todos los elementos visuales usando pestañas."""
        notebook = ttk.Notebook(self.root, padding=10)
        
        main_tab = ttk.Frame(notebook, padding="10")
        history_tab = ttk.Frame(notebook, padding="10")
        help_tab = ttk.Frame(notebook, padding="10")

        notebook.add(main_tab, text='Configuración del Bot')
        notebook.add(history_tab, text='Historial de Envíos')
        notebook.add(help_tab, text='Ayuda y Advertencia')
        
        self.create_main_tab_content(main_tab)
        self.create_history_tab_content(history_tab)
        self.create_help_tab_content(help_tab)
        
        notebook.pack(expand=True, fill='both')

    def create_main_tab_content(self, parent_frame):
        """Crea el contenido de la pestaña principal de configuración."""
        parent_frame.columnconfigure(2, weight=1)
        # --- 1. Configuración de Coordenadas ---
        coords_frame = ttk.LabelFrame(parent_frame, text="1. Configuración de Clics", padding="15")
        coords_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        coords_frame.columnconfigure(1, weight=1)
        
        btn_target = ttk.Button(coords_frame, text="Capturar Objetivo (Escribir)", command=lambda: self.get_coords('target'))
        btn_target.grid(row=0, column=0, padx=5, sticky="ew")
        self.lbl_target_coords = ttk.Label(coords_frame, text="X: ?, Y: ?", width=15)
        self.lbl_target_coords.grid(row=0, column=1, sticky="w", padx=10)
        
        btn_send = ttk.Button(coords_frame, text="Capturar Acción (Enviar)", command=lambda: self.get_coords('send'))
        btn_send.grid(row=1, column=0, padx=5, pady=(5,0), sticky="ew")
        self.lbl_send_coords = ttk.Label(coords_frame, text="X: ?, Y: ?", width=15)
        self.lbl_send_coords.grid(row=1, column=1, sticky="w", padx=10, pady=(5,0))
        
        ToolTip(btn_target, "Minimiza la app y te da 5 segundos\npara poner el mouse sobre el cuadro de texto.")
        ToolTip(btn_send, "Minimiza la app y te da 5 segundos\npara poner el mouse sobre el botón de 'Enviar'.")

        # --- 2. Lista de Mensajes ---
        msg_frame = ttk.LabelFrame(parent_frame, text="2. Lista de Mensajes", padding="15")
        msg_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=15)
        parent_frame.rowconfigure(1, weight=1)
        msg_frame.columnconfigure(0, weight=1)

        self.msg_listbox = tk.Listbox(msg_frame, height=10, font=('Helvetica', 10), relief=tk.FLAT)
        self.msg_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(msg_frame, orient=tk.VERTICAL, command=self.msg_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.msg_listbox.config(yscrollcommand=scrollbar.set)

        msg_actions_frame = ttk.Frame(parent_frame)
        msg_actions_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        msg_actions_frame.columnconfigure(0, weight=1)
        
        self.entry_new_msg = ttk.Entry(msg_actions_frame, font=('Helvetica', 10))
        self.entry_new_msg.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_new_msg.bind("<Return>", lambda event: self.add_message())

        btn_add = ttk.Button(msg_actions_frame, text="Añadir", command=self.add_message)
        btn_add.grid(row=0, column=1, padx=(0, 5))
        btn_del = ttk.Button(msg_actions_frame, text="Borrar", command=self.delete_message)
        btn_del.grid(row=0, column=2)
        
        ToolTip(self.entry_new_msg, "Escribe un mensaje y presiona 'Añadir' o Enter.")
        ToolTip(btn_del, "Elimina el mensaje seleccionado de la lista.")

        # --- 3. Intervalo de Tiempo ---
        time_frame = ttk.LabelFrame(parent_frame, text="3. Intervalo de Tiempo (segundos)", padding="15")
        time_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=15)
        time_frame.columnconfigure(0, weight=1)
        time_frame.columnconfigure(2, weight=1)

        ttk.Label(time_frame, text="Mínimo:").grid(row=0, column=0, sticky="e")
        self.spin_min_time = ttk.Spinbox(time_frame, from_=1, to=3600, width=5, justify="center")
        self.spin_min_time.set(self.time_settings['min'])
        self.spin_min_time.grid(row=0, column=1, padx=10)
        
        ttk.Label(time_frame, text="Máximo:").grid(row=0, column=2, sticky="e")
        self.spin_max_time = ttk.Spinbox(time_frame, from_=1, to=3600, width=5, justify="center")
        self.spin_max_time.set(self.time_settings['max'])
        self.spin_max_time.grid(row=0, column=3, padx=10)

        # --- 4. Controles Principales ---
        controls_container = ttk.Frame(parent_frame)
        controls_container.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        controls_container.columnconfigure((0,1,2), weight=1)

        self.btn_start = ttk.Button(controls_container, text="INICIAR BOT", style="Success.TButton", command=self.start_bot)
        self.btn_start.grid(row=0, column=0, sticky="ew")
        
        self.btn_pause = ttk.Button(controls_container, text="PAUSAR", style="Warning.TButton", command=self.pause_bot, state=tk.DISABLED)
        self.btn_pause.grid(row=0, column=1, sticky="ew", padx=10)
        
        self.btn_stop = ttk.Button(controls_container, text="DETENER", style="Danger.TButton", command=self.stop_bot, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=2, sticky="ew")

        # --- Barra de Estado ---
        self.status_var = tk.StringVar(value="Estado: Listo para iniciar.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_history_tab_content(self, parent_frame):
        """Crea el contenido de la pestaña de historial."""
        parent_frame.rowconfigure(0, weight=1)
        parent_frame.columnconfigure(0, weight=1)
        
        cols = ('timestamp', 'message')
        self.history_tree = ttk.Treeview(parent_frame, columns=cols, show='headings')
        
        self.history_tree.heading('timestamp', text='Hora de Envío')
        self.history_tree.heading('message', text='Mensaje Enviado')
        
        self.history_tree.column('timestamp', width=150, anchor=tk.CENTER)
        self.history_tree.column('message', width=300)
        
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def create_help_tab_content(self, parent_frame):
        """Crea el contenido de la pestaña de ayuda con scroll y layout robusto."""
        parent_frame.rowconfigure(0, weight=1)
        parent_frame.columnconfigure(0, weight=1)

        help_text_widget = tk.Text(parent_frame, wrap="word", relief=tk.FLAT, font=("Helvetica", 10))
        help_text_widget.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=help_text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        help_text_widget.config(yscrollcommand=scrollbar.set)

        help_text_widget.tag_configure("title", font=("Helvetica", 16, "bold"), spacing3=20)
        help_text_widget.tag_configure("heading", font=("Helvetica", 12, "bold"), spacing3=10)
        help_text_widget.tag_configure("normal", font=("Helvetica", 10), lmargin1=10, lmargin2=25)
        help_text_widget.tag_configure("warning", font=("Helvetica", 10), lmargin1=10, lmargin2=10)

        help_text_widget.insert(tk.END, "Guía de Uso y Descargo de Responsabilidad\n", "title")
        
        help_text_widget.insert(tk.END, "¿Cómo usar la aplicación?\n", "heading")
        how_to_text = (
            "1.  Capturar Coordenadas:\n"
            "    - Clic en 'Capturar Objetivo': Tienes 5 segundos para mover el mouse al lugar donde quieres escribir.\n"
            "    - Clic en 'Capturar Acción': Tienes 5 segundos para mover el mouse al botón de 'Enviar' o similar.\n\n"
            "2.  Añadir Mensajes:\n"
            "    - Escribe tus mensajes en el campo de texto y presiona 'Añadir' o la tecla Enter.\n\n"
            "3.  Configurar Tiempo:\n"
            "    - Define el intervalo de tiempo (mínimo y máximo) en segundos entre cada mensaje.\n\n"
            "4.  Iniciar el Bot:\n"
            "    - Presiona 'INICIAR BOT'. Puedes pausar, reanudar y detener el proceso con los controles.\n\n"
            "5.  Guardar/Cargar Perfiles:\n"
            "    - Usa el menú 'Archivo' para guardar tu configuración (coordenadas y mensajes) y cargarla más tarde.\n"
        )
        help_text_widget.insert(tk.END, how_to_text, "normal")

        help_text_widget.insert(tk.END, "\n⚠️ Advertencia y Descargo de Responsabilidad\n", "heading")
        disclaimer_text = (
            "Esta aplicación es una herramienta de automatización de propósito general. El uso de este software para interactuar con plataformas de terceros (como sitios web, redes sociales o juegos) puede violar sus Términos de Servicio.\n\n"
            "El uso de bots puede resultar en sanciones, incluyendo la suspensión temporal o permanente de su cuenta. Los desarrolladores de Universal Auto-Typer no se hacen responsables de ninguna consecuencia derivada del uso de este software. Utilícelo bajo su propio riesgo y discreción."
        )
        help_text_widget.insert(tk.END, disclaimer_text, "warning")
        
        help_text_widget.config(state=tk.DISABLED)

    def get_coords(self, target):
        """Muestra una ventana de cuenta regresiva y captura las coordenadas del mouse."""
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.geometry(f"400x100+{self.root.winfo_screenwidth()//2-200}+{self.root.winfo_screenheight()//2-50}")
        overlay.attributes('-alpha', 0.85)
        overlay.configure(bg='black')
        
        countdown_label = tk.Label(overlay, text="", font=("Helvetica", 24, "bold"), fg="white", bg="black")
        countdown_label.pack(expand=True)

        self.root.iconify()

        def countdown(count):
            if count > 0:
                countdown_label.config(text=f"Capturando en... {count}")
                overlay.after(1000, countdown, count - 1)
            else:
                overlay.destroy()
                pos = pyautogui.position()
                self.root.deiconify()
                
                if target == 'target':
                    self.coords_target = pos
                    self.lbl_target_coords.config(text=f"X: {pos.x}, Y: {pos.y}")
                elif target == 'send':
                    self.coords_send = pos
                    self.lbl_send_coords.config(text=f"X: {pos.x}, Y: {pos.y}")
                self.status_var.set(f"Coordenadas de '{target}' capturadas.")
        
        countdown(5)

    def add_message(self):
        """Añade un mensaje del campo de entrada a la lista."""
        msg = self.entry_new_msg.get()
        if msg:
            self.msg_listbox.insert(tk.END, msg)
            self.entry_new_msg.delete(0, tk.END)

    def delete_message(self):
        """Borra el mensaje seleccionado de la lista."""
        selected_indices = self.msg_listbox.curselection()
        if selected_indices:
            self.msg_listbox.delete(selected_indices[0])

    def update_ui_state(self, is_running):
        """Habilita o deshabilita los controles según el estado del bot."""
        config_state = tk.DISABLED if is_running else tk.NORMAL
        running_state = tk.NORMAL if is_running else tk.DISABLED
        
        self.btn_start.config(state=config_state)
        self.menubar.entryconfig("Archivo", state=config_state)
        
        self.btn_pause.config(state=running_state)
        self.btn_stop.config(state=running_state)
    
    def update_time_settings(self):
        """Lee los valores de tiempo de los spinbox y los guarda."""
        try:
            min_val = int(self.spin_min_time.get())
            max_val = int(self.spin_max_time.get())
            if min_val <= 0 or max_val < min_val:
                raise ValueError
            self.time_settings['min'] = min_val
            self.time_settings['max'] = max_val
            return True
        except (ValueError, tk.TclError):
            messagebox.showerror("Error de Configuración", "Los valores de tiempo no son válidos.")
            return False

    def start_bot(self):
        """Valida la configuración e inicia el hilo del bot."""
        if not self.coords_target or not self.coords_send:
            messagebox.showerror("Error de Configuración", "Debes capturar ambas coordenadas antes de iniciar.")
            return
        
        messages = list(self.msg_listbox.get(0, tk.END))
        if not messages:
            messagebox.showerror("Error de Configuración", "La lista de mensajes está vacía.")
            return

        if not self.update_time_settings():
            return

        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        self.stop_event.clear()
        self.pause_event.clear()
        self.bot_thread = threading.Thread(target=self.bot_loop, args=(messages,), daemon=True)
        self.bot_thread.start()
        self.update_ui_state(is_running=True)
        self.status_var.set("Estado: Bot iniciando...")
        self.btn_pause.config(text="PAUSAR")

    def pause_bot(self):
        """Pausa o reanuda el funcionamiento del bot."""
        if self.pause_event.is_set():
            if not self.update_time_settings():
                return
            self.pause_event.clear()
            self.status_var.set("Estado: Bot reanudado.")
            self.btn_pause.config(text="PAUSAR")
        else:
            self.pause_event.set()
            if self.countdown_job:
                self.root.after_cancel(self.countdown_job)
            self.status_var.set("Estado: Bot pausado.")
            self.btn_pause.config(text="REANUDAR")
    
    def stop_bot(self):
        """Detiene de forma segura el hilo del bot y limpia el historial."""
        if self.bot_thread:
            self.stop_event.set()
            if self.countdown_job:
                self.root.after_cancel(self.countdown_job)
                self.countdown_job = None
            self.update_ui_state(is_running=False)
            self.status_var.set("Estado: Bot detenido. Historial reiniciado.")
            self.bot_thread = None
            for i in self.history_tree.get_children():
                self.history_tree.delete(i)

    def update_countdown(self, remaining_time):
        """Actualiza el contador en la barra de estado cada segundo."""
        if remaining_time > 0 and not self.pause_event.is_set() and not self.stop_event.is_set():
            self.status_var.set(f"Próximo mensaje en {remaining_time} segundos...")
            self.countdown_job = self.root.after(1000, self.update_countdown, remaining_time - 1)

    def add_to_history(self, message):
        """Añade una entrada al historial de forma segura."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history_tree.insert("", tk.END, values=(timestamp, message))
        self.history_tree.yview_moveto(1)

    def bot_loop(self, messages):
        """El bucle principal que se ejecuta en un hilo separado para enviar mensajes."""
        while not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.5)
                continue

            mensaje_a_enviar = random.choice(messages)
            
            try:
                pyautogui.click(self.coords_target[0], self.coords_target[1])
                time.sleep(0.2)
                pyautogui.typewrite(mensaje_a_enviar, interval=0.05)
                time.sleep(0.2)
                pyautogui.click(self.coords_send[0], self.coords_send[1])
                
                self.root.after(0, self.add_to_history, mensaje_a_enviar)
                
                min_t = self.time_settings['min']
                max_t = self.time_settings['max']
                tiempo_espera = random.randint(min_t, max_t)

                self.root.after(0, self.update_countdown, tiempo_espera)
                self.stop_event.wait(tiempo_espera)

            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {e}. Bot detenido."))
                break
        
        self.root.after(0, self.stop_bot)
    
    def save_profile(self):
        """Guarda la configuración actual en un archivo JSON."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Bot Profiles", "*.json"), ("All Files", "*.*")],
            title="Guardar Perfil"
        )
        if not filepath: return
        
        profile_data = {
            "coords_target": self.coords_target,
            "coords_send": self.coords_send,
            "messages": list(self.msg_listbox.get(0, tk.END)),
            "min_time": self.spin_min_time.get(),
            "max_time": self.spin_max_time.get()
        }
        
        with open(filepath, 'w') as f:
            json.dump(profile_data, f, indent=4)
        self.status_var.set(f"Perfil guardado.")

    def load_profile(self):
        """Carga una configuración desde un archivo JSON."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Bot Profiles", "*.json"), ("All Files", "*.*")],
            title="Cargar Perfil"
        )
        if not filepath: return
        
        try:
            with open(filepath, 'r') as f:
                profile_data = json.load(f)
                
            self.coords_target = tuple(profile_data.get("coords_target")) if profile_data.get("coords_target") else None
            self.coords_send = tuple(profile_data.get("coords_send")) if profile_data.get("coords_send") else None
            
            self.lbl_target_coords.config(text=f"X: {self.coords_target[0]}, Y: {self.coords_target[1]}" if self.coords_target else "X: ?, Y: ?")
            self.lbl_send_coords.config(text=f"X: {self.coords_send[0]}, Y: {self.coords_send[1]}" if self.coords_send else "X: ?, Y: ?")
            
            self.msg_listbox.delete(0, tk.END)
            for msg in profile_data.get("messages", []):
                self.msg_listbox.insert(tk.END, msg)
            
            self.spin_min_time.set(profile_data.get("min_time", "5"))
            self.spin_max_time.set(profile_data.get("max_time", "15"))
            
            self.status_var.set(f"Perfil cargado.")
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar el perfil.\nError: {e}")

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = AutoTyperApp(root)
    root.mainloop()


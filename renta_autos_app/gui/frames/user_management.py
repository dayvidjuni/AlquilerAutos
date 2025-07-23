# Archivo: renta_autos_app/gui/frames/user_management.py
import customtkinter as ctk
from database_manager import DatabaseManager
from auth_manager import AuthManager
from gui.add_user_window import AddUserWindow # Lo crearemos en el siguiente paso

class UserManagementFrame(ctk.CTkFrame):
    """
    Frame para mostrar y gestionar los usuarios del sistema (clientes, empleados, admins).
    """
    def __init__(self, master, db_manager: DatabaseManager, auth_manager: AuthManager):
        super().__init__(master, fg_color="transparent")
        self.db_manager = db_manager
        self.auth_manager = auth_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Frame Superior ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(top_frame, text="Gestión de Usuarios", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(top_frame, text="Registrar Usuario", command=self.open_add_user_window).grid(row=0, column=1, padx=(10, 5))
        ctk.CTkButton(top_frame, text="Actualizar", command=self.load_users, width=100).grid(row=0, column=2, padx=(0, 5))

        # --- Frame Desplazable para la Lista ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Listado de Usuarios")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.load_users()

    def open_add_user_window(self):
        if hasattr(self, 'add_window') and self.add_window.winfo_exists():
            self.add_window.focus()
            return
        
        self.add_window = AddUserWindow(
            master=self.winfo_toplevel(),
            db_manager=self.db_manager,
            auth_manager=self.auth_manager,
            on_close_callback=self.load_users
        )
    
    def load_users(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = """
            SELECT u.nombre, u.apellido, u.username, u.email, u.telefono, u.activo, r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id_rol
            ORDER BY u.id_rol, u.apellido;
        """
        users = self.db_manager.execute_query(query)

        if not users:
            ctk.CTkLabel(self.scrollable_frame, text="No hay usuarios para mostrar.").pack(pady=20)
            return

        for user in users:
            card = ctk.CTkFrame(self.scrollable_frame, border_width=1)
            card.pack(fill="x", padx=10, pady=5, expand=True)
            card.grid_columnconfigure(1, weight=1)

            full_name = f"{user['nombre']} {user['apellido']}"
            ctk.CTkLabel(card, text=full_name, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
            ctk.CTkLabel(card, text=f"Usuario: {user['username']}", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=10, pady=2, sticky="w")
            
            ctk.CTkLabel(card, text=f"Email: {user['email']}", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(card, text=f"Teléfono: {user.get('telefono', 'N/A')}", font=ctk.CTkFont(size=12)).grid(row=3, column=0, padx=10, pady=(2, 10), sticky="w")

            role_label = ctk.CTkLabel(card, text=user['rol'].upper(), font=ctk.CTkFont(size=14, weight="bold"))
            role_label.grid(row=1, column=1, rowspan=2, padx=10)

            status_text = "ACTIVO" if user['activo'] else "INACTIVO"
            status_color = "green" if user['activo'] else "red"
            ctk.CTkLabel(card, text=status_text, font=ctk.CTkFont(size=12), text_color=status_color).grid(row=0, column=2, padx=10, sticky="e")
# Archivo: renta_autos_app/gui/add_user_window.py
import customtkinter as ctk
from database_manager import DatabaseManager
from auth_manager import AuthManager

class AddUserWindow(ctk.CTkToplevel):
    def __init__(self, master, db_manager: DatabaseManager, auth_manager: AuthManager, on_close_callback):
        super().__init__(master)
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.on_close_callback = on_close_callback

        self.title("Registrar Nuevo Usuario")
        self.geometry("450x650")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text="Datos del Nuevo Usuario", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 20))

        # --- Campos del formulario ---
        self.username_entry = ctk.CTkEntry(main_frame, placeholder_text="Nombre de usuario (para login)", height=35)
        self.username_entry.pack(pady=8, fill="x")
        
        self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="Contraseña", show="*", height=35)
        self.password_entry.pack(pady=8, fill="x")

        self.name_entry = ctk.CTkEntry(main_frame, placeholder_text="Nombre(s)", height=35)
        self.name_entry.pack(pady=8, fill="x")

        self.lastname_entry = ctk.CTkEntry(main_frame, placeholder_text="Apellido(s)", height=35)
        self.lastname_entry.pack(pady=8, fill="x")

        self.email_entry = ctk.CTkEntry(main_frame, placeholder_text="Correo electrónico", height=35)
        self.email_entry.pack(pady=8, fill="x")

        self.phone_entry = ctk.CTkEntry(main_frame, placeholder_text="Teléfono (opcional)", height=35)
        self.phone_entry.pack(pady=8, fill="x")

        # --- Menú para seleccionar el rol ---
        ctk.CTkLabel(main_frame, text="Rol del usuario:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=5, pady=(10, 0))
        roles = self.db_manager.execute_query("SELECT nombre FROM roles ORDER BY nombre")
        role_names = [role['nombre'] for role in roles] if roles else []
        self.role_menu = ctk.CTkOptionMenu(main_frame, values=role_names, height=35)
        self.role_menu.pack(pady=5, fill="x")
        self.role_menu.set("cliente") # Valor por defecto

        self.status_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.status_label.pack(pady=(10, 0))

        # --- Botones ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", side="bottom")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_frame, text="Guardar Usuario", command=self.save_user).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="gray").grid(row=0, column=1, padx=5, sticky="ew")

    def save_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        nombre = self.name_entry.get()
        apellido = self.lastname_entry.get()
        email = self.email_entry.get()
        rol = self.role_menu.get()
        
        # Usar el método que ya teníamos en auth_manager
        result = self.auth_manager.register_user(
            username, password, email, nombre, apellido, rol
        )

        if result['success']:
            # Si se registró bien, añadimos el teléfono que es opcional
            phone = self.phone_entry.get().strip()
            if phone:
                user_id = result['user_id']
                self.db_manager.execute_modification(
                    "UPDATE usuarios SET telefono = %s WHERE id_usuario = %s",
                    (phone, user_id)
                )
            
            self.on_close_callback()
            self.destroy()
        else:
            self.status_label.configure(text=f"Error: {result['message']}")
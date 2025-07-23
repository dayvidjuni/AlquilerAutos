# Archivo: renta_autos_app/gui/add_vehicle_window.py
import customtkinter as ctk
from database_manager import DatabaseManager

class AddVehicleWindow(ctk.CTkToplevel):
    def __init__(self, master, db_manager: DatabaseManager, on_close_callback):
        super().__init__(master)
        self.db_manager = db_manager
        self.on_close_callback = on_close_callback # Función para refrescar la lista principal

        self.title("Añadir Nuevo Vehículo")
        self.geometry("450x550")
        self.resizable(False, False)
        self.transient(master) # Mantiene esta ventana por encima de la principal
        self.grab_set() # Bloquea la interacción con la ventana principal

        # --- Frame principal ---
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Datos del Nuevo Vehículo", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 20))

        # --- Campos del formulario ---
        self.models_map = {} # Diccionario para mapear "Nombre a mostrar" -> id_modelo
        models_data = self.db_manager.get_all_models_for_dropdown()
        model_names = []
        if models_data:
            for model in models_data:
                self.models_map[model['display_name']] = model['id_modelo']
                model_names.append(model['display_name'])

        self.model_menu = ctk.CTkOptionMenu(main_frame, values=model_names, height=35)
        self.model_menu.pack(pady=10, fill="x")
        self.model_menu.set("Seleccionar Modelo" if not model_names else model_names[0])
        
        self.plate_entry = ctk.CTkEntry(main_frame, placeholder_text="Placa (ej: P-123ABC)", height=35)
        self.plate_entry.pack(pady=10, fill="x")
        
        self.year_entry = ctk.CTkEntry(main_frame, placeholder_text="Año (ej: 2023)", height=35)
        self.year_entry.pack(pady=10, fill="x")

        self.color_entry = ctk.CTkEntry(main_frame, placeholder_text="Color", height=35)
        self.color_entry.pack(pady=10, fill="x")

        self.km_entry = ctk.CTkEntry(main_frame, placeholder_text="Kilometraje", height=35)
        self.km_entry.pack(pady=10, fill="x")

        self.price_entry = ctk.CTkEntry(main_frame, placeholder_text="Precio Diario (ej: 55.00)", height=35)
        self.price_entry.pack(pady=10, fill="x")

        self.status_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.status_label.pack(pady=(10, 0))

        # --- Botones ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", side="bottom")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Guardar Vehículo", command=self.save_vehicle).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, fg_color="gray").grid(row=0, column=1, padx=5, sticky="ew")

    def save_vehicle(self):
        # Obtener los datos de los campos
        selected_model_name = self.model_menu.get()
        id_modelo = self.models_map.get(selected_model_name)
        placa = self.plate_entry.get().strip()
        anio = self.year_entry.get().strip()
        color = self.color_entry.get().strip()
        km = self.km_entry.get().strip()
        precio = self.price_entry.get().strip()

        # Validaciones básicas
        if not all([id_modelo, placa, anio, color, km, precio]) or selected_model_name == "Seleccionar Modelo":
            self.status_label.configure(text="Error: Todos los campos son obligatorios.")
            return
        
        try:
            # Insertar en la base de datos
            query = """
                INSERT INTO vehiculos (id_modelo, placa, anio, color, kilometraje, precio_diario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (id_modelo, placa, int(anio), color, int(km), float(precio))
            self.db_manager.execute_modification(query, params)
            
            # Si todo fue bien, llamar al callback para refrescar la lista y cerrar la ventana
            self.on_close_callback()
            self.destroy()

        except ValueError:
            self.status_label.configure(text="Error: Año, Kilometraje y Precio deben ser números.")
        except Exception as e:
            if "Duplicate entry" in str(e):
                self.status_label.configure(text=f"Error: La placa '{placa}' ya existe.")
            else:
                self.status_label.configure(text="Error al guardar en la base de datos.")
            print(f"Error en save_vehicle: {e}")
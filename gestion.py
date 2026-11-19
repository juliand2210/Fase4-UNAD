from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os

# CONFIGURACION LOGS
logging.basicConfig(
    filename="Logs_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"  # Se fuerza encoding="utf-8" para evitar errores de decodificación al leer caracteres con tildes desde la interfaz gráfica.
)

# EXCEPCIONES PERSONALIZADAS
class ClienteError(Exception):#Excepcion lanzada ante datos invalidos o clientes duplicados.
    pass
class ServicioError(Exception):
    pass
class ReservaError(Exception):
    pass

# CLASE ABSTRACTA ENTIDAD
class Entidad(ABC):
    @abstractmethod
    def obtener_informacion(self):
        pass

# CLIENTE
class Cliente(Entidad):# representa a un cliente registrado y valida sus datos basicos

    def __init__(self, nombre, documento, email):
        if not nombre.strip():
            raise ClienteError("El nombre no puede estar vacío")# en estas lineas se garantiza que el nombre, documento y email sean correctos
        if not documento.strip():
            raise ClienteError("El documento es obligatorio")
        if "@" not in email:
            raise ClienteError("Correo inválido")
        # encapsulamiento a travez de atrubutos privados
        self.__nombre = nombre
        self.__documento = documento
        self.__email = email

    @property
    def nombre(self):
        return self.__nombre
    @property
    def documento(self):
        return self.__documento
    @property
    def email(self):
        return self.__email
    def obtener_informacion(self):
        return (
            f"{self.__nombre} - "
            f"Doc: {self.__documento} "
            f"({self.__email})"
        )

# SERVICIO ABSTRACTO
class Servicio(ABC):

    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def validar(self):
        pass
    @abstractmethod
    def calcular_costo(self, duracion):
        pass
    @abstractmethod
    def descripcion(self):
        pass
    def calcular_total(self,duracion,impuesto=0,descuento=0):
        total = self.calcular_costo(duracion)
        total += total * impuesto
        total -= total * descuento
        return round(total, 2)



# RESERVA DE SALA
class ReservaSala(Servicio):

    TARIFA = 100000  # Tarifa por hora
    def __init__(self, capacidad):
        super().__init__("Reserva Sala")
        try:
            self.capacidad = int(capacidad)
        except ValueError:
            raise ServicioError("La capacidad de la sala debe ser un número entero válido")
    def validar(self):
        if self.capacidad <= 0:
            raise ServicioError("Capacidad de sala inválida (debe ser mayor a 0)")
    def calcular_costo(self, horas):
        self.validar()
        try:
            h = int(horas)
        except ValueError:
            raise ServicioError("Las horas deben ser un número entero")
        if h <= 0:
            raise ServicioError("Las horas de reserva deben ser mayores a 0")
        return h * self.TARIFA
    def descripcion(self):
        return f"Sala para {self.capacidad} personas"

# ALQUILER EQUIPO
class AlquilerEquipo(Servicio):
    TARIFA = 50000  # Tarifa por día
    def __init__(self, equipo):
        super().__init__("Alquiler Equipo")
        self.equipo = equipo.strip()
    def validar(self):
        if not self.equipo:
            raise ServicioError("El nombre del equipo es obligatorio")       
        if self.equipo.isdigit():
            raise ServicioError("El nombre del equipo no puede ser solo un número")
    def calcular_costo(self, dias):
        self.validar()
        try:
            d = int(dias)
        except ValueError:
            raise ServicioError("Los días deben ser un número entero")
        if d <= 0:
            raise ServicioError("Los días de alquiler deben ser mayores a 0")
        return d * self.TARIFA
    def descripcion(self):
        return f"Equipo: {self.equipo}"

# ASESORIA
class AsesoriaEspecializada(Servicio):
    TARIFA = 90000  # Tarifa por hora
    def __init__(self, experto):
        super().__init__("Asesoría")
        self.experto = experto.strip()
    def validar(self):
        if not self.experto:
            raise ServicioError("El nombre del experto es obligatorio")
        if self.experto.isdigit():   # evita que el nombre del asesor sea un número
            raise ServicioError("El nombre del experto no puede ser un número")
    def calcular_costo(self, horas):
        self.validar()
        try:
            h = int(horas)
        except ValueError:
            raise ServicioError("Las horas deben ser un número entero")
        if h <= 0:
            raise ServicioError("Las horas de asesoría deben ser mayores a 0")
        return h * self.TARIFA
    def descripcion(self):
        return f"Asesor: {self.experto}"

# RESERVA
class Reserva:

    def __init__(self,cliente,servicio,duracion):
        self.cliente = cliente
        self.servicio = servicio       
        try:
            self.duracion = int(duracion)
        except ValueError:
            raise ReservaError("La duración debe ser un número entero")           
        self.estado = "Pendiente"
    def confirmar(self):
        try:
            if self.duracion <= 0:
                raise ReservaError("Duración inválida")
            costo = self.servicio.calcular_costo(self.duracion) # realiza el cálculo al servicio usando la duración de esta reserva
            self.estado = "Confirmada"
            logging.info(
                f"Reserva confirmada para "
                f"{self.cliente.nombre} | Servicio: {self.servicio.nombre}"
            )
            return costo
        except Exception as e:
            logging.error(str(e))
            raise ReservaError(
                f"Error al confirmar reserva: {str(e)}"
            ) from e

    def cancelar(self):
        self.estado = "Cancelada"
        logging.info(
            f"Reserva cancelada "
            f"{self.cliente.nombre}"
        )

    def actualizar_duracion(
            self,
            nueva_duracion):
        try:
            nueva = int(nueva_duracion)
        except ValueError:
            raise ReservaError("La duración debe ser un número entero")
        if nueva <= 0:
            raise ReservaError(
                "Duración inválida"
            )
        self.duracion = nueva

# GESTOR
class GestorReservas:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
    def agregar_cliente(self, cliente):# impide registrar dos clientes con el mismo documento
        for c in self.clientes:
            if c.documento == cliente.documento:
                raise ClienteError(
                    "Cliente duplicado"
                )
        self.clientes.append(cliente)
    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)



# INTERFAZ GRAFICA CON TKINTEK

class SoftwareFJGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión - Julian Ortiz")
        self.root.geometry("1350x720") # ancho optimizado para la tabla de reservas
        self.root.configure(bg="#F1F8E9")
        self.gestor = GestorReservas()
        self.crear_estilos()
        self.crear_interfaz()

    def crear_estilos(self):# se configura el estilos y tipografia
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(".", font=("Segoe UI", 10))
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 8])

    def crear_interfaz(self):# se crea el encabezado y las pestañas
        titulo = tk.Label(self.root,text="Sistema de Gestión de Usuarios y reservas",font=("Segoe UI", 18, "bold"),bg="#F1F8E9",fg="#1B5E20")
        titulo.pack(pady=10)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        self.tab_clientes = tk.Frame(notebook, bg="#FFFFFF")
        self.tab_servicios = tk.Frame(notebook, bg="#FFFFFF")
        self.tab_reservas = tk.Frame(notebook, bg="#FFFFFF")
        self.tab_logs = tk.Frame(notebook, bg="#FFFFFF")
        notebook.add(self.tab_clientes, text="Clientes")
        notebook.add(self.tab_servicios, text="Servicios")
        notebook.add(self.tab_reservas, text="Reservas")
        notebook.add(self.tab_logs, text="Registros (Logs)")

        self.crear_tab_clientes()
        self.crear_tab_servicios()
        self.crear_tab_reservas()
        self.crear_tab_logs()

    # CLIENTES
    def crear_tab_clientes(self):# crea el formulario de registro de los clientes

        tk.Label(self.tab_clientes, text="Nombre", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.ent_nombre = tk.Entry(self.tab_clientes, font=("Segoe UI", 10), width=25)
        self.ent_nombre.grid(row=0, column=1, padx=10, pady=15)

        tk.Label(self.tab_clientes, text="Documento", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=15, pady=15, sticky="w")
        self.ent_documento = tk.Entry(self.tab_clientes, font=("Segoe UI", 10), width=25)
        self.ent_documento.grid(row=1, column=1, padx=10, pady=15)

        tk.Label(self.tab_clientes, text="Email", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=15, pady=15, sticky="w")
        self.ent_email = tk.Entry(self.tab_clientes, font=("Segoe UI", 10), width=25)
        self.ent_email.grid(row=2, column=1, padx=10, pady=15)

        btn_cliente = tk.Button(self.tab_clientes,text="Registrar Cliente",command=self.registrar_cliente,bg="#2E7D32", fg="white",font=("Segoe UI", 10, "bold"),padx=10, pady=5, relief="flat", cursor="hand2")
        btn_cliente.grid(row=3, column=0, columnspan=2, pady=15)
        self.tv_clientes = ttk.Treeview(self.tab_clientes,columns=("Documento", "Nombre", "Email"),show="headings",height=12)

        for col in ("Documento", "Nombre", "Email"):
            self.tv_clientes.heading(col, text=col)

        self.tv_clientes.grid(row=4, column=0, columnspan=4, padx=15, pady=10)
 
    # SERVICIOS
    def crear_tab_servicios(self):
        tk.Label(self.tab_servicios, text="Tipo", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # crea un selector para escoger el tipo de servicio
        self.cb_tipo = ttk.Combobox(self.tab_servicios,values=["Reserva Sala", "Alquiler Equipo", "Asesoría"],state="readonly",width=23)
        self.cb_tipo.grid(row=0, column=1, padx=10, pady=15)
        self.cb_tipo.bind("<<ComboboxSelected>>", self.actualizar_ayuda_parametro)

        self.lbl_tarifa_info = tk.Label(self.tab_servicios,text="",font=("Segoe UI", 10, "bold"),fg="#1B5E20",bg="#FFFFFF")
        self.lbl_tarifa_info.grid(row=0, column=2, padx=15, pady=15, sticky="w")

        self.lbl_param1 = tk.Label(self.tab_servicios, text="Parámetro", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold"))
        self.lbl_param1.grid(row=1, column=0, padx=15, pady=15, sticky="w")

        self.ent_param1 = tk.Entry(self.tab_servicios, font=("Segoe UI", 10), width=25)
        self.ent_param1.grid(row=1, column=1, padx=10, pady=15)

        self.lbl_ayuda_detalle = tk.Label(self.tab_servicios, text="", font=("Segoe UI", 9, "italic"), fg="gray", bg="#FFFFFF")
        self.lbl_ayuda_detalle.grid(row=1, column=2, padx=15, pady=15, sticky="w")

        #tk.Label(self.tab_servicios,text="* Nota: La duración (horas/días) se indica al momento de crear la reserva.",font=("Segoe UI", 9, "italic"),fg="#2E7D32",bg="#FFFFFF").grid(row=2, column=0, columnspan=3, padx=15, pady=5, sticky="w")

        btn_servicio = tk.Button(self.tab_servicios,text="Crear Servicio",command=self.crear_servicio,bg="#2E7D32", fg="white",font=("Segoe UI", 10, "bold"),padx=10, pady=5, relief="flat", cursor="hand2")
        btn_servicio.grid(row=3, column=0, columnspan=2, pady=15)

        self.tv_servicios = ttk.Treeview(self.tab_servicios,columns=("Tipo", "Descripción"),show="headings",height=10)

        for col in ("Tipo", "Descripción"):
            self.tv_servicios.heading(col, text=col)

        self.tv_servicios.grid(row=4, column=0, columnspan=4, padx=15, pady=10)

    def actualizar_ayuda_parametro(self, event=None):# muestra el valor de cada servicio escogido
        seleccion = self.cb_tipo.get()
        if seleccion == "Reserva Sala":
            self.lbl_param1.config(text="Capacidad")
            self.lbl_ayuda_detalle.config(text="Número entero (Ej: 10)")
            self.lbl_tarifa_info.config(text=f"Tarifa: ${ReservaSala.TARIFA:,.0f} / hora")
        elif seleccion == "Alquiler Equipo":
            self.lbl_param1.config(text="Nombre del Equipo")
            self.lbl_ayuda_detalle.config(text="Texto obligatorio (Ej: Proyector HD)")
            self.lbl_tarifa_info.config(text=f"Tarifa: ${AlquilerEquipo.TARIFA:,.0f} / día")
        elif seleccion == "Asesoría":
            self.lbl_param1.config(text="Nombre del Experto")
            self.lbl_ayuda_detalle.config(text="Texto obligatorio (Ej: Ing. Carlos)")
            self.lbl_tarifa_info.config(text=f"Tarifa: ${AsesoriaEspecializada.TARIFA:,.0f} / hora")

    # RESERVAS
    def crear_tab_reservas(self):

        tk.Label(self.tab_reservas, text="Cliente", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.cb_cliente = ttk.Combobox(self.tab_reservas, state="readonly", width=35)
        self.cb_cliente.grid(row=0, column=1, padx=10, pady=15)
        tk.Label(self.tab_reservas, text="Servicio", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, padx=15, pady=15, sticky="w")
        self.cb_servicio = ttk.Combobox(self.tab_reservas, state="readonly", width=35)
        self.cb_servicio.grid(row=1, column=1, padx=10, pady=15)
        tk.Label(self.tab_reservas, text="Duración", bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, padx=15, pady=15, sticky="w")
        self.ent_duracion = tk.Entry(self.tab_reservas, font=("Segoe UI", 10), width=37)
        self.ent_duracion.grid(row=2, column=1, padx=10, pady=15)     
        tk.Label(self.tab_reservas, text="* Horas (Salas/Asesorías) o Días (Equipos)", font=("Segoe UI", 9, "italic"), fg="gray", bg="#FFFFFF").grid(row=2, column=2, padx=15, pady=15, sticky="w")
        
        btn_crear_res = tk.Button(self.tab_reservas, text="Crear Reserva", command=self.crear_reserva, bg="#2E7D32", fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=5, relief="flat", cursor="hand2")
        btn_crear_res.grid(row=3, column=0, padx=5, pady=15)       
        btn_can_res = tk.Button(self.tab_reservas, text="Cancelar Reserva", command=self.cancelar_reserva, bg="#C62828", fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=5, relief="flat", cursor="hand2")
        btn_can_res.grid(row=3, column=1, padx=5, pady=15,sticky="w")

        self.tv_reservas = ttk.Treeview(self.tab_reservas,columns=("Cliente", "Servicio", "Duración", "Costo", "Estado"),show="headings",height=10)# se crean las columnas de la tabla

        # Ajuste de ancho de columnas para que no se corte nada
        self.tv_reservas.column("Cliente", width=340, anchor="w")
        self.tv_reservas.column("Servicio", width=250, anchor="w")
        self.tv_reservas.column("Duración", width=90, anchor="center")
        self.tv_reservas.column("Costo", width=100, anchor="e")
        self.tv_reservas.column("Estado", width=90, anchor="center")

        for col in ("Cliente", "Servicio", "Duración", "Costo", "Estado"):
            self.tv_reservas.heading(col, text=col)

        self.tv_reservas.grid(row=4, column=0, columnspan=5, padx=15, pady=10)
 
    # PESTAÑA DE LOGS (REGISTROS)
    def crear_tab_logs(self):
        tk.Label(self.tab_logs,text="Historial de Eventos y Errores del Sistema (software_fj.log)",font=("Segoe UI", 11, "bold"),bg="#FFFFFF",fg="#1B5E20").pack(anchor="w", padx=15, pady=10)

        frame_txt = tk.Frame(self.tab_logs, bg="#FFFFFF")
        frame_txt.pack(fill="both", expand=True, padx=15, pady=5)
        scrollbar = tk.Scrollbar(frame_txt)
        scrollbar.pack(side="right", fill="y")
        self.txt_logs = tk.Text(frame_txt,wrap="word",yscrollcommand=scrollbar.set,font=("Consolas", 10),bg="#FAFAFA",fg="#333333",padx=10, pady=10)
        self.txt_logs.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.txt_logs.yview)
        frame_btns = tk.Frame(self.tab_logs, bg="#FFFFFF")
        frame_btns.pack(fill="x", padx=15, pady=10)
        btn_actualizar_log = tk.Button(frame_btns,text="Actualizar Logs",command=self.cargar_contenido_logs,bg="#37474F", fg="white",font=("Segoe UI", 9, "bold"),padx=10, pady=5, relief="flat", cursor="hand2")
        btn_actualizar_log.pack(side="left")
        self.cargar_contenido_logs()

    def cargar_contenido_logs(self):
        self.txt_logs.delete("1.0", tk.END)
        if os.path.exists("Logs_fj.log"):
            try:
                # Se usa errors="ignore" para prevenir cualquier fallo futuro de lectura de caracteres
                with open("Logs_fj.log", "r", encoding="utf-8", errors="ignore") as archivo:
                    contenido = archivo.read()
                    if contenido.strip() == "":
                        contenido = "El archivo de registro está vacío actualmente."
                    self.txt_logs.insert(tk.END, contenido)
            except Exception as e:
                self.txt_logs.insert(tk.END, f"Error al leer el archivo de logs: {str(e)}")
        else:
            self.txt_logs.insert(tk.END, "Aún no se ha generado ningún archivo de registro (Logs_fj.log).")

    # FUNCIONES GLOBALES DEL PROGRAMA
    def actualizar_combos(self):
        self.cb_cliente["values"] = [
            f"{c.nombre} - Doc: {c.documento} ({c.email})"
            for c in self.gestor.clientes
        ]
        self.cb_servicio["values"] = [
            f"{s.nombre} - {s.descripcion()}"
            for s in self.gestor.servicios
        ]
    def registrar_cliente(self):
        try:
            cliente = Cliente(
                self.ent_nombre.get(),
                self.ent_documento.get(),
                self.ent_email.get()
            )
            self.gestor.agregar_cliente(cliente)
            self.tv_clientes.insert("", tk.END, values=(cliente.documento, cliente.nombre, cliente.email))
            self.actualizar_combos()
            messagebox.showinfo("Éxito", "Cliente registrado correctamente")
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", str(e))
        finally:
            self.cargar_contenido_logs()

    def crear_servicio(self):
        try:
            tipo = self.cb_tipo.get()
            dato1 = self.ent_param1.get()
            if not tipo:
                raise ServicioError("Seleccione un tipo de servicio")
            if tipo == "Reserva Sala":
                servicio = ReservaSala(dato1)
            elif tipo == "Alquiler Equipo":
                servicio = AlquilerEquipo(dato1)
            else:
                servicio = AsesoriaEspecializada(dato1)
            servicio.validar()
            self.gestor.agregar_servicio(servicio)
            self.tv_servicios.insert("", tk.END, values=(servicio.nombre, servicio.descripcion()))
            self.actualizar_combos()
            messagebox.showinfo("Éxito", "Servicio creado correctamente en el catálogo")
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", str(e))
        finally:
            self.cargar_contenido_logs()

    def crear_reserva(self):
        try:
            if not self.cb_cliente.get() or not self.cb_servicio.get():
                raise ReservaError("Debe seleccionar un cliente y un servicio")
            cliente = self.gestor.clientes[self.cb_cliente.current()]
            servicio = self.gestor.servicios[self.cb_servicio.current()]
            duracion = self.ent_duracion.get()
            reserva = Reserva(cliente, servicio, duracion)
            costo = reserva.confirmar()
            self.gestor.agregar_reserva(reserva)
            sufijo = "días" if isinstance(servicio, AlquilerEquipo) else "horas"
            duracion_texto = f"{reserva.duracion} {sufijo}"
            info_cliente = f"{cliente.nombre} - Doc: {cliente.documento} ({cliente.email})"
            info_servicio = servicio.descripcion()
            self.tv_reservas.insert("", tk.END, values=(info_cliente, info_servicio, duracion_texto, f"${costo:,.2f}", reserva.estado))
            messagebox.showinfo("Reserva", f"Reserva confirmada con éxito. Costo total: ${costo:,.2f}")
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", str(e))
        finally:
            self.cargar_contenido_logs()

    def cancelar_reserva(self):
        try:
            item = self.tv_reservas.selection()
            if not item:
                raise ReservaError("Seleccione una reserva de la tabla")
            fila = item[0]
            indice = self.tv_reservas.index(fila)
            reserva = self.gestor.reservas[indice]
            reserva.cancelar()
            sufijo = "días" if isinstance(reserva.servicio, AlquilerEquipo) else "horas"
            duracion_texto = f"{reserva.duracion} {sufijo}"
            info_cliente = f"{reserva.cliente.nombre} - Doc: {reserva.cliente.documento} ({reserva.cliente.email})"
            info_servicio = reserva.servicio.descripcion()
            costo_actual = reserva.servicio.calcular_costo(reserva.duracion)
            self.tv_reservas.item(
                fila,
                values=(info_cliente, info_servicio, duracion_texto, f"${costo_actual:,.2f}", reserva.estado)
            )
            messagebox.showinfo("Cancelada", "Reserva cancelada exitosamente")
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", str(e))
        finally:
            self.cargar_contenido_logs()

# MAIN
if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareFJGUI(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox

class Cliente(Entidad):

    def __init__(self, nombre, documento, email):

        if not nombre.strip():
            raise ClienteError("El nombre no puede estar vacío")

        if not documento.strip():
            raise ClienteError("El documento es obligatorio")

        if "@" not in email:
            raise ClienteError("Correo inválido")

        self.__nombre = nombre
        self.__documento = documento
        self.__email = email

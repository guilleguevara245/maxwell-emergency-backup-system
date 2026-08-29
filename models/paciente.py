"""
Maxwell Medic System - by Guillermo Guevara

Modelo de Paciente: representa la entidad y sus operaciones
contra la base de datos (crear, leer, actualizar, borrar).
El DNI es la clave primaria: es un dato real, no un numero generado.
"""

from database import obtener_conexion
from utils.validaciones import validar_dni, validar_email, validar_telefono, validar_telefono_fijo


class Paciente:
    def __init__(self, nombre, apellido, dni, telefono, email, telefono_fijo=None):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.telefono_fijo = telefono_fijo
        self.email = email

    def __str__(self):
        return f"[DNI {self.dni}] {self.nombre} {self.apellido}"

    def guardar(self):
        """
        Inserta el paciente en la base de datos usando el DNI como clave.
        Valida el formato de DNI, telefono y email antes de guardar.
        """
        validar_dni(self.dni)
        validar_telefono(self.telefono)
        validar_telefono_fijo(self.telefono_fijo)
        validar_email(self.email)

        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO pacientes (dni, nombre, apellido, telefono, telefono_fijo, email)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.dni, self.nombre, self.apellido, self.telefono, self.telefono_fijo, self.email),
            )
            conexion.commit()
        finally:
            conexion.close()

    @staticmethod
    def listar_todos():
        """
        Devuelve una lista con todos los pacientes registrados.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT dni, nombre, apellido, telefono, telefono_fijo, email FROM pacientes"
        )
        filas = cursor.fetchall()
        conexion.close()

        pacientes = []
        for fila in filas:
            pacientes.append(Paciente(
                dni=fila[0], nombre=fila[1], apellido=fila[2],
                telefono=fila[3], telefono_fijo=fila[4], email=fila[5]
            ))
        return pacientes

    @staticmethod
    def buscar_por_dni(dni):
        """
        Busca un paciente por su DNI. Devuelve None si no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT dni, nombre, apellido, telefono, telefono_fijo, email FROM pacientes WHERE dni = ?",
            (dni,),
        )
        fila = cursor.fetchone()
        conexion.close()

        if fila is None:
            return None
        return Paciente(dni=fila[0], nombre=fila[1], apellido=fila[2],
                         telefono=fila[3], telefono_fijo=fila[4], email=fila[5])

    def actualizar(self):
        """
        Actualiza los datos del paciente en la base de datos (usa self.dni).
        Valida el formato de telefono y email antes de actualizar.
        """
        validar_telefono(self.telefono)
        validar_telefono_fijo(self.telefono_fijo)
        validar_email(self.email)

        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE pacientes
                SET nombre = ?, apellido = ?, telefono = ?, telefono_fijo = ?, email = ?
                WHERE dni = ?
                """,
                (self.nombre, self.apellido, self.telefono,
                 self.telefono_fijo, self.email, self.dni),
            )
            conexion.commit()
        finally:
            conexion.close()

    @staticmethod
    def eliminar(dni):
        """
        Elimina un paciente de la base de datos segun su DNI.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM pacientes WHERE dni = ?", (dni,))
        conexion.commit()
        conexion.close()

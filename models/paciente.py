"""
Maxwell Emergency Backup System - by Guillermo Guevara

Modelo de Paciente: representa la entidad y sus operaciones
contra la base de datos (crear, leer, actualizar, borrar).
El DNI es la clave primaria: es un dato real, no un numero generado.
Usa borrado logico: "eliminar" marca al paciente como inactivo,
no borra el registro (para conservar el historial de turnos).
"""

from database import obtener_conexion
from utils.validaciones import validar_dni, validar_email, validar_telefono, validar_telefono_fijo


class Paciente:
    def __init__(self, nombre, apellido, dni, telefono, email, telefono_fijo=None,
                 activo=True, fecha_registro=None):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.telefono_fijo = telefono_fijo
        self.email = email
        self.activo = bool(activo)
        self.fecha_registro = fecha_registro

    def __str__(self):
        etiqueta = "" if self.activo else " (INACTIVO)"
        return f"[DNI {self.dni}] {self.nombre} {self.apellido}{etiqueta}"

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
    def listar_todos(incluir_inactivos=False):
        """
        Devuelve una lista con los pacientes registrados.
        Por defecto solo devuelve los activos.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        consulta = ("SELECT dni, nombre, apellido, telefono, telefono_fijo, "
                    "email, activo, fecha_registro FROM pacientes")
        if not incluir_inactivos:
            consulta += " WHERE activo = 1"
        cursor.execute(consulta)
        filas = cursor.fetchall()
        conexion.close()

        return [Paciente(dni=f[0], nombre=f[1], apellido=f[2], telefono=f[3],
                          telefono_fijo=f[4], email=f[5], activo=f[6], fecha_registro=f[7])
                for f in filas]

    @staticmethod
    def buscar_por_dni(dni):
        """
        Busca un paciente por su DNI (activo o inactivo). Devuelve None si no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT dni, nombre, apellido, telefono, telefono_fijo, email, activo, fecha_registro
            FROM pacientes WHERE dni = ?
            """,
            (dni,),
        )
        fila = cursor.fetchone()
        conexion.close()

        if fila is None:
            return None
        return Paciente(dni=fila[0], nombre=fila[1], apellido=fila[2], telefono=fila[3],
                         telefono_fijo=fila[4], email=fila[5], activo=fila[6], fecha_registro=fila[7])

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
        Borrado logico: marca al paciente como inactivo en vez de
        borrar el registro, para conservar el historial de turnos.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE pacientes SET activo = 0 WHERE dni = ?", (dni,))
        conexion.commit()
        conexion.close()

    @staticmethod
    def reactivar(dni):
        """
        Revierte un borrado logico: vuelve a marcar al paciente como activo.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE pacientes SET activo = 1 WHERE dni = ?", (dni,))
        conexion.commit()
        conexion.close()

    @staticmethod
    def eliminar_todos():
        """
        Borra TODOS los pacientes de la base local, sin posibilidad de
        deshacerlo. Se usa al cerrar el uso diario de Maxwell, despues
        de exportar los datos: los pacientes son informacion transitoria
        de una jornada de emergencia, no un registro permanente.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM pacientes")
        conexion.commit()
        conexion.close()

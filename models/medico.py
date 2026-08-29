"""
Maxwell Medic System - by Guillermo Guevara

Modelo de Medico: representa la entidad y sus operaciones
contra la base de datos (crear, leer, actualizar, borrar).
El legajo es la clave primaria: funciona como identidad institucional
y matricula profesional a la vez.
El DNI, telefono y email se guardan como datos personales de contacto.
Usa borrado logico: "eliminar" marca al medico como inactivo,
no borra el registro (para conservar el historial de turnos).
"""

from database import obtener_conexion
from utils.validaciones import validar_legajo, validar_dni, validar_telefono, validar_email


class Medico:
    def __init__(self, legajo, dni, nombre, apellido, especialidad, telefono, email,
                 activo=True, fecha_registro=None):
        self.legajo = legajo
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.especialidad = especialidad
        self.telefono = telefono
        self.email = email
        self.activo = bool(activo)
        self.fecha_registro = fecha_registro

    def __str__(self):
        etiqueta = "" if self.activo else " (INACTIVO)"
        return f"[Legajo {self.legajo}] Dr/a. {self.nombre} {self.apellido} - {self.especialidad}{etiqueta}"

    def guardar(self):
        """
        Inserta el medico en la base de datos usando el legajo como clave.
        """
        validar_legajo(self.legajo)
        validar_dni(self.dni)
        validar_telefono(self.telefono)
        validar_email(self.email)

        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO medicos (legajo, dni, nombre, apellido, especialidad, telefono, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self.legajo, self.dni, self.nombre, self.apellido,
                 self.especialidad, self.telefono, self.email),
            )
            conexion.commit()
        finally:
            conexion.close()

    @staticmethod
    def listar_todos(incluir_inactivos=False):
        """
        Devuelve una lista con los medicos registrados.
        Por defecto solo devuelve los activos.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        consulta = ("SELECT legajo, dni, nombre, apellido, especialidad, telefono, "
                    "email, activo, fecha_registro FROM medicos")
        if not incluir_inactivos:
            consulta += " WHERE activo = 1"
        cursor.execute(consulta)
        filas = cursor.fetchall()
        conexion.close()

        return [Medico(legajo=f[0], dni=f[1], nombre=f[2], apellido=f[3], especialidad=f[4],
                        telefono=f[5], email=f[6], activo=f[7], fecha_registro=f[8])
                for f in filas]

    @staticmethod
    def buscar_por_legajo(legajo):
        """
        Busca un medico por su legajo (activo o inactivo). Devuelve None si no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT legajo, dni, nombre, apellido, especialidad, telefono, email, activo, fecha_registro
            FROM medicos WHERE legajo = ?
            """,
            (legajo,),
        )
        fila = cursor.fetchone()
        conexion.close()

        if fila is None:
            return None
        return Medico(legajo=fila[0], dni=fila[1], nombre=fila[2], apellido=fila[3],
                       especialidad=fila[4], telefono=fila[5], email=fila[6],
                       activo=fila[7], fecha_registro=fila[8])

    @staticmethod
    def listar_por_especialidad(especialidad):
        """
        Devuelve los medicos activos que coinciden con una especialidad dada.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT legajo, dni, nombre, apellido, especialidad, telefono, email, activo, fecha_registro
            FROM medicos WHERE especialidad = ? AND activo = 1
            """,
            (especialidad,),
        )
        filas = cursor.fetchall()
        conexion.close()

        return [Medico(legajo=f[0], dni=f[1], nombre=f[2], apellido=f[3], especialidad=f[4],
                        telefono=f[5], email=f[6], activo=f[7], fecha_registro=f[8]) for f in filas]

    def actualizar(self):
        """
        Actualiza los datos del medico en la base de datos (usa self.legajo).
        """
        validar_telefono(self.telefono)
        validar_email(self.email)

        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE medicos
                SET dni = ?, nombre = ?, apellido = ?, especialidad = ?, telefono = ?, email = ?
                WHERE legajo = ?
                """,
                (self.dni, self.nombre, self.apellido, self.especialidad,
                 self.telefono, self.email, self.legajo),
            )
            conexion.commit()
        finally:
            conexion.close()

    @staticmethod
    def eliminar(legajo):
        """
        Borrado logico: marca al medico como inactivo en vez de
        borrar el registro, para conservar el historial de turnos.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE medicos SET activo = 0 WHERE legajo = ?", (legajo,))
        conexion.commit()
        conexion.close()

    @staticmethod
    def reactivar(legajo):
        """
        Revierte un borrado logico: vuelve a marcar al medico como activo.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE medicos SET activo = 1 WHERE legajo = ?", (legajo,))
        conexion.commit()
        conexion.close()

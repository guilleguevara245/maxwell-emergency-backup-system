"""
Maxwell Medic System - by Guillermo Guevara

Modelo de Medico: representa la entidad y sus operaciones
contra la base de datos (crear, leer, actualizar, borrar).
El legajo es la clave primaria: funciona como identidad institucional
y matricula profesional a la vez.
El DNI, telefono y email se guardan como datos personales de contacto.
"""

from database import obtener_conexion
from utils.validaciones import validar_legajo, validar_dni, validar_telefono, validar_email


class Medico:
    def __init__(self, legajo, dni, nombre, apellido, especialidad, telefono, email):
        self.legajo = legajo
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.especialidad = especialidad
        self.telefono = telefono
        self.email = email

    def __str__(self):
        return f"[Legajo {self.legajo}] Dr/a. {self.nombre} {self.apellido} - {self.especialidad}"

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
    def listar_todos():
        """
        Devuelve una lista con todos los medicos registrados.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT legajo, dni, nombre, apellido, especialidad, telefono, email FROM medicos")
        filas = cursor.fetchall()
        conexion.close()

        medicos = []
        for fila in filas:
            medicos.append(Medico(legajo=fila[0], dni=fila[1], nombre=fila[2], apellido=fila[3],
                                   especialidad=fila[4], telefono=fila[5], email=fila[6]))
        return medicos

    @staticmethod
    def buscar_por_legajo(legajo):
        """
        Busca un medico por su legajo. Devuelve None si no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT legajo, dni, nombre, apellido, especialidad, telefono, email FROM medicos WHERE legajo = ?",
            (legajo,),
        )
        fila = cursor.fetchone()
        conexion.close()

        if fila is None:
            return None
        return Medico(legajo=fila[0], dni=fila[1], nombre=fila[2], apellido=fila[3],
                       especialidad=fila[4], telefono=fila[5], email=fila[6])

    @staticmethod
    def listar_por_especialidad(especialidad):
        """
        Devuelve los medicos que coinciden con una especialidad dada.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT legajo, dni, nombre, apellido, especialidad, telefono, email FROM medicos WHERE especialidad = ?",
            (especialidad,),
        )
        filas = cursor.fetchall()
        conexion.close()

        return [Medico(legajo=f[0], dni=f[1], nombre=f[2], apellido=f[3],
                        especialidad=f[4], telefono=f[5], email=f[6]) for f in filas]

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
        Elimina un medico de la base de datos segun su legajo.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM medicos WHERE legajo = ?", (legajo,))
        conexion.commit()
        conexion.close()

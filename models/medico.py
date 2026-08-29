"""
Maxwell Medic System — by Guillermo Guevara

Modelo de Medico: representa la entidad y sus operaciones
contra la base de datos (crear, leer, actualizar, borrar).
"""

from database import obtener_conexion


class Medico:
    def __init__(self, nombre, apellido, especialidad, id=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.especialidad = especialidad

    def __str__(self):
        return f"[{self.id}] Dr/a. {self.nombre} {self.apellido} — {self.especialidad}"

    def guardar(self):
        """
        Inserta el medico en la base de datos y le asigna el id generado.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO medicos (nombre, apellido, especialidad) VALUES (?, ?, ?)",
            (self.nombre, self.apellido, self.especialidad),
        )
        conexion.commit()
        self.id = cursor.lastrowid
        conexion.close()
        return self.id

    @staticmethod
    def listar_todos():
        """
        Devuelve una lista con todos los medicos registrados.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, apellido, especialidad FROM medicos")
        filas = cursor.fetchall()
        conexion.close()

        medicos = []
        for fila in filas:
            medicos.append(Medico(id=fila[0], nombre=fila[1], apellido=fila[2], especialidad=fila[3]))
        return medicos

    @staticmethod
    def buscar_por_id(id_medico):
        """
        Busca un medico por su id. Devuelve None si no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, apellido, especialidad FROM medicos WHERE id = ?",
            (id_medico,),
        )
        fila = cursor.fetchone()
        conexion.close()

        if fila is None:
            return None
        return Medico(id=fila[0], nombre=fila[1], apellido=fila[2], especialidad=fila[3])

    @staticmethod
    def listar_por_especialidad(especialidad):
        """
        Devuelve los medicos que coinciden con una especialidad dada.

        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, apellido, especialidad FROM medicos WHERE especialidad = ?",
            (especialidad,),
        )
        filas = cursor.fetchall()
        conexion.close()

        return [Medico(id=f[0], nombre=f[1], apellido=f[2], especialidad=f[3]) for f in filas]

    def actualizar(self):
        """
        Actualiza los datos del medico en la base de datos (usa self.id).
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE medicos SET nombre = ?, apellido = ?, especialidad = ? WHERE id = ?",
            (self.nombre, self.apellido, self.especialidad, self.id),
        )
        conexion.commit()
        conexion.close()

    @staticmethod
    def eliminar(id_medico):
        """
        Elimina un medico de la base de datos segun su id.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM medicos WHERE id = ?", (id_medico,))
        conexion.commit()
        conexion.close()

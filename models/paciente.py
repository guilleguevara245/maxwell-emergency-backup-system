"""
Maxwell Medic System — by Guillermo Guevara

Modelo de Paciente: representa la entidad y sus operaciones
contra la base de datos (crear, leer, actualizar, borrar).
"""

from database import obtener_conexion


class Paciente:
    def __init__(self, nombre, apellido, dni, telefono, email, telefono_fijo=None, id=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.telefono = telefono
        self.telefono_fijo = telefono_fijo
        self.email = email

    def __str__(self):
        return f"[{self.id}] {self.nombre} {self.apellido} (DNI: {self.dni})"

    def guardar(self):
        """
        Inserta el paciente en la base de datos y le asigna el id generado.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO pacientes (nombre, apellido, dni, telefono, telefono_fijo, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (self.nombre, self.apellido, self.dni, self.telefono, self.telefono_fijo, self.email),
        )
        conexion.commit()
        self.id = cursor.lastrowid
        conexion.close()
        return self.id

    @staticmethod
    def listar_todos():
        """
        Devuelve una lista con todos los pacientes registrados.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, apellido, dni, telefono, telefono_fijo, email FROM pacientes"
        )
        filas = cursor.fetchall()
        conexion.close()

        pacientes = []
        for fila in filas:
            pacientes.append(Paciente(
                id=fila[0], nombre=fila[1], apellido=fila[2], dni=fila[3],
                telefono=fila[4], telefono_fijo=fila[5], email=fila[6]
            ))
        return pacientes

    @staticmethod
    def buscar_por_id(id_paciente):
        """
        Busca un paciente por su id. Devuelve None si no existe.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre, apellido, dni, telefono, telefono_fijo, email FROM pacientes WHERE id = ?",
            (id_paciente,),
        )
        fila = cursor.fetchone()
        conexion.close()

        if fila is None:
            return None
        return Paciente(id=fila[0], nombre=fila[1], apellido=fila[2], dni=fila[3],
                         telefono=fila[4], telefono_fijo=fila[5], email=fila[6])

    def actualizar(self):
        """
        Actualiza los datos del paciente en la base de datos (usa self.id).
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE pacientes
            SET nombre = ?, apellido = ?, dni = ?, telefono = ?, telefono_fijo = ?, email = ?
            WHERE id = ?
            """,
            (self.nombre, self.apellido, self.dni, self.telefono,
             self.telefono_fijo, self.email, self.id),
        )
        conexion.commit()
        conexion.close()

    @staticmethod
    def eliminar(id_paciente):
        """
        Elimina un paciente de la base de datos segun su id.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (id_paciente,))
        conexion.commit()
        conexion.close()

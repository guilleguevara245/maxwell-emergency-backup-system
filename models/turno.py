"""
Maxwell Medic System — by Guillermo Guevara

Modelo de Turno: representa la entidad y sus operaciones,
incluyendo la validacion de disponibilidad horaria del medico.
"""

from database import obtener_conexion


class Turno:
    ESTADOS_VALIDOS = ("pendiente", "confirmado", "cancelado", "atendido")

    def __init__(self, paciente_id, medico_id, fecha, hora,
                 estado="pendiente", motivo=None, id=None):
        self.id = id
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.fecha = fecha    # formato esperado: "AAAA-MM-DD"
        self.hora = hora      # formato esperado: "HH:MM"
        self.estado = estado
        self.motivo = motivo

    def __str__(self):
        return (f"[{self.id}] {self.fecha} {self.hora} — "
                f"Paciente {self.paciente_id} / Médico {self.medico_id} — {self.estado}")

    @staticmethod
    def existe_solapamiento(medico_id, fecha, hora):
        """
        Devuelve True si el medico ya tiene un turno (no cancelado)
        agendado en esa misma fecha y hora.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM turnos
            WHERE medico_id = ? AND fecha = ? AND hora = ? AND estado != 'cancelado'
            """,
            (medico_id, fecha, hora),
        )
        cantidad = cursor.fetchone()[0]
        conexion.close()
        return cantidad > 0

    def guardar(self):
        """
        Inserta el turno en la base de datos, validando antes que
        el medico este disponible en esa fecha y hora.
        Lanza un ValueError si ya existe un turno solapado.
        """
        if Turno.existe_solapamiento(self.medico_id, self.fecha, self.hora):
            raise ValueError(
                f"El medico {self.medico_id} ya tiene un turno el {self.fecha} a las {self.hora}."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO turnos (paciente_id, medico_id, fecha, hora, estado, motivo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (self.paciente_id, self.medico_id, self.fecha, self.hora, self.estado, self.motivo),
        )
        conexion.commit()
        self.id = cursor.lastrowid
        conexion.close()
        return self.id

    @staticmethod
    def listar_por_fecha(fecha):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_id, medico_id, fecha, hora, estado, motivo
            FROM turnos WHERE fecha = ? ORDER BY hora
            """,
            (fecha,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Turno(id=f[0], paciente_id=f[1], medico_id=f[2], fecha=f[3],
                       hora=f[4], estado=f[5], motivo=f[6]) for f in filas]

    @staticmethod
    def listar_por_medico(medico_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_id, medico_id, fecha, hora, estado, motivo
            FROM turnos WHERE medico_id = ? ORDER BY fecha, hora
            """,
            (medico_id,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Turno(id=f[0], paciente_id=f[1], medico_id=f[2], fecha=f[3],
                       hora=f[4], estado=f[5], motivo=f[6]) for f in filas]

    @staticmethod
    def listar_por_paciente(paciente_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_id, medico_id, fecha, hora, estado, motivo
            FROM turnos WHERE paciente_id = ? ORDER BY fecha, hora
            """,
            (paciente_id,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Turno(id=f[0], paciente_id=f[1], medico_id=f[2], fecha=f[3],
                       hora=f[4], estado=f[5], motivo=f[6]) for f in filas]

    def cambiar_estado(self, nuevo_estado):
        """
        Cambia el estado del turno (ej: cancelar, marcar como atendido).
        """
        if nuevo_estado not in Turno.ESTADOS_VALIDOS:
            raise ValueError(f"Estado invalido: {nuevo_estado}")

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE turnos SET estado = ? WHERE id = ?", (nuevo_estado, self.id))
        conexion.commit()
        conexion.close()
        self.estado = nuevo_estado

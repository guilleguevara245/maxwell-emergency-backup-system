"""
Maxwell Medic System - by Guillermo Guevara

Modelo de Turno: representa la entidad y sus operaciones,
incluyendo la validacion de disponibilidad horaria del medico.
Referencia a pacientes por DNI y a medicos por legajo.
"""

from database import obtener_conexion
from utils.validaciones import validar_fecha, validar_hora, fecha_iso_a_visual


class Turno:
    ESTADOS_VALIDOS = ("pendiente", "confirmado", "cancelado", "atendido")

    def __init__(self, paciente_dni, medico_legajo, fecha, hora,
                 motivo, estado="pendiente", id=None):
        self.id = id
        self.paciente_dni = paciente_dni
        self.medico_legajo = medico_legajo
        self.fecha = fecha    # formato interno: AAAA-MM-DD
        self.hora = hora      # formato esperado: HH:MM
        self.estado = estado
        self.motivo = motivo

    def __str__(self):
        return (f"[{self.id}] {fecha_iso_a_visual(self.fecha)} {self.hora} - "
                f"Paciente DNI {self.paciente_dni} / Medico Legajo {self.medico_legajo} - {self.estado}")

    @staticmethod
    def existe_solapamiento(medico_legajo, fecha, hora):
        """
        Devuelve True si el medico ya tiene un turno (no cancelado)
        agendado en esa misma fecha y hora.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM turnos
            WHERE medico_legajo = ? AND fecha = ? AND hora = ? AND estado != 'cancelado'
            """,
            (medico_legajo, fecha, hora),
        )
        cantidad = cursor.fetchone()[0]
        conexion.close()
        return cantidad > 0

    def guardar(self):
        """
        Inserta el turno en la base de datos, validando antes que
        el medico este disponible en esa fecha y hora.
        """
        if not self.motivo or not self.motivo.strip():
            raise ValueError("El motivo de consulta es obligatorio.")

        validar_fecha(self.fecha)
        validar_hora(self.hora)

        if Turno.existe_solapamiento(self.medico_legajo, self.fecha, self.hora):
            raise ValueError(
                f"El medico con legajo {self.medico_legajo} ya tiene un turno "
                f"el {fecha_iso_a_visual(self.fecha)} a las {self.hora}."
            )

        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO turnos (paciente_dni, medico_legajo, fecha, hora, estado, motivo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.paciente_dni, self.medico_legajo, self.fecha, self.hora, self.estado, self.motivo),
            )
            conexion.commit()
            self.id = cursor.lastrowid
        finally:
            conexion.close()
        return self.id

    @staticmethod
    def listar_por_fecha(fecha):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_dni, medico_legajo, fecha, hora, estado, motivo
            FROM turnos WHERE fecha = ? ORDER BY hora
            """,
            (fecha,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Turno(id=f[0], paciente_dni=f[1], medico_legajo=f[2], fecha=f[3],
                       hora=f[4], estado=f[5], motivo=f[6]) for f in filas]

    @staticmethod
    def listar_por_medico(medico_legajo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_dni, medico_legajo, fecha, hora, estado, motivo
            FROM turnos WHERE medico_legajo = ? ORDER BY fecha, hora
            """,
            (medico_legajo,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Turno(id=f[0], paciente_dni=f[1], medico_legajo=f[2], fecha=f[3],
                       hora=f[4], estado=f[5], motivo=f[6]) for f in filas]

    @staticmethod
    def listar_por_paciente(paciente_dni):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_dni, medico_legajo, fecha, hora, estado, motivo
            FROM turnos WHERE paciente_dni = ? ORDER BY fecha, hora
            """,
            (paciente_dni,),
        )
        filas = cursor.fetchall()
        conexion.close()
        return [Turno(id=f[0], paciente_dni=f[1], medico_legajo=f[2], fecha=f[3],
                       hora=f[4], estado=f[5], motivo=f[6]) for f in filas]

    @staticmethod
    def buscar_por_id(id_turno):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id, paciente_dni, medico_legajo, fecha, hora, estado, motivo
            FROM turnos WHERE id = ?
            """,
            (id_turno,),
        )
        fila = cursor.fetchone()
        conexion.close()
        if fila is None:
            return None
        return Turno(id=fila[0], paciente_dni=fila[1], medico_legajo=fila[2],
                     fecha=fila[3], hora=fila[4], estado=fila[5], motivo=fila[6])

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

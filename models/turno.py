"""
Maxwell Emergency Backup System - by Guillermo Guevara

Modelo de Turno: representa una SOLICITUD de turno, no un turno ya
agendado. Maxwell es un sistema de respaldo que se usa cuando el
sistema principal del consultorio esta caido: registra los datos
necesarios (paciente, especialidad, medico especifico si se pidio,
motivo y observaciones) para que despues se asigne fecha y hora
en el sistema principal. Por eso no tiene fecha ni hora.

El campo "exportado" indica si la solicitud ya fue enviada al sistema
principal (via la exportacion a CSV).
"""

from database import conexion_segura


def _validar_referencias(paciente_dni, medico_legajo):
    """
    Verifica que el paciente exista y este activo. Si se especifico
    un medico en particular, tambien verifica que exista y este activo.
    Se hace aca (en vez de dejar que salte el error de clave foranea
    de SQLite) para dar un mensaje claro en vez de un traceback tecnico.
    """
    # Import diferido para evitar import circular con paciente.py/medico.py
    from models.paciente import Paciente
    from models.medico import Medico

    paciente = Paciente.buscar_por_dni(paciente_dni)
    if paciente is None:
        raise ValueError(f"No existe un paciente con DNI {paciente_dni}.")
    if not paciente.activo:
        raise ValueError(f"El paciente con DNI {paciente_dni} esta inactivo.")

    if medico_legajo:
        medico = Medico.buscar_por_legajo(medico_legajo)
        if medico is None:
            raise ValueError(f"No existe un medico con legajo {medico_legajo}.")
        if not medico.activo:
            raise ValueError(f"El medico con legajo {medico_legajo} esta inactivo.")


class Turno:
    # "atendido" queda disponible para cuando el sistema principal
    # informa que la consulta se realizo.
    ESTADOS_VALIDOS = ("pendiente", "confirmado", "cancelado", "atendido")

    CAMPOS_SELECT = ("id, paciente_dni, especialidad, medico_legajo, motivo, "
                      "observaciones, estado, exportado, fecha_registro")

    def __init__(self, paciente_dni, especialidad, motivo, medico_legajo=None,
                 observaciones=None, estado="pendiente", id=None,
                 exportado=False, fecha_registro=None):
        self.id = id
        self.paciente_dni = paciente_dni
        self.especialidad = especialidad
        self.medico_legajo = medico_legajo
        self.motivo = motivo
        self.observaciones = observaciones
        self.estado = estado
        self.exportado = bool(exportado)
        self.fecha_registro = fecha_registro

    def __str__(self):
        medico_texto = f"Legajo {self.medico_legajo}" if self.medico_legajo else "sin medico especifico"
        return (f"[{self.id}] Paciente DNI {self.paciente_dni} - {self.especialidad} "
                f"({medico_texto}) - {self.estado}")

    def guardar(self):
        """
        Inserta la solicitud de turno en la base de datos.
        Valida que el paciente exista y este activo, y si se pidio
        un medico especifico, que tambien exista y este activo.
        """
        if not self.especialidad or not self.especialidad.strip():
            raise ValueError("La especialidad es obligatoria.")
        if not self.motivo or not self.motivo.strip():
            raise ValueError("El motivo de consulta es obligatorio.")

        _validar_referencias(self.paciente_dni, self.medico_legajo)

        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO turnos (paciente_dni, especialidad, medico_legajo,
                                     motivo, observaciones, estado)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.paciente_dni, self.especialidad, self.medico_legajo,
                 self.motivo, self.observaciones, self.estado),
            )
            conexion.commit()
            self.id = cursor.lastrowid
        return self.id

    @staticmethod
    def _filas_a_turnos(filas):
        return [Turno(id=f[0], paciente_dni=f[1], especialidad=f[2], medico_legajo=f[3],
                       motivo=f[4], observaciones=f[5], estado=f[6], exportado=f[7],
                       fecha_registro=f[8]) for f in filas]

    @staticmethod
    def listar_de_hoy():
        """
        Devuelve las solicitudes registradas hoy (segun fecha_registro),
        ordenadas por hora de registro. Se usa para el listado numerado
        al cancelar una solicitud, sin necesidad de que el usuario
        conozca el ID interno.
        """
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"""
                SELECT {Turno.CAMPOS_SELECT} FROM turnos
                WHERE date(fecha_registro) = date('now')
                ORDER BY fecha_registro
                """
            )
            filas = cursor.fetchall()
        return Turno._filas_a_turnos(filas)

    @staticmethod
    def listar_por_medico(medico_legajo):
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT {Turno.CAMPOS_SELECT} FROM turnos WHERE medico_legajo = ? ORDER BY fecha_registro",
                (medico_legajo,),
            )
            filas = cursor.fetchall()
        return Turno._filas_a_turnos(filas)

    @staticmethod
    def listar_por_paciente(paciente_dni):
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT {Turno.CAMPOS_SELECT} FROM turnos WHERE paciente_dni = ? ORDER BY fecha_registro",
                (paciente_dni,),
            )
            filas = cursor.fetchall()
        return Turno._filas_a_turnos(filas)

    @staticmethod
    def listar_pendientes_de_exportar():
        """
        Devuelve las solicitudes que todavia no fueron enviadas al
        sistema principal (exportado = 0).
        """
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT {Turno.CAMPOS_SELECT} FROM turnos WHERE exportado = 0")
            filas = cursor.fetchall()
        return Turno._filas_a_turnos(filas)

    @staticmethod
    def contar_pendientes_de_exportar():
        """
        Cuenta cuantas solicitudes todavia no se enviaron al sistema principal.
        """
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM turnos WHERE exportado = 0")
            cantidad = cursor.fetchone()[0]
        return cantidad

    @staticmethod
    def marcar_todos_como_exportados():
        """
        Marca todas las solicitudes pendientes como ya enviadas al
        sistema principal. Se llama despues de generar la exportacion a CSV.
        """
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute("UPDATE turnos SET exportado = 1 WHERE exportado = 0")
            conexion.commit()

    @staticmethod
    def buscar_por_id(id_turno):
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"SELECT {Turno.CAMPOS_SELECT} FROM turnos WHERE id = ?",
                (id_turno,),
            )
            fila = cursor.fetchone()
        if fila is None:
            return None
        return Turno._filas_a_turnos([fila])[0]

    @staticmethod
    def resumen_por_paciente(paciente_dni):
        """
        Devuelve un resumen de las solicitudes de turno de un paciente:
        cantidad total y cantidad por cada estado.
        """
        turnos = Turno.listar_por_paciente(paciente_dni)
        resumen = {estado: 0 for estado in Turno.ESTADOS_VALIDOS}
        for turno in turnos:
            resumen[turno.estado] = resumen.get(turno.estado, 0) + 1
        resumen["total"] = len(turnos)
        return resumen, turnos

    @staticmethod
    def eliminar(id_turno):
        """
        Borra la solicitud de la base de datos local de Maxwell.
        Se usa al cancelar: como la solicitud nunca se envio al
        sistema principal, no tiene sentido conservarla ni contarla
        como pendiente de exportar.
        """
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM turnos WHERE id = ?", (id_turno,))
            conexion.commit()

    @staticmethod
    def eliminar_todos():
        """
        Borra TODAS las solicitudes de la base local, sin posibilidad
        de deshacerlo. Se usa al cerrar el uso diario de Maxwell,
        despues de exportar: las solicitudes son informacion transitoria
        de una jornada de emergencia, no un registro permanente.
        """
        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM turnos")
            conexion.commit()

    def cambiar_estado(self, nuevo_estado):
        """
        Cambia el estado de la solicitud (ej: cancelar antes de enviarla,
        o marcar atendida cuando el sistema principal informa que la
        consulta se realizo).
        """
        if nuevo_estado not in Turno.ESTADOS_VALIDOS:
            raise ValueError(f"Estado invalido: {nuevo_estado}")

        with conexion_segura() as conexion:
            cursor = conexion.cursor()
            cursor.execute("UPDATE turnos SET estado = ? WHERE id = ?", (nuevo_estado, self.id))
            conexion.commit()
        self.estado = nuevo_estado

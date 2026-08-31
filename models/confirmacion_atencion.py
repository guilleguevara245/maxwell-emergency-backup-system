"""
Maxwell Emergency Backup System - by Guillermo Guevara

Modelo de ConfirmacionAtencion: un registro libre para anotar que un
paciente fue atendido, usando el codigo de turno que le dio el sistema
principal (por ejemplo "0809899") junto con su DNI, y observaciones
opcionales para dejar cualquier aclaracion util a la hora de cargarlo
despues en el sistema principal. No se relaciona con la tabla de
solicitudes (Turno): el codigo lo asigna el sistema principal, que
Maxwell no conoce ni valida en formato.

Sirve como recordatorio de que hay confirmaciones pendientes de
cargar manualmente en el sistema principal cuando vuelva a estar
disponible.
"""

from database import obtener_conexion
from utils.validaciones import validar_dni


class ConfirmacionAtencion:
    CAMPOS_SELECT = "id, codigo_turno, paciente_dni, observaciones, exportado, fecha_registro"

    def __init__(self, codigo_turno, paciente_dni, observaciones=None, id=None, exportado=False, fecha_registro=None):
        self.id = id
        self.codigo_turno = codigo_turno
        self.paciente_dni = paciente_dni
        self.observaciones = observaciones
        self.exportado = bool(exportado)
        self.fecha_registro = fecha_registro

    def __str__(self):
        return f"[{self.id}] Codigo {self.codigo_turno} - Paciente DNI {self.paciente_dni}"

    def guardar(self):
        """
        Guarda la confirmacion. El codigo de turno es texto libre
        (no tiene formato fijo, lo asigna el sistema principal).
        El DNI del paciente solo se valida en FORMATO (que sea un DNI
        valido), no se exige que el paciente ya este registrado en
        Maxwell: puede tratarse de un paciente que el sistema
        principal ya conocia de antes.
        """
        if not self.codigo_turno or not self.codigo_turno.strip():
            raise ValueError("El codigo de turno es obligatorio.")

        validar_dni(self.paciente_dni)

        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO confirmaciones_atencion (codigo_turno, paciente_dni, observaciones) VALUES (?, ?, ?)",
                (self.codigo_turno, self.paciente_dni, self.observaciones),
            )
            conexion.commit()
            self.id = cursor.lastrowid
        finally:
            conexion.close()
        return self.id

    @staticmethod
    def _filas_a_confirmaciones(filas):
        return [ConfirmacionAtencion(id=f[0], codigo_turno=f[1], paciente_dni=f[2],
                                      observaciones=f[3], exportado=f[4], fecha_registro=f[5]) for f in filas]

    @staticmethod
    def listar_todas():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(f"SELECT {ConfirmacionAtencion.CAMPOS_SELECT} FROM confirmaciones_atencion")
        filas = cursor.fetchall()
        conexion.close()
        return ConfirmacionAtencion._filas_a_confirmaciones(filas)

    @staticmethod
    def listar_pendientes_de_exportar():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            f"SELECT {ConfirmacionAtencion.CAMPOS_SELECT} FROM confirmaciones_atencion WHERE exportado = 0"
        )
        filas = cursor.fetchall()
        conexion.close()
        return ConfirmacionAtencion._filas_a_confirmaciones(filas)

    @staticmethod
    def contar_pendientes_de_exportar():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM confirmaciones_atencion WHERE exportado = 0")
        cantidad = cursor.fetchone()[0]
        conexion.close()
        return cantidad

    @staticmethod
    def marcar_todas_como_exportadas():
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("UPDATE confirmaciones_atencion SET exportado = 1 WHERE exportado = 0")
        conexion.commit()
        conexion.close()

    @staticmethod
    def eliminar_todas():
        """
        Borra TODAS las confirmaciones de la base local, sin posibilidad
        de deshacerlo. Se usa al cerrar el uso diario de Maxwell,
        despues de exportar: son informacion transitoria de una
        jornada de emergencia, no un registro permanente.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM confirmaciones_atencion")
        conexion.commit()
        conexion.close()

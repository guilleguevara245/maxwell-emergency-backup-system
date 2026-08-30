"""
Maxwell Medic System - by Guillermo Guevara

Exportacion de datos a archivos CSV, pensada para poder sacar
un respaldo o migrar la informacion a otro sistema facilmente
(por ejemplo, abriendolo en Excel).
"""

import csv
import os
from datetime import datetime

from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno
from models.confirmacion_atencion import ConfirmacionAtencion

CARPETA_EXPORTACION = "exportado"


def _asegurar_carpeta():
    if not os.path.exists(CARPETA_EXPORTACION):
        os.makedirs(CARPETA_EXPORTACION)


def exportar_pacientes_csv(incluir_inactivos=True):
    """
    Exporta todos los pacientes a un archivo CSV.
    Devuelve la ruta del archivo generado.
    """
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_EXPORTACION, "pacientes.csv")
    pacientes = Paciente.listar_todos(incluir_inactivos=incluir_inactivos)

    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["dni", "nombre", "apellido", "telefono", "telefono_fijo",
                            "email", "activo", "fecha_registro"])
        for p in pacientes:
            escritor.writerow([p.dni, p.nombre, p.apellido, p.telefono,
                                p.telefono_fijo or "", p.email, p.activo, p.fecha_registro])

    return ruta


def exportar_medicos_csv(incluir_inactivos=True):
    """
    Exporta todos los medicos a un archivo CSV.
    Devuelve la ruta del archivo generado.
    """
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_EXPORTACION, "medicos.csv")
    medicos = Medico.listar_todos(incluir_inactivos=incluir_inactivos)

    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["legajo", "dni", "nombre", "apellido", "especialidad",
                            "telefono", "email", "activo", "fecha_registro"])
        for m in medicos:
            escritor.writerow([m.legajo, m.dni, m.nombre, m.apellido, m.especialidad,
                                m.telefono, m.email, m.activo, m.fecha_registro])

    return ruta


def exportar_turnos_csv():
    """
    Exporta todas las solicitudes de turno a un archivo CSV, recorriendo
    todos los pacientes (activos e inactivos) para no dejar ninguna
    afuera. Marca las solicitudes exportadas como enviadas al sistema
    principal, que es quien va a asignarles fecha y hora reales.
    Devuelve la ruta del archivo generado.
    """
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_EXPORTACION, "turnos.csv")

    turnos = []
    for paciente in Paciente.listar_todos(incluir_inactivos=True):
        turnos.extend(Turno.listar_por_paciente(paciente.dni))

    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["id", "paciente_dni", "especialidad", "medico_legajo",
                            "motivo", "observaciones", "estado", "fecha_registro"])
        for t in turnos:
            escritor.writerow([t.id, t.paciente_dni, t.especialidad, t.medico_legajo or "",
                                t.motivo, t.observaciones or "", t.estado, t.fecha_registro])

    Turno.marcar_todos_como_exportados()
    return ruta


def exportar_atenciones_csv():
    """
    Exporta las confirmaciones de atencion (codigo de turno del sistema
    principal + DNI del paciente) a un archivo CSV. Marca las
    confirmaciones exportadas como enviadas.
    Devuelve la ruta del archivo generado.
    """
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_EXPORTACION, "atenciones.csv")
    confirmaciones = ConfirmacionAtencion.listar_todas()

    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["id", "codigo_turno", "paciente_dni", "fecha_registro"])
        for c in confirmaciones:
            escritor.writerow([c.id, c.codigo_turno, c.paciente_dni, c.fecha_registro])

    ConfirmacionAtencion.marcar_todas_como_exportadas()
    return ruta


def exportar_todo_csv():
    """
    Exporta pacientes, medicos, solicitudes de turno y confirmaciones
    de atencion, cada uno a su propio CSV dentro de la carpeta
    "exportado/". Devuelve la lista de rutas generadas.
    """
    rutas = [
        exportar_pacientes_csv(),
        exportar_medicos_csv(),
        exportar_turnos_csv(),
        exportar_atenciones_csv(),
    ]
    return rutas

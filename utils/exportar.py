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
    Exporta todos los turnos a un archivo CSV, recorriendo todos los
    pacientes (activos e inactivos) para no dejar turnos afuera.
    Devuelve la ruta del archivo generado.
    """
    _asegurar_carpeta()
    ruta = os.path.join(CARPETA_EXPORTACION, "turnos.csv")

    turnos = []
    for paciente in Paciente.listar_todos(incluir_inactivos=True):
        turnos.extend(Turno.listar_por_paciente(paciente.dni))

    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["id", "paciente_dni", "medico_legajo", "fecha", "hora",
                            "estado", "motivo", "fecha_registro"])
        for t in turnos:
            escritor.writerow([t.id, t.paciente_dni, t.medico_legajo, t.fecha, t.hora,
                                t.estado, t.motivo, t.fecha_registro])

    return ruta


def exportar_todo_csv():
    """
    Exporta pacientes, medicos y turnos, cada uno a su propio CSV
    dentro de la carpeta "exportado/". Devuelve la lista de rutas generadas.
    """
    rutas = [
        exportar_pacientes_csv(),
        exportar_medicos_csv(),
        exportar_turnos_csv(),
    ]
    return rutas

"""
Maxwell Emergency Backup System - by Guillermo Guevara

Exportacion de datos a archivos PDF, pensada para poder sacar un
respaldo legible y facil de entender para pasarle la informacion al
sistema principal una vez que vuelva a estar disponible.

Cada exportacion completa crea su propia carpeta con fecha y hora
dentro de "exportado/", para no mezclar los respaldos de distintos
dias ni de distintos turnos del mismo dia (por ejemplo, turno tarde
y turno noche) si Maxwell se usa mas de una vez. Despues de generar
los PDF, se borran los pacientes, las solicitudes de turno y las
confirmaciones de atencion de la base local (los medicos NO se
borran: son el unico dato permanente de Maxwell), para que el
sistema quede listo para un nuevo uso sin arrastrar datos viejos.
"""

import os
import shutil
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno
from models.confirmacion_atencion import ConfirmacionAtencion

CARPETA_EXPORTACION = "exportado"
CARPETA_ASSETS = "assets"

COLOR_MARCA = colors.HexColor("#B02A2A")  # rojo Maxwell
ESTILOS = getSampleStyleSheet()


def _carpeta_de_hoy():
    """
    Devuelve (y crea si hace falta) la carpeta de exportacion del
    momento actual, por ejemplo "exportado/registro de datos
    30-08-2026 19-10". Incluye la hora ademas de la fecha para que
    dos exportaciones del mismo dia (por ejemplo, turno tarde y turno
    noche) queden en carpetas separadas en vez de pisarse entre si.
    """
    nombre_carpeta = datetime.now().strftime("registro de datos %d-%m-%Y %H-%M")
    ruta = os.path.join(CARPETA_EXPORTACION, nombre_carpeta)
    if not os.path.exists(ruta):
        os.makedirs(ruta)
    return ruta


def _ruta_asset(nombre_archivo):
    ruta = os.path.join(CARPETA_ASSETS, nombre_archivo)
    return ruta if os.path.exists(ruta) else None


def _estilo_tabla():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_MARCA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


def _armar_documento(ruta, elementos_extra_al_inicio, titulo, encabezados, filas):
    """
    Arma y guarda un PDF con una imagen o titulo al inicio, seguido
    de una tabla con encabezados y filas de datos.
    """
    documento = SimpleDocTemplate(ruta, pagesize=A4,
                                   leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                                   topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elementos = list(elementos_extra_al_inicio)
    elementos.append(Paragraph(titulo, ESTILOS["Heading2"]))
    elementos.append(Spacer(1, 12))

    if filas:
        datos = [encabezados] + filas
        tabla = Table(datos, repeatRows=1)
        tabla.setStyle(_estilo_tabla())
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("(sin registros)", ESTILOS["Normal"]))

    documento.build(elementos)


def exportar_pacientes_pdf(carpeta=None):
    """
    Exporta todos los pacientes (activos e inactivos) a un PDF.
    Devuelve la ruta del archivo generado.
    """
    carpeta = carpeta or _carpeta_de_hoy()
    ruta = os.path.join(carpeta, "pacientes.pdf")

    encabezados = ["DNI", "Nombre", "Apellido", "Telefono", "Tel. fijo", "Email", "Activo", "Registrado"]
    filas = []
    for p in Paciente.listar_todos(incluir_inactivos=True):
        filas.append([p.dni, p.nombre, p.apellido, p.telefono, p.telefono_fijo or "-",
                      p.email, "Si" if p.activo else "No", p.fecha_registro])

    elementos_iniciales = []
    ruta_header = _ruta_asset("header_pacientes.jpg")
    if ruta_header:
        elementos_iniciales.append(Image(ruta_header, width=10 * cm, height=8 * cm, kind="proportional"))
        elementos_iniciales.append(Spacer(1, 12))

    _armar_documento(ruta, elementos_iniciales, "Registro de pacientes", encabezados, filas)
    return ruta


def exportar_medicos_pdf(carpeta=None):
    """
    Exporta todos los medicos (activos e inactivos) a un PDF.
    Devuelve la ruta del archivo generado.
    """
    carpeta = carpeta or _carpeta_de_hoy()
    ruta = os.path.join(carpeta, "medicos.pdf")

    encabezados = ["Legajo", "DNI", "Nombre", "Apellido", "Especialidad", "Telefono", "Email", "Activo"]
    filas = []
    for m in Medico.listar_todos(incluir_inactivos=True):
        filas.append([m.legajo, m.dni, m.nombre, m.apellido, m.especialidad,
                      m.telefono, m.email, "Si" if m.activo else "No"])

    elementos_iniciales = []
    ruta_header = _ruta_asset("header_medicos.jpg")
    if ruta_header:
        elementos_iniciales.append(Image(ruta_header, width=10 * cm, height=8 * cm, kind="proportional"))
        elementos_iniciales.append(Spacer(1, 12))

    _armar_documento(ruta, elementos_iniciales, "Registro de medicos", encabezados, filas)
    return ruta


def exportar_turnos_pdf(carpeta=None):
    """
    Exporta todas las solicitudes de turno a un PDF, con la imagen de
    cabecera de "Turnos Pendientes".
    Devuelve la ruta del archivo generado.
    """
    carpeta = carpeta or _carpeta_de_hoy()
    ruta = os.path.join(carpeta, "turnos_pendientes.pdf")

    turnos = []
    for paciente in Paciente.listar_todos(incluir_inactivos=True):
        turnos.extend(Turno.listar_por_paciente(paciente.dni))

    encabezados = ["ID", "DNI Paciente", "Especialidad", "Medico (legajo)", "Motivo", "Observaciones", "Estado"]
    filas = []
    for t in turnos:
        filas.append([str(t.id), t.paciente_dni, t.especialidad, t.medico_legajo or "A asignar",
                      t.motivo, t.observaciones or "-", t.estado])

    elementos_iniciales = []
    ruta_header = _ruta_asset("header_turnos_pendientes.jpg")
    if ruta_header:
        elementos_iniciales.append(Image(ruta_header, width=10 * cm, height=8 * cm, kind="proportional"))
        elementos_iniciales.append(Spacer(1, 12))

    _armar_documento(ruta, elementos_iniciales, "Solicitudes de turno para asignar", encabezados, filas)
    return ruta


def exportar_atenciones_pdf(carpeta=None):
    """
    Exporta las confirmaciones de atencion a un PDF, con la imagen de
    cabecera de "Turnos Atendidos".
    Devuelve la ruta del archivo generado.
    """
    carpeta = carpeta or _carpeta_de_hoy()
    ruta = os.path.join(carpeta, "turnos_atendidos.pdf")

    encabezados = ["Codigo de turno", "DNI Paciente", "Observaciones", "Registrado"]
    filas = []
    for c in ConfirmacionAtencion.listar_todas():
        filas.append([c.codigo_turno, c.paciente_dni, c.observaciones or "-", c.fecha_registro])

    elementos_iniciales = []
    ruta_header = _ruta_asset("header_turnos_atendidos.jpg")
    if ruta_header:
        elementos_iniciales.append(Image(ruta_header, width=10 * cm, height=8 * cm, kind="proportional"))
        elementos_iniciales.append(Spacer(1, 12))

    _armar_documento(ruta, elementos_iniciales, "Turnos confirmados como atendidos", encabezados, filas)
    return ruta


def exportar_todo_pdf():
    """
    Exporta pacientes, medicos, solicitudes de turno y confirmaciones
    de atencion, cada uno a su propio PDF dentro de una carpeta con
    la fecha de hoy, para no mezclar respaldos de distintos dias.

    Despues de generar los 4 PDF, borra los pacientes, las solicitudes
    de turno y las confirmaciones de atencion de la base local (los
    medicos se conservan), dejando Maxwell listo para una nueva
    jornada de emergencia sin arrastrar datos del dia anterior.

    Devuelve la lista de rutas generadas.
    """
    carpeta = _carpeta_de_hoy()
    rutas = [
        exportar_pacientes_pdf(carpeta),
        exportar_medicos_pdf(carpeta),
        exportar_turnos_pdf(carpeta),
        exportar_atenciones_pdf(carpeta),
    ]

    Turno.eliminar_todos()
    Paciente.eliminar_todos()
    ConfirmacionAtencion.eliminar_todas()

    return rutas


def listar_carpetas_respaldo():
    """
    Devuelve la lista de carpetas de respaldo generadas hasta ahora
    dentro de "exportado/", ordenadas de la mas vieja a la mas nueva.
    """
    if not os.path.exists(CARPETA_EXPORTACION):
        return []
    carpetas = [
        nombre for nombre in os.listdir(CARPETA_EXPORTACION)
        if os.path.isdir(os.path.join(CARPETA_EXPORTACION, nombre))
    ]
    return sorted(carpetas)


def eliminar_carpeta_respaldo(nombre_carpeta):
    """
    Elimina una carpeta de respaldo especifica (con todos sus PDF
    adentro). Devuelve True si la borro, False si no existia.
    """
    ruta = os.path.join(CARPETA_EXPORTACION, nombre_carpeta)
    if not os.path.isdir(ruta):
        return False
    shutil.rmtree(ruta)
    return True


def eliminar_todas_las_carpetas_respaldo():
    """
    Elimina TODAS las carpetas de respaldo generadas hasta ahora.
    No afecta a la base de datos de Maxwell, solo a los PDF ya
    exportados en disco.
    """
    for nombre_carpeta in listar_carpetas_respaldo():
        eliminar_carpeta_respaldo(nombre_carpeta)

"""
Maxwell Medic System — by Guillermo Guevara

Funciones de validacion de formato, reutilizadas por los distintos
modelos antes de guardar datos en la base.
"""

import re
from datetime import datetime

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_dni(dni):
    """
    Un DNI valido tiene entre 7 y 8 digitos numericos (formato argentino).
    """
    if not dni or not dni.isdigit():
        raise ValueError("El DNI debe contener solo numeros.")
    if not (7 <= len(dni) <= 8):
        raise ValueError("El DNI debe tener 7 u 8 digitos.")


def validar_email(email):
    """
    Valida que el email tenga un formato basico valido (algo@algo.algo).
    """
    if not email or not PATRON_EMAIL.match(email):
        raise ValueError(f"El email '{email}' no tiene un formato valido.")


def validar_telefono(telefono):
    """
    Un celular argentino valido tiene 11 digitos en total
    (9 + codigo de area + numero). Permite guiones o espacios en la escritura.
    """
    if not telefono:
        raise ValueError("El telefono es obligatorio.")
    solo_numeros = re.sub(r"[^0-9]", "", telefono)
    if len(solo_numeros) < 11:
        raise ValueError("El telefono (celular) debe tener al menos 11 digitos.")


def validar_telefono_fijo(telefono_fijo):
    """
    Un telefono fijo argentino valido tiene 10 digitos en total
    (codigo de area + numero). Es opcional: si no se completa, no valida nada.
    """
    if not telefono_fijo:
        return
    solo_numeros = re.sub(r"[^0-9]", "", telefono_fijo)
    if len(solo_numeros) < 10:
        raise ValueError("El telefono fijo debe tener al menos 10 digitos.")


def validar_fecha(fecha):
    """
    Valida que la fecha tenga formato AAAA-MM-DD y sea una fecha real
    (por ejemplo, rechaza '2026-02-30'). Este es el formato interno
    que se guarda en la base de datos.
    """
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"La fecha '{fecha}' debe tener el formato AAAA-MM-DD y ser valida.")


def fecha_visual_a_iso(fecha_dm):
    """
    Convierte una fecha ingresada por el usuario en formato DD/MM/AAAA
    al formato interno AAAA-MM-DD que se guarda en la base de datos.
    Lanza ValueError si el formato o la fecha no son validos.
    """
    try:
        return datetime.strptime(fecha_dm, "%d/%m/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(f"La fecha '{fecha_dm}' debe tener el formato DD/MM/AAAA y ser valida.")


def fecha_iso_a_visual(fecha_iso):
    """
    Convierte una fecha guardada en formato AAAA-MM-DD al formato
    DD/MM/AAAA para mostrarla en pantalla.
    """
    try:
        return datetime.strptime(fecha_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return fecha_iso  # si algo viene mal formado, se muestra tal cual en vez de romper


def validar_hora(hora):
    """
    Valida que la hora tenga formato HH:MM (24 horas).
    """
    try:
        datetime.strptime(hora, "%H:%M")
    except (ValueError, TypeError):
        raise ValueError(f"La hora '{hora}' debe tener el formato HH:MM (24 horas).")

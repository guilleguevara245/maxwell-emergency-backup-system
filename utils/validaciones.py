"""
Maxwell Medic System - by Guillermo Guevara

Funciones de validacion de formato, reutilizadas por los distintos
modelos antes de guardar datos en la base.
"""

import re

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_legajo(legajo):
    """
    Un legajo valido no esta vacio y tiene entre 3 y 10 caracteres
    alfanumericos (permite numeros o codigos con letras, segun la
    institucion).
    """
    if not legajo or not legajo.strip():
        raise ValueError("El legajo es obligatorio.")
    if not legajo.isalnum():
        raise ValueError("El legajo debe contener solo letras y numeros.")
    if not (3 <= len(legajo) <= 10):
        raise ValueError("El legajo debe tener entre 3 y 10 caracteres.")


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
    Un celular argentino valido tiene al menos 10 digitos en total.
    Permite guiones o espacios en la escritura.
    """
    if not telefono:
        raise ValueError("El telefono es obligatorio.")
    solo_numeros = re.sub(r"[^0-9]", "", telefono)
    if len(solo_numeros) < 10:
        raise ValueError("El telefono (celular) debe tener al menos 10 digitos.")


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

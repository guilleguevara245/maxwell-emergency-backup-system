"""
Maxwell Emergency Backup System - by Guillermo Guevara

Punto de entrada del sistema. Menu de consola para gestionar
pacientes, medicos y solicitudes de turno.

Maxwell es un sistema de respaldo: cuando el sistema principal del
consultorio esta caido en horario laboral, permite registrar pacientes
y solicitudes de turno (paciente, especialidad, medico especifico si
se pidio, motivo y observaciones) para cargarlas despues en el sistema
principal, que es quien asigna la fecha y hora real.
"""

from database import crear_tablas
from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno
from models.confirmacion_atencion import ConfirmacionAtencion
from utils.exportar import (
    exportar_todo_pdf,
    listar_carpetas_respaldo,
    eliminar_carpeta_respaldo,
    eliminar_todas_las_carpetas_respaldo,
)

ANCHO_CAJA = 60


# ---------- INTERFAZ DE CONSOLA ----------

def _caja(secciones, ancho=ANCHO_CAJA):
    """
    Arma una caja de texto tipo panel de consola a partir de una lista
    de secciones (cada seccion es una lista de lineas), separando cada
    seccion de la siguiente con una linea divisoria.
    """
    borde_arriba = "\u2554" + "\u2550" * (ancho + 2) + "\u2557"
    borde_medio = "\u2560" + "\u2550" * (ancho + 2) + "\u2563"
    borde_abajo = "\u255a" + "\u2550" * (ancho + 2) + "\u255d"

    lineas = [borde_arriba]
    for indice, seccion in enumerate(secciones):
        if indice > 0:
            lineas.append(borde_medio)
        for linea in seccion:
            lineas.append("\u2551 " + linea.ljust(ancho) + " \u2551")
    lineas.append(borde_abajo)
    return "\n".join(lineas)


def mostrar_menu(titulo, opciones, texto_volver="Volver", avisos=None, ancho=ANCHO_CAJA):
    """
    Imprime un menu con el estilo de panel de Maxwell: titulo centrado,
    opciones numeradas [01], [02]... y la opcion de volver/salir
    marcada como [00], separada del resto.
    """
    if avisos:
        for aviso in avisos:
            print(f"[!] {aviso}")

    seccion_titulo = [titulo.center(ancho)]

    seccion_opciones = [""]
    for numero, texto in enumerate(opciones, start=1):
        seccion_opciones.append(f"[{numero}] {texto}")
    seccion_opciones.append("")

    seccion_volver = [f"[0] \u2190 {texto_volver}"]

    print("\n" + _caja([seccion_titulo, seccion_opciones, seccion_volver], ancho))


def elegir_opcion(prompt="Seleccionar"):
    return input(f"\n{prompt} > ").strip()


def ok(mensaje):
    print(f"[\u2713] {mensaje}")


def err(mensaje):
    print(f"[x] {mensaje}")


def esperar_tecla(mensaje="Presiona una tecla para continuar..."):
    """
    Pausa la ejecucion hasta que el usuario presione una tecla.
    Intenta una lectura de tecla unica (sin necesidad de Enter) tanto
    en Windows como en sistemas tipo Unix con terminal interactiva; si
    no hay una terminal disponible (por ejemplo, al correr Maxwell
    empaquetado o de forma no interactiva), cae de vuelta a esperar un
    Enter para no romper la ejecucion.
    """
    print(f"\n{mensaje}")
    try:
        import msvcrt
        msvcrt.getch()
        return
    except ImportError:
        pass

    try:
        import sys
        import termios
        import tty

        descriptor = sys.stdin.fileno()
        configuracion_previa = termios.tcgetattr(descriptor)
        try:
            tty.setraw(descriptor)
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(descriptor, termios.TCSADRAIN, configuracion_previa)
        return
    except Exception:
        try:
            input()
        except EOFError:
            pass


def pausar():
    esperar_tecla("Presiona una tecla para continuar...")


def despedida():
    print("\n" + _caja([["Shutting down Maxwell. Maximum backup. Well saved.".center(ANCHO_CAJA)]]))
    esperar_tecla("Presiona una tecla para salir...")


# ---------- MENU DE PACIENTES ----------

def menu_pacientes():
    while True:
        mostrar_menu("GESTION DE PACIENTES", [
            "Dar de alta un paciente",
            "Listar pacientes",
            "Actualizar un paciente",
        ], texto_volver="Volver al menu principal")
        opcion = elegir_opcion()

        if opcion == "1":
            dni = input("DNI: ").strip()
            nombre = input("Nombre: ").strip()
            apellido = input("Apellido: ").strip()
            telefono = input("Telefono (celular): ").strip()
            telefono_fijo = input("Telefono fijo (opcional): ").strip() or None
            email = input("Email: ").strip()
            try:
                paciente = Paciente(nombre, apellido, dni, telefono, email, telefono_fijo)
                paciente.guardar()
                ok(f"Paciente creado con exito: {paciente}")
            except Exception as error:
                err(f"No se pudo crear el paciente: {error}")
            pausar()

        elif opcion == "2":
            pacientes = Paciente.listar_todos()
            if not pacientes:
                print("No hay pacientes activos registrados todavia.")
            for p in pacientes:
                print(p)
            pausar()

        elif opcion == "3":
            dni = input("DNI del paciente a actualizar: ").strip()
            paciente = Paciente.buscar_por_dni(dni)
            if paciente is None:
                err("No existe un paciente con ese DNI.")
            else:
                print(f"Datos actuales: {paciente}")
                paciente.nombre = input(f"Nuevo nombre [{paciente.nombre}]: ").strip() or paciente.nombre
                paciente.apellido = input(f"Nuevo apellido [{paciente.apellido}]: ").strip() or paciente.apellido
                paciente.telefono = input(f"Nuevo telefono [{paciente.telefono}]: ").strip() or paciente.telefono
                paciente.telefono_fijo = input(f"Nuevo telefono fijo [{paciente.telefono_fijo}]: ").strip() or paciente.telefono_fijo
                try:
                    paciente.actualizar()
                    ok("Paciente actualizado.")
                except Exception as error:
                    err(f"No se pudo actualizar: {error}")
            pausar()

        elif opcion == "0":
            break
        else:
            err("Opcion invalida.")


# ---------- MENU DE MEDICOS ----------

def menu_medicos():
    while True:
        mostrar_menu("GESTION DE MEDICOS", [
            "Dar de alta un medico",
            "Listar medicos",
            "Buscar medicos por especialidad",
            "Desactivar un medico",
        ], texto_volver="Volver al menu principal")
        opcion = elegir_opcion()

        if opcion == "1":
            legajo = input("Legajo: ").strip()
            dni = input("DNI: ").strip()
            nombre = input("Nombre: ").strip()
            apellido = input("Apellido: ").strip()
            especialidad = input("Especialidad: ").strip()
            telefono = input("Telefono (celular): ").strip()
            email = input("Email: ").strip()
            try:
                medico = Medico(legajo, dni, nombre, apellido, especialidad, telefono, email)
                medico.guardar()
                ok(f"Medico creado con exito: {medico}")
            except Exception as error:
                err(f"No se pudo crear el medico: {error}")
            pausar()

        elif opcion == "2":
            medicos = Medico.listar_todos()
            if not medicos:
                print("No hay medicos activos registrados todavia.")
            for m in medicos:
                print(m)
            pausar()

        elif opcion == "3":
            especialidad = input("Especialidad a buscar: ").strip()
            medicos = Medico.listar_por_especialidad(especialidad)
            if not medicos:
                print("No se encontraron medicos con esa especialidad.")
            for m in medicos:
                print(m)
            pausar()

        elif opcion == "4":
            legajo = input("Legajo del medico a desactivar: ").strip()
            Medico.eliminar(legajo)
            ok("Medico desactivado (el historial de turnos se conserva).")
            pausar()

        elif opcion == "0":
            break
        else:
            err("Opcion invalida.")


# ---------- MENU DE TURNOS (solicitudes) ----------

def menu_turnos():
    while True:
        mostrar_menu("SOLICITUDES DE TURNO", [
            "Registrar una solicitud de turno",
            "Listar solicitudes por paciente",
            "Cancelar una solicitud",
            "Registrar turno atendido (codigo del sistema principal + DNI)",
        ], texto_volver="Volver al menu principal")
        opcion = elegir_opcion()

        if opcion == "1":
            paciente_dni = input("DNI del paciente: ").strip()
            especialidad = input("Especialidad: ").strip()
            quiere_medico_especifico = input("Pide un medico especifico? (si/no): ").strip().lower()

            medico_legajo = None
            if quiere_medico_especifico == "si":
                medicos = Medico.listar_por_especialidad(especialidad)
                if not medicos:
                    print(f"No hay medicos activos de la especialidad '{especialidad}'. Se sigue sin medico especifico.")
                else:
                    print("\nMedicos disponibles de esa especialidad:")
                    for m in medicos:
                        print(f"  Legajo {m.legajo} - Dr/a. {m.nombre} {m.apellido}")
                    medico_legajo = input("Legajo del medico elegido: ").strip()

            motivo = input("Motivo de consulta: ").strip()
            observaciones = input("Observaciones (opcional): ").strip() or None

            try:
                turno = Turno(paciente_dni, especialidad, motivo,
                              medico_legajo=medico_legajo, observaciones=observaciones)
                turno.guardar()
                ok(f"Solicitud registrada con exito: {turno}")
            except ValueError as error:
                err(f"No se pudo registrar la solicitud: {error}")
            pausar()

        elif opcion == "2":
            paciente_dni = input("DNI del paciente: ").strip()
            turnos = Turno.listar_por_paciente(paciente_dni)
            if not turnos:
                print("No hay solicitudes para ese paciente.")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "3":
            solicitudes_hoy = Turno.listar_de_hoy()
            if not solicitudes_hoy:
                print("No hay solicitudes registradas hoy.")
                pausar()
                continue

            print("\nSolicitudes de hoy:")
            for indice, turno in enumerate(solicitudes_hoy, start=1):
                paciente = Paciente.buscar_por_dni(turno.paciente_dni)
                nombre_paciente = f"{paciente.nombre} {paciente.apellido}" if paciente else "(paciente no encontrado)"
                print(f"  {indice}. DNI {turno.paciente_dni} - {nombre_paciente} - "
                      f"{turno.especialidad} - {turno.motivo}")

            seleccion = input("Numero de la solicitud a cancelar (o Enter para cancelar la operacion): ").strip()
            if not seleccion:
                print("Operacion cancelada.")
            elif not seleccion.isdigit() or not (1 <= int(seleccion) <= len(solicitudes_hoy)):
                err("Numero invalido.")
            else:
                turno_elegido = solicitudes_hoy[int(seleccion) - 1]
                Turno.eliminar(turno_elegido.id)
                ok("Solicitud cancelada y eliminada del sistema local.")
            pausar()

        elif opcion == "4":
            codigo_turno = input("Codigo de turno (segun el sistema principal): ").strip()
            paciente_dni = input("DNI del paciente: ").strip()
            observaciones = input("Observaciones (opcional): ").strip() or None
            try:
                confirmacion = ConfirmacionAtencion(codigo_turno, paciente_dni, observaciones)
                confirmacion.guardar()
                ok(f"Confirmacion registrada: {confirmacion}")
            except ValueError as error:
                err(f"No se pudo registrar la confirmacion: {error}")
            pausar()

        elif opcion == "0":
            break
        else:
            err("Opcion invalida.")


# ---------- MENU DE RESPALDOS EXPORTADOS ----------

def menu_respaldos():
    while True:
        mostrar_menu("RESPALDOS EXPORTADOS", [
            "Listar carpetas de respaldo",
            "Eliminar una carpeta especifica",
            "Eliminar todas las carpetas de respaldo",
        ], texto_volver="Volver al menu principal")
        opcion = elegir_opcion()

        if opcion == "1":
            carpetas = listar_carpetas_respaldo()
            if not carpetas:
                print("No hay carpetas de respaldo generadas todavia.")
            else:
                print("\nCarpetas de respaldo:")
                for indice, nombre in enumerate(carpetas, start=1):
                    print(f"  {indice}. {nombre}")
            pausar()

        elif opcion == "2":
            carpetas = listar_carpetas_respaldo()
            if not carpetas:
                print("No hay carpetas de respaldo generadas todavia.")
                pausar()
                continue

            print("\nCarpetas de respaldo:")
            for indice, nombre in enumerate(carpetas, start=1):
                print(f"  {indice}. {nombre}")

            seleccion = input("Numero de la carpeta a eliminar (o Enter para cancelar): ").strip()
            if not seleccion:
                print("Operacion cancelada.")
            elif not seleccion.isdigit() or not (1 <= int(seleccion) <= len(carpetas)):
                err("Numero invalido.")
            else:
                nombre_elegido = carpetas[int(seleccion) - 1]
                confirmacion = input(f"Confirmar eliminacion de '{nombre_elegido}'? (si/no): ").strip().lower()
                if confirmacion == "si":
                    eliminar_carpeta_respaldo(nombre_elegido)
                    ok("Carpeta eliminada.")
                else:
                    print("Operacion cancelada.")
            pausar()

        elif opcion == "3":
            carpetas = listar_carpetas_respaldo()
            if not carpetas:
                print("No hay carpetas de respaldo generadas todavia.")
                pausar()
                continue

            confirmacion = input(f"Esto va a eliminar las {len(carpetas)} carpetas de respaldo. Confirmar? (si/no): ").strip().lower()
            if confirmacion == "si":
                eliminar_todas_las_carpetas_respaldo()
                ok("Todas las carpetas de respaldo fueron eliminadas.")
            else:
                print("Operacion cancelada.")
            pausar()

        elif opcion == "0":
            break
        else:
            err("Opcion invalida.")


# ---------- MENU PRINCIPAL ----------

def menu_principal():
    crear_tablas()
    while True:
        pendientes_turnos = Turno.contar_pendientes_de_exportar()
        pendientes_atenciones = ConfirmacionAtencion.contar_pendientes_de_exportar()

        avisos = []
        if pendientes_turnos > 0:
            avisos.append(f"Tenes {pendientes_turnos} solicitud(es) de turno pendiente(s) por asignar al sistema principal.")
        if pendientes_atenciones > 0:
            avisos.append(f"Tenes {pendientes_atenciones} turno(s) atendido(s) pendiente(s) por cargar en el sistema principal.")

        mostrar_menu("MAXWELL EMERGENCY BACKUP SYSTEM", [
            "Gestion de Pacientes",
            "Gestion de Medicos",
            "Gestion de Solicitudes de Turno",
            "Exportar datos a PDF (respaldo)",
            "Gestion de Respaldos Exportados",
        ], texto_volver="Salir", avisos=avisos)
        opcion = elegir_opcion()

        if opcion == "1":
            menu_pacientes()
        elif opcion == "2":
            menu_medicos()
        elif opcion == "3":
            menu_turnos()
        elif opcion == "4":
            print("\nEsto va a exportar los datos a PDF y despues BORRAR pacientes,")
            print("solicitudes de turno y confirmaciones de atencion de Maxwell")
            print("(los medicos se conservan).")
            confirmacion = input("Confirmar? (si/no): ").strip().lower()
            if confirmacion == "si":
                try:
                    rutas = exportar_todo_pdf()
                    print("\nDatos exportados con exito:")
                    for ruta in rutas:
                        print(f"  - {ruta}")
                    ok("Pacientes, solicitudes y confirmaciones borrados de Maxwell.")
                except Exception as error:
                    err(f"No se pudo completar la exportacion: {error}")
                    print("No se borro ningun dato local.")
            else:
                print("Exportacion cancelada.")
            pausar()
        elif opcion == "5":
            menu_respaldos()
        elif opcion == "0":
            despedida()
            break
        else:
            err("Opcion invalida.")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print()
        despedida()

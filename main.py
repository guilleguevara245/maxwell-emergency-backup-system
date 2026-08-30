"""
Maxwell Medic System - by Guillermo Guevara

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
from utils.exportar import exportar_todo_pdf


def pausar():
    input("\nPresiona Enter para continuar...")


# ---------- MENU DE PACIENTES ----------

def menu_pacientes():
    while True:
        print("\n--- Gestion de Pacientes ---")
        print("1. Dar de alta un paciente")
        print("2. Listar pacientes")
        print("3. Actualizar un paciente")
        print("4. Desactivar un paciente")
        print("5. Volver al menu principal")
        opcion = input("Elegi una opcion: ").strip()

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
                print(f"Paciente creado con exito: {paciente}")
            except Exception as error:
                print(f"No se pudo crear el paciente: {error}")
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
                print("No existe un paciente con ese DNI.")
            else:
                print(f"Datos actuales: {paciente}")
                paciente.nombre = input(f"Nuevo nombre [{paciente.nombre}]: ").strip() or paciente.nombre
                paciente.apellido = input(f"Nuevo apellido [{paciente.apellido}]: ").strip() or paciente.apellido
                paciente.telefono = input(f"Nuevo telefono [{paciente.telefono}]: ").strip() or paciente.telefono
                paciente.telefono_fijo = input(f"Nuevo telefono fijo [{paciente.telefono_fijo}]: ").strip() or paciente.telefono_fijo
                try:
                    paciente.actualizar()
                    print("Paciente actualizado.")
                except Exception as error:
                    print(f"No se pudo actualizar: {error}")
            pausar()

        elif opcion == "4":
            dni = input("DNI del paciente a desactivar: ").strip()
            Paciente.eliminar(dni)
            print("Paciente desactivado (el historial de turnos se conserva).")
            pausar()

        elif opcion == "5":
            break
        else:
            print("Opcion invalida.")


# ---------- MENU DE MEDICOS ----------

def menu_medicos():
    while True:
        print("\n--- Gestion de Medicos ---")
        print("1. Dar de alta un medico")
        print("2. Listar medicos")
        print("3. Buscar medicos por especialidad")
        print("4. Desactivar un medico")
        print("5. Volver al menu principal")
        opcion = input("Elegi una opcion: ").strip()

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
                print(f"Medico creado con exito: {medico}")
            except Exception as error:
                print(f"No se pudo crear el medico: {error}")
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
            print("Medico desactivado (el historial de turnos se conserva).")
            pausar()

        elif opcion == "5":
            break
        else:
            print("Opcion invalida.")


# ---------- MENU DE TURNOS (solicitudes) ----------

def menu_turnos():
    while True:
        print("\n--- Gestion de Solicitudes de Turno ---")
        print("1. Registrar una solicitud de turno")
        print("2. Listar solicitudes por medico")
        print("3. Listar solicitudes por paciente")
        print("4. Ver historial de un paciente (con resumen)")
        print("5. Cancelar una solicitud")
        print("6. Registrar turno atendido (codigo del sistema principal + DNI)")
        print("7. Volver al menu principal")
        opcion = input("Elegi una opcion: ").strip()

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
                print(f"Solicitud registrada con exito: {turno}")
            except ValueError as error:
                print(f"No se pudo registrar la solicitud: {error}")
            pausar()

        elif opcion == "2":
            medico_legajo = input("Legajo del medico: ").strip()
            turnos = Turno.listar_por_medico(medico_legajo)
            if not turnos:
                print("No hay solicitudes para ese medico.")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "3":
            paciente_dni = input("DNI del paciente: ").strip()
            turnos = Turno.listar_por_paciente(paciente_dni)
            if not turnos:
                print("No hay solicitudes para ese paciente.")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "4":
            paciente_dni = input("DNI del paciente: ").strip()
            resumen, turnos = Turno.resumen_por_paciente(paciente_dni)
            print(f"\nHistorial del paciente DNI {paciente_dni}")
            print(f"Total de solicitudes: {resumen['total']}")
            print(f"  Atendidas:   {resumen['atendido']}")
            print(f"  Pendientes:  {resumen['pendiente']}")
            print(f"  Confirmadas: {resumen['confirmado']}")
            print(f"  Canceladas:  {resumen['cancelado']}")
            print("\nDetalle:")
            if not turnos:
                print("(sin solicitudes registradas)")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "5":
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
                print("Numero invalido.")
            else:
                turno_elegido = solicitudes_hoy[int(seleccion) - 1]
                Turno.eliminar(turno_elegido.id)
                print("Solicitud cancelada y eliminada del sistema local.")
            pausar()

        elif opcion == "6":
            codigo_turno = input("Codigo de turno (segun el sistema principal): ").strip()
            paciente_dni = input("DNI del paciente: ").strip()
            try:
                confirmacion = ConfirmacionAtencion(codigo_turno, paciente_dni)
                confirmacion.guardar()
                print(f"Confirmacion registrada: {confirmacion}")
            except ValueError as error:
                print(f"No se pudo registrar la confirmacion: {error}")
            pausar()

        elif opcion == "7":
            break
        else:
            print("Opcion invalida.")


# ---------- MENU PRINCIPAL ----------

def menu_principal():
    crear_tablas()
    while True:
        pendientes_turnos = Turno.contar_pendientes_de_exportar()
        pendientes_atenciones = ConfirmacionAtencion.contar_pendientes_de_exportar()
        print("\n===== Maxwell Medic System =====")
        if pendientes_turnos > 0:
            print(f"AVISO: tenes {pendientes_turnos} solicitud(es) de turno pendiente(s) por asignar al sistema principal.")
        if pendientes_atenciones > 0:
            print(f"AVISO: tenes {pendientes_atenciones} turno(s) atendido(s) pendiente(s) por cargar en el sistema principal.")
        print("1. Gestion de Pacientes")
        print("2. Gestion de Medicos")
        print("3. Gestion de Solicitudes de Turno")
        print("4. Exportar datos a PDF (respaldo)")
        print("5. Salir")
        opcion = input("Elegi una opcion: ").strip()

        if opcion == "1":
            menu_pacientes()
        elif opcion == "2":
            menu_medicos()
        elif opcion == "3":
            menu_turnos()
        elif opcion == "4":
            rutas = exportar_todo_pdf()
            print("\nDatos exportados con exito:")
            for ruta in rutas:
                print(f"  - {ruta}")
            pausar()
        elif opcion == "5":
            print("Hasta luego!")
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido. Hasta luego!")

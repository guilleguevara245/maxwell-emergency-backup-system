"""
Maxwell Medic System - by Guillermo Guevara

Punto de entrada del sistema. Menu de consola para gestionar
pacientes, medicos y turnos.
"""

from database import crear_tablas
from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno
from utils.validaciones import fecha_visual_a_iso


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


# ---------- MENU DE TURNOS ----------

def menu_turnos():
    while True:
        print("\n--- Gestion de Turnos ---")
        print("1. Sacar un turno")
        print("2. Listar turnos por fecha")
        print("3. Listar turnos por medico")
        print("4. Listar turnos por paciente")
        print("5. Ver historial de un paciente (con resumen)")
        print("6. Cancelar un turno")
        print("7. Marcar un turno como atendido")
        print("8. Marcar un turno como ausente")
        print("9. Volver al menu principal")
        opcion = input("Elegi una opcion: ").strip()

        if opcion == "1":
            paciente_dni = input("DNI del paciente: ").strip()
            medico_legajo = input("Legajo del medico: ").strip()
            fecha_visual = input("Fecha (DD/MM/AAAA): ").strip()
            hora = input("Hora (HH:MM): ").strip()
            motivo = input("Motivo de consulta: ").strip()
            try:
                fecha_iso = fecha_visual_a_iso(fecha_visual)
                turno = Turno(paciente_dni, medico_legajo, fecha_iso, hora, motivo=motivo)
                turno.guardar()
                print(f"Turno creado con exito: {turno}")
            except ValueError as error:
                print(f"No se pudo crear el turno: {error}")
            pausar()

        elif opcion == "2":
            fecha_visual = input("Fecha a consultar (DD/MM/AAAA): ").strip()
            try:
                fecha_iso = fecha_visual_a_iso(fecha_visual)
                turnos = Turno.listar_por_fecha(fecha_iso)
                if not turnos:
                    print("No hay turnos para esa fecha.")
                for t in turnos:
                    print(t)
            except ValueError as error:
                print(f"Fecha invalida: {error}")
            pausar()

        elif opcion == "3":
            medico_legajo = input("Legajo del medico: ").strip()
            turnos = Turno.listar_por_medico(medico_legajo)
            if not turnos:
                print("No hay turnos para ese medico.")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "4":
            paciente_dni = input("DNI del paciente: ").strip()
            turnos = Turno.listar_por_paciente(paciente_dni)
            if not turnos:
                print("No hay turnos para ese paciente.")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "5":
            paciente_dni = input("DNI del paciente: ").strip()
            resumen, turnos = Turno.resumen_por_paciente(paciente_dni)
            print(f"\nHistorial del paciente DNI {paciente_dni}")
            print(f"Total de turnos: {resumen['total']}")
            print(f"  Atendidos:  {resumen['atendido']}")
            print(f"  Pendientes: {resumen['pendiente']}")
            print(f"  Confirmados: {resumen['confirmado']}")
            print(f"  Cancelados: {resumen['cancelado']}")
            print(f"  Ausentes:   {resumen['ausente']}")
            print("\nDetalle:")
            if not turnos:
                print("(sin turnos registrados)")
            for t in turnos:
                print(t)
            pausar()

        elif opcion == "6":
            id_turno = input("ID del turno a cancelar: ").strip()
            turno = Turno.buscar_por_id(id_turno)
            if turno is None:
                print("No existe un turno con ese ID.")
            else:
                turno.cambiar_estado("cancelado")
                print("Turno cancelado.")
            pausar()

        elif opcion == "7":
            id_turno = input("ID del turno a marcar como atendido: ").strip()
            turno = Turno.buscar_por_id(id_turno)
            if turno is None:
                print("No existe un turno con ese ID.")
            else:
                turno.cambiar_estado("atendido")
                print("Turno marcado como atendido.")
            pausar()

        elif opcion == "8":
            id_turno = input("ID del turno a marcar como ausente: ").strip()
            turno = Turno.buscar_por_id(id_turno)
            if turno is None:
                print("No existe un turno con ese ID.")
            else:
                turno.cambiar_estado("ausente")
                print("Turno marcado como ausente.")
            pausar()

        elif opcion == "9":
            break
        else:
            print("Opcion invalida.")


# ---------- MENU PRINCIPAL ----------

def menu_principal():
    crear_tablas()
    while True:
        print("\n===== Maxwell Medic System =====")
        print("1. Gestion de Pacientes")
        print("2. Gestion de Medicos")
        print("3. Gestion de Turnos")
        print("4. Salir")
        opcion = input("Elegi una opcion: ").strip()

        if opcion == "1":
            menu_pacientes()
        elif opcion == "2":
            menu_medicos()
        elif opcion == "3":
            menu_turnos()
        elif opcion == "4":
            print("Hasta luego!")
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    menu_principal()

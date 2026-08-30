<p align="center">
  <img src="assets/logo_maxwell.jpg" alt="Maxwell Medic System" width="320">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/tests-80%20passing-brightgreen" alt="80 tests passing">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT License">
</p>

# Maxwell Medic System

Sistema de respaldo para consultorios médicos pequeños, desarrollado en Python con persistencia en SQLite.

**by Guillermo Guevara**

## Descripción

Maxwell Medic System está pensado para un escenario puntual: el sistema principal de un consultorio se cae en horario laboral y hay pacientes esperando. En vez de perder esa información, Maxwell permite registrar pacientes, médicos y solicitudes de turno de forma local, sin conexión a ningún servidor externo, para cargar todo en el sistema principal apenas vuelva a estar disponible.

Por diseño, las solicitudes de turno **no llevan fecha ni hora**: eso lo asigna el sistema principal, que es quien conoce la agenda real. Maxwell solo captura los datos necesarios para no perder tiempo ni información mientras tanto.

## Funcionalidades

- Alta, baja (lógica) y modificación de pacientes, identificados por DNI
- Alta, baja (lógica) y modificación de médicos, identificados por legajo (que funciona también como matrícula profesional)
- Registro de solicitudes de turno: paciente, especialidad, médico específico si se pidió (con listado de médicos disponibles de esa especialidad), motivo y observaciones
- Búsqueda de médicos por especialidad, sin distinguir mayúsculas de minúsculas
- Cancelación de solicitudes del día mediante un listado numerado (sin necesidad de conocer IDs internos)
- Registro de confirmaciones de atención: código de turno del sistema principal + DNI del paciente, para anotar que alguien fue atendido y cargarlo después
- Historial de turnos por paciente, con resumen por estado
- Avisos en el menú principal de cuántas solicitudes y confirmaciones siguen pendientes de pasar al sistema principal
- Exportación de todos los datos a PDF (pacientes, médicos, solicitudes de turno y confirmaciones de atención), como respaldo legible
- Validaciones de formato en todos los datos sensibles (DNI, email, teléfono, legajo)
- Suite de 80 tests automáticos cubriendo toda la lógica de negocio

## Tecnologías

- **Python 3** (sin frameworks)
- **SQLite** para persistencia de datos
- **reportlab** para la generación de los PDF de respaldo
- **unittest** para los tests automáticos

## Estructura del proyecto

```
maxwell-medic-system/
├── main.py                        # Punto de entrada / menu principal
├── database.py                    # Conexion y creacion de tablas
├── models/
│   ├── paciente.py
│   ├── medico.py
│   ├── turno.py                   # Solicitudes de turno (sin fecha/hora)
│   └── confirmacion_atencion.py   # Registro de codigo + DNI de turnos atendidos
├── utils/
│   ├── validaciones.py            # Validaciones de formato reutilizables
│   └── exportar.py                # Exportacion a PDF
├── tests/                         # 80 tests automaticos (unittest)
├── assets/                        # Logo e imagenes de cabecera de los PDF
├── README.md
├── requirements.txt
└── LICENSE
```

## Cómo ejecutarlo

```bash
git clone https://github.com/guilleguevara245/maxwell-medic-system.git
cd maxwell-medic-system
pip install -r requirements.txt
python main.py
```

## Cómo correr los tests

```bash
python -m unittest discover -s tests -v
```

## Autor

**Guillermo Guevara**
Estudiante de la Tecnicatura Universitaria en Programación y la Licenciatura en Informática — Universidad Nacional de Hurlingham.

## Licencia

Este proyecto está bajo la licencia MIT — ver el archivo [LICENSE](LICENSE) para más detalles.

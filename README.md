# Maxwell Medic System

Sistema de gestión de turnos para consultorios médicos, desarrollado en Python con persistencia en SQLite.

**by Guillermo Guevara**

## 📋 Descripción

Maxwell Medic System permite administrar pacientes, médicos y turnos de un consultorio de forma simple y ordenada, evitando solapamientos de horarios y facilitando el seguimiento de las consultas.

## ✨ Funcionalidades

- Alta, baja y modificación de pacientes
- Alta, baja y modificación de médicos (con su especialidad)
- Asignación de turnos, validando disponibilidad horaria del médico
- Listado de turnos por fecha, por médico o por paciente
- Cancelación y reprogramación de turnos
- Marcado de turnos como atendidos
- Reportes básicos (turnos del día, cancelaciones, médico con más turnos del mes)

## 🛠️ Tecnologías

- **Python 3**
- **SQLite** (persistencia de datos)

## 📁 Estructura del proyecto

```
maxwell-medic-system/
├── main.py              # Punto de entrada / menú principal
├── database.py          # Conexión y creación de tablas
├── models/
│   ├── paciente.py
│   ├── medico.py
│   └── turno.py
├── services/
│   └── turno_service.py # Lógica de negocio y validaciones
├── README.md
└── requirements.txt
```

## 🚀 Cómo ejecutarlo

```bash
git clone https://github.com/<tu-usuario>/maxwell-medic-system.git
cd maxwell-medic-system
python main.py
```

## 👤 Autor

**Guillermo Guevara**
Estudiante de la Tecnicatura Universitaria en Programación y la Licenciatura en Informática — Universidad Nacional de Hurlingham.


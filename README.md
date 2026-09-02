<p align="center">
  <img src="assets/logo_maxwell.jpg" alt="Maxwell Emergency Backup System" width="800">
</p>

<p align="center">
  <img src="https://github.com/guilleguevara245/maxwell-emergency-backup-system/actions/workflows/tests.yml/badge.svg" alt="Estado de los tests">
  <img src="coverage.svg" alt="Cobertura de tests">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/tests-98%20passing-brightgreen" alt="98 tests passing">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT License">
  <img src="https://img.shields.io/badge/status-stable-success" alt="Stable">
</p>

# Maxwell Emergency Backup System

Sistema de contingencia para consultorios médicos pequeños, desarrollado en Python con persistencia local en SQLite.

## Descripción

Maxwell Emergency Backup System resuelve un problema operativo concreto: cuando el sistema de gestión principal de un consultorio deja de funcionar en horario de atención, el personal administrativo pierde la capacidad de registrar pacientes y turnos, y esa información termina anotada en papel o, peor, se pierde directamente.

Esta aplicación está pensada para usarse en Argentina, y nace de una situación que vi repetirse muchas veces en consultorios y centros de salud del país: caídas de sistema, cortes de conexión o servidores que se cuelgan justo en el momento de más movimiento, dejando a la recepción sin forma de anotar nada de manera ordenada. De más joven vi este problema de cerca varias veces, con recepcionistas anotando datos en hojas sueltas, post-its o cuadernos que después había que descifrar y cargar a mano, con el riesgo constante de perder información o de cargarla mal. De esa experiencia surgió la idea de Maxwell: no reemplazar al sistema principal, sino darle al consultorio una red de contención simple para esos momentos, que cualquiera pueda usar sin capacitación previa.

Por eso, además de resolver el problema técnico, Maxwell se diseñó pensando en la facilidad de uso: un menú de texto simple, sin curva de aprendizaje, pensado para que lo pueda operar sin problemas incluso el personal administrativo menos acostumbrado a la tecnología, que en un momento de tensión (el sistema caído, pacientes esperando) necesita algo directo y sin fricción, no una herramienta más para aprender.

Maxwell funciona como una capa de contingencia local, sin dependencias de red ni de servicios externos: corre enteramente en la computadora del consultorio y no requiere conexión a internet una vez instalado. Permite registrar pacientes, mantener un padrón de médicos y capturar solicitudes de turno mientras el sistema principal está fuera de servicio, para después exportar todo en un formato claro y volcarlo al sistema principal apenas se restablezca.

Una decisión de diseño central es que las solicitudes de turno **no incluyen fecha ni hora**: esa asignación depende de la disponibilidad real del sistema principal, que Maxwell no conoce. En cambio, Maxwell captura los datos que sí puede validar en el momento — identidad del paciente, especialidad requerida, médico específico si corresponde, y motivo de consulta — dejando la planificación temporal para quien tiene la agenda completa.

Del mismo modo, cada uso de Maxwell se trata como un evento aislado: al exportar los datos del día, el sistema genera los respaldos correspondientes y luego limpia su propio estado transitorio (pacientes, solicitudes y confirmaciones), conservando únicamente el padrón de médicos, que es información estable de la institución. Esto evita que los datos de distintas jornadas de contingencia se mezclen entre sí.

## Funcionalidades

- Alta y modificación de pacientes, identificados por DNI
- Alta, baja lógica y modificación de médicos, identificados por legajo (que funciona también como matrícula profesional)
- Registro de solicitudes de turno: paciente, especialidad, médico específico si se pidió (con listado de médicos disponibles de esa especialidad), motivo y observaciones
- Búsqueda de médicos por especialidad, sin distinguir mayúsculas de minúsculas
- Cancelación de solicitudes del día mediante un listado numerado, sin necesidad de conocer identificadores internos
- Registro de confirmaciones de atención: código de turno del sistema principal, DNI del paciente y observaciones opcionales, para dejar asentado que alguien fue atendido y cargarlo después
- Avisos en el menú principal indicando cuántas solicitudes y confirmaciones siguen pendientes de trasladar al sistema principal
- Exportación de todos los datos a PDF con identidad visual propia, organizados en una carpeta con la fecha del día
- Limpieza automática del estado transitorio después de cada exportación, preservando el padrón de médicos
- Validaciones de formato en todos los datos sensibles (DNI, email, teléfono, legajo)
- Suite de 98 tests automáticos cubriendo la totalidad de la lógica de negocio

## Tecnologías

- **Python 3**, sin frameworks
- **SQLite** para persistencia local de datos
- **reportlab** para la generación de los PDF de respaldo
- **unittest** para la suite de tests automáticos

## Estructura del proyecto

```
maxwell-emergency-backup-system/
├── main.py                        # Punto de entrada / menu principal
├── database.py                    # Conexion y creacion de tablas
├── models/
│   ├── paciente.py
│   ├── medico.py
│   ├── turno.py                   # Solicitudes de turno (sin fecha/hora)
│   └── confirmacion_atencion.py   # Registro de codigo + DNI de turnos atendidos
├── utils/
│   ├── validaciones.py            # Validaciones de formato reutilizables
│   └── exportar.py                # Exportacion a PDF y limpieza post-exportacion
├── tests/                         # 98 tests automaticos (unittest)
├── assets/                        # Logo e imagenes de cabecera de los PDF
├── README.md
├── requirements.txt
└── LICENSE
```

## Instalación

```bash
git clone https://github.com/guilleguevara245/maxwell-emergency-backup-system.git
cd maxwell-emergency-backup-system
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

El sistema crea automáticamente la base de datos local en el primer uso. Al exportar los datos desde el menú principal, se genera una carpeta con la fecha del día dentro de `exportado/`, conteniendo los cuatro PDF de respaldo (pacientes, médicos, solicitudes de turno y confirmaciones de atención). Tras confirmar la exportación, Maxwell borra su estado transitorio (pacientes, solicitudes y confirmaciones), dejando únicamente el padrón de médicos para el siguiente uso.

## Tests

```bash
python -m unittest discover -s tests -v
```

La suite cubre la totalidad de los modelos y las validaciones de negocio: creación y borrado de entidades, restricciones de formato, prevención de duplicados, el ciclo completo de exportación y limpieza de datos, y el manejo de errores de la base de datos (archivo corrupto, escrituras concurrentes desde más de una instancia). Un workflow de GitHub Actions corre automáticamente toda la suite en Python 3.10, 3.11 y 3.12 en cada `push` y `pull request` a `main`.

## Ejecutable para Windows

Para un consultorio sin Python instalado, Maxwell se puede compilar a un `.exe` autocontenido con [Nuitka](https://nuitka.net/):

1. Hacer doble clic en `build_exe.bat`.
2. Esperar a que termine. La primera vez tarda varios minutos (puede ser 5 o más, según la PC), porque instala Nuitka y descarga el compilador que necesita para generar el ejecutable.
3. Cuando la ventana muestra `Presiona una tecla para continuar...`, ya terminó: el ejecutable quedó en `dist\Maxwell.exe`, con la carpeta `assets/` y el ícono de Maxwell ya incluidos adentro.

Para compartir Maxwell con un consultorio alcanza con copiarles la carpeta `dist` completa (o directamente el archivo `Maxwell.exe` de adentro): no hace falta instalar nada más, ni Python ni ninguna otra dependencia.

Se usa Nuitka en lugar de PyInstaller porque compila a un binario nativo (en vez de empaquetar el intérprete de Python), lo que da mejor rendimiento y muchos menos falsos positivos de antivirus.

## Estado del proyecto y versión estable

El proyecto se encuentra en un estado funcional completo: todas las funcionalidades descritas están implementadas, probadas y en uso. La rama `main` refleja en todo momento la última versión estable.

## Autor

**Guillermo Guevara**
Estudiante de la Tecnicatura Universitaria en Programación y la Licenciatura en Informática — Universidad Nacional de Hurlingham.

## Licencia

Este proyecto está bajo la licencia MIT — ver el archivo [LICENSE](LICENSE) para más detalles.

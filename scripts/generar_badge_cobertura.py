"""
Maxwell Emergency Backup System - by Guillermo Guevara

Genera coverage.svg a partir del reporte JSON de coverage.py, sin
depender del paquete "coverage-badge" (que quedo sin mantenimiento y
se rompe con versiones nuevas de setuptools, que ya no incluyen
pkg_resources).

Uso (despues de correr "coverage run" y "coverage json"):
    python scripts/generar_badge_cobertura.py
"""

import json
import os

RUTA_REPORTE_JSON = "coverage.json"
RUTA_BADGE_SVG = "coverage.svg"


def _color_segun_porcentaje(porcentaje):
    if porcentaje >= 90:
        return "#4c1"       # verde
    if porcentaje >= 80:
        return "#97ca00"    # verde-amarillo
    if porcentaje >= 60:
        return "#dfb317"    # amarillo
    if porcentaje >= 40:
        return "#fe7d37"    # naranja
    return "#e05d44"        # rojo


def _generar_svg(porcentaje):
    color = _color_segun_porcentaje(porcentaje)
    texto_porcentaje = f"{porcentaje:.0f}%"
    ancho_texto = 6 * len(texto_porcentaje) + 20
    ancho_total = 61 + ancho_texto

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{ancho_total}" height="20" role="img" aria-label="coverage: {texto_porcentaje}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{ancho_total}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="61" height="20" fill="#555"/>
    <rect x="61" width="{ancho_texto}" height="20" fill="{color}"/>
    <rect width="{ancho_total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="315" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="510">coverage</text>
    <text x="315" y="140" transform="scale(.1)" fill="#fff" textLength="510">coverage</text>
    <text aria-hidden="true" x="{610 + ancho_texto * 5}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{ancho_texto * 10 - 100}">{texto_porcentaje}</text>
    <text x="{610 + ancho_texto * 5}" y="140" transform="scale(.1)" fill="#fff" textLength="{ancho_texto * 10 - 100}">{texto_porcentaje}</text>
  </g>
</svg>
'''


def main():
    with open(RUTA_REPORTE_JSON, encoding="utf-8") as archivo:
        datos = json.load(archivo)

    porcentaje = datos["totals"]["percent_covered"]
    svg = _generar_svg(porcentaje)

    with open(RUTA_BADGE_SVG, "w", encoding="utf-8") as archivo:
        archivo.write(svg)

    print(f"Badge generado en {os.path.abspath(RUTA_BADGE_SVG)}: {porcentaje:.1f}% de cobertura.")


if __name__ == "__main__":
    main()

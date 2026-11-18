# Sistema de Gestión Financiera Personal

Proyecto final de Lenguajes de Programación (UTP, 2026-II). El mismo sistema se implementa con
el mismo dataset en tres paradigmas y debe producir los mismos resultados:

| Lenguaje | Paradigma | Programa |
|---|---|---|
| Scala 3 | Funcional | `scala/src/main/scala/Finanzas.scala` |
| Prolog (SWI-Prolog) | Lógico | `prolog/finanzas.pl` |
| Python 3 | Multiparadigma (objetos, funcional, imperativo) | `python/finanzas.py` |

Las reglas, los parámetros y los resultados esperados están en
[`datos/especificacion-sistema.md`](datos/especificacion-sistema.md), que es la fuente de verdad.

## Estructura

```
datos/      movimientos.csv (Scala y Python), datos.pl (Prolog; los mismos 80 movimientos) y la especificación
python/     finanzas.py
scala/      build.sbt y src/main/scala/Finanzas.scala
prolog/     finanzas.pl
tests/      verificar.py (compara con la especificación) y metricas.py (cuenta líneas de código)
docs/       metricas.md (generado por tests/metricas.py)
```

## Requisitos

- **Python 3.** Sin dependencias externas.
- **Scala:** JDK y [sbt](https://www.scala-sbt.org/). Scala 3 la descarga sbt según `scala/build.sbt`.
- **Prolog:** [SWI-Prolog](https://www.swi-prolog.org/) (`swipl`).

## Cómo ejecutar cada programa

Los tres programas abren un menú por consola: opciones `1` a `6` para F1–F6 y `0` para salir.

| Lenguaje | Carpeta desde la que se ejecuta | Comando |
|---|---|---|
| Python | cualquiera | `python3 python/finanzas.py` (ajusta la ruta si estás en otra carpeta) |
| Prolog | cualquiera | `swipl prolog/finanzas.pl` (ajusta la ruta si estás en otra carpeta) |
| Scala | **`scala/`**, obligatoriamente | `sbt run` |

```bash
python3 python/finanzas.py
```

```bash
swipl prolog/finanzas.pl
```

```bash
cd scala && sbt run
```

**Scala solo funciona desde `scala/`.** Lee `"../datos/movimientos.csv"`, una ruta relativa al
directorio de trabajo, y `sbt` usa `scala/` como directorio de trabajo. Ejecutar `sbt` desde la
raíz falla con "Neither build.sbt nor a 'project' directory". Python y Prolog calculan la ruta
de los datos a partir de la ubicación del propio programa, así que funcionan desde cualquier carpeta.

## Verificación

`tests/verificar.py` ejecuta cada programa por su menú y compara F1–F6 con las tablas de la
sección 5 de la especificación: igualdad exacta en F1, F2 y F3, y tolerancia de ±0.01 soles en F4, F5 y F6.

```bash
python3 tests/verificar.py
```

También se puede indicar qué lenguajes verificar: `python3 tests/verificar.py python prolog`.
Si falta `swipl` o `sbt` en el PATH, ese lenguaje se marca `[OMITIDO]` y el script termina con
código 2, para no dar por bueno algo que no se ejecutó. Código 1 significa que hay diferencias.

## Métricas

`docs/metricas.md` contiene las líneas de código por funcionalidad y por lenguaje (sin
comentarios, sin líneas en blanco y sin pruebas, según la sección 7 de la especificación).
Para regenerarlo:

```bash
python3 tests/metricas.py
```

## Decisiones de diseño que conviene conocer

- Montos en céntimos enteros y fechas como dos enteros (mes, día). Solo se redondea al imprimir.
- En Python, `Movimiento` es la clase base de `Gasto` e `Ingreso`; `cargar()` devuelve una sola
  lista de `Movimiento` y las funciones F1–F6 la reciben como parámetro.
- `movimientos.csv` es la fuente de datos de Scala y Python; `datos.pl` contiene los mismos
  datos como hechos de Prolog.

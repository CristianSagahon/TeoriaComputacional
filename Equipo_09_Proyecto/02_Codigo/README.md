# Network Graph Analyzer

Proyecto 4 de Teoría Computacional: analizador de redes mediante grafos. **Equipo 9.**

## Integrantes

- Jared Alejandro Galarza Limón
- Cristian Adair Sagahon Arredondo
- David Torres Alemendarez

## Descripción

Programa de terminal que carga una red ficticia (routers, switches, PCs y servidores) desde un archivo de texto, la representa como un grafo no dirigido y permite:

- Ver la red como lista de adyacencia y el grado de cada dispositivo.
- Consultar si dos dispositivos están conectados.
- Encontrar la ruta más corta (en saltos) entre dos dispositivos.
- Detectar dispositivos aislados.
- Saber si un equipo tuvo una falla según su registro de pings, usando un AFN y un AFD.
- Conocer el estado actual de cada equipo con el ciclo de estados Activo → Sobrecargado → Falla → Recuperación.
- Ejecutar consultas anidadas validadas con una gramática y un autómata de pila.

## Requisitos

- Python 3.10 o superior (probado con Python 3.12).
- No necesita instalar bibliotecas externas.

## Lenguaje utilizado

Python 3, solo biblioteca estándar (`re`, `collections`).

## Instrucciones de ejecución

Desde la carpeta `02_Codigo`:

```bash
python main.py
```

Aparece el menú:

```text
===== NETWORK GRAPH ANALYZER =====
1. Cargar red desde archivo
2. Mostrar red (lista de adyacencia y grados)
3. Consultar conectividad entre dos dispositivos
4. Buscar ruta más corta
5. Detectar dispositivos aislados
6. Cargar archivo de eventos (pings)
7. Analizar registro de pings (AFN, AFD y ciclo de estados)
8. Ejecutar consulta (gramática y autómata de pila)
0. Salir
```

Para empezar con los datos de ejemplo: elegir la opción 1 y presionar Enter (carga `datos/red_ejemplo.txt`), luego la opción 6 y Enter (carga `datos/eventos_ejemplo.txt`). Las opciones 2 a 5 necesitan una red cargada; la consulta `falla(X)` de la opción 8 necesita el archivo de eventos.

## Estructura del proyecto

Código (esta carpeta):

```text
02_Codigo/
├── main.py            menú e integración de todas las partes
├── grafo.py           carga de la red, BFS, conectividad, ruta más corta, aislados
├── expresiones.py     expresiones regulares ER1, ER2 y ER3
├── automatas.py       archivo de eventos, AFN, AFD y ciclo de estados
├── gramatica.py       tokens, gramática, autómata de pila y evaluación de consultas
├── datos/
│   ├── red_ejemplo.txt       red del laboratorio (11 dispositivos, 10 enlaces)
│   └── eventos_ejemplo.txt   registros de pings de 5 equipos
└── README.md
```

Qué archivo usa a cuál: `main.py` usa los otros cuatro; `gramatica.py` usa `grafo.py` y `automatas.py`; todos usan `expresiones.py`.

Resto de la entrega:

```text
Equipo_09_Proyecto/
├── 01_Documentacion/   reporte final (Proyecto_Final.pdf y su fuente .md)
├── 02_Codigo/          (esta carpeta)
├── 03_Automatas/       AFN.png, AFD.png, AP.png, Ciclo_estados.png (y sus .svg editables)
├── 04_Grafos/          Grafo.png (y Grafo.svg)
├── 05_Pruebas/         15 casos de prueba (casos_prueba.md y test_sistema.py)
├── 06_Presentacion/    presentación
└── 07_Evidencias/      Bitacora.md y capturas
```

## Formato de los archivos de entrada

Red (`datos/red_ejemplo.txt`): un enlace por línea, `Dispositivo,Dispositivo`. Una línea con un solo dispositivo lo registra sin enlaces. Las líneas que empiezan con `#` son comentarios.

```text
Router1,Switch1
Switch1,PC1
PC4
```

Eventos (`datos/eventos_ejemplo.txt`): `Dispositivo:eventos`, donde cada ping es `pr` (respondió) o `pt` (timeout).

```text
Server1:ptptpr
```

## Pruebas automáticas

Las pruebas están en la carpeta `05_Pruebas` (fuera de `02_Codigo`). Se ejecutan desde esa carpeta:

```bash
cd 05_Pruebas
python -m unittest -v
```

Los **15 casos de prueba** del sistema están en `test_sistema.py` y su tabla en `casos_prueba.md`:

```bash
python -m unittest -v test_sistema
```

`python -m unittest -v` ejecuta además las pruebas de apoyo de cada modelo. Para uno solo: `python -m unittest -v test_grafo`.

| Archivo | Qué prueba |
|---|---|
| `test_grafo.py` | Carga de la red, conectividad, rutas, aislados y grados |
| `test_expresiones.py` | Ejemplos válidos e inválidos de ER1, ER2 y ER3 |
| `test_automatas.py` | AFN, AFD, que reconozcan el mismo lenguaje y el ciclo de estados |
| `test_gramatica.py` | Tokens, autómata de pila y evaluación de consultas |
| `test_sistema.py` | Los 15 casos de prueba del programa completo, usando el menú |

`python test_sistema.py --tabla` genera la tabla de resultados de `casos_prueba.md`.

## Ejemplos de uso

Salidas reales del programa con los archivos de ejemplo.

Ruta más corta (opción 4):

```text
Dispositivo origen: Server1
Dispositivo destino: PC3
Ruta más corta: Server1 -> Switch2 -> Router2 -> Switch3 -> PC3
Saltos: 4
```

Dispositivos aislados (opción 5):

```text
Dispositivos aislados (grado 0): PC4
```

Análisis de un registro de pings con el AFN, el AFD y el ciclo de estados (opción 7):

```text
Escriba un registro de pings (ej. prptpt) o un dispositivo con registro cargado (ej. Server1): ptprpt
Recorrido AFN: {q0} -p-> {q1, q2} -t-> {q0, q3} -p-> {q1, q2, q4} -r-> {q0} -p-> {q1, q2} -t-> {q0, q3}
Resultado AFN: RECHAZA
Recorrido AFD: A -p-> B -t-> C -p-> D -r-> A -p-> B -t-> C
Resultado AFD: RECHAZA
El AFN y el AFD coinciden.
Falla registrada: NO (nunca hubo dos timeouts seguidos)
Ciclo de estados: ACTIVO -pt-> SOBRECARGADO -pr-> ACTIVO -pt-> SOBRECARGADO
Estado actual del dispositivo: SOBRECARGADO
```

Estado de cada equipo al cargar los eventos de ejemplo (opción 6):

```text
  Dispositivo Registro       Estado actual  Falla registrada
  PC1         prprpr         ACTIVO         no
  PC2         prptpr         ACTIVO         no
  PC3         prpt           SOBRECARGADO   no
  Server1     ptptpr         RECUPERACIÓN   sí
  Server2     prptpt         FALLA          sí
```

Consultas (opción 8):

```text
Consulta: y(conectado(PC1,Server1),no(falla(Server1)))
Resultado: FALSO

Consulta: ruta(PC1,Server2)
Resultado: PC1 -> Switch1 -> Router1 -> Router2 -> Switch3 -> Server2

Consulta: no(ruta(PC1,PC2))
Error: Token 3: se esperaba una consulta de sí/no (conectado, falla, no, y, o) y llegó 'ruta'.
```

Palabras de consulta disponibles: `ruta(A,B)`, `aislados()`, `conectado(A,B)`, `falla(A)`, `no(...)`, `y(...,...)`, `o(...,...)`. Se pueden anidar sin límite.

Error en un archivo de red (opción 1 con `05_Pruebas/datos_prueba/red_con_errores.txt`):

```text
No se cargó el archivo. Se encontraron estos problemas:
  - Línea 2: formato inválido 'router1,Switch2'. Se espera Dispositivo,Dispositivo o un solo Dispositivo (ejemplo: Router1,Switch1).
  - Línea 3: 'PC1,PC1' conecta un dispositivo consigo mismo.
  - Línea 4: formato inválido 'Switch1;PC2'. Se espera Dispositivo,Dispositivo o un solo Dispositivo (ejemplo: Router1,Switch1).
  - Línea 5: formato inválido 'Laptop1'. Se espera Dispositivo,Dispositivo o un solo Dispositivo (ejemplo: Router1,Switch1).
```

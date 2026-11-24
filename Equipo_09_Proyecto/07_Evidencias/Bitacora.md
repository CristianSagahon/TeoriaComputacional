# Bitácora del proyecto

Proyecto 4: Network Graph Analyzer. Equipo 9: Jared Alejandro Galarza Limón, Cristian Adair Sagahon Arredondo y David Torres Alemendarez.


## Registro


| Fecha | Actividad | Responsable(s) | Resultado |
|---|---|---|---|
| 11/11/2026 | Propuesta general, decisiones de diseño D1 a D11, reparto de tareas y estructura de carpetas (borrador con IA) | ***Los tres integrantes*** | Se realizo el reparto de actividades y organización del equipo. |
| 12/11/2026 | Etapa 1: definición del problema |***Los tres integrantes*** |Entendimiento del problema, alcance y lenguaje de programación a utlizar. |
| 13/11/2026 | Etapa 2: modelado con grafos. Red de ejemplo del laboratorio (11 dispositivos, 10 enlaces), vértices, aristas, tipo de grafo y lista de adyacencia | ***David*** | Red de ejemplo en `datos/red_ejemplo.txt`, tabla de adyacencia y grados; dibujo `Grafo.png` |
| 14/11/2026 | Etapa 2: programación de `grafo.py` (carga de la red, BFS, conectividad, ruta más corta, aislados y grados) | ***David*** | Funciones de grafos terminadas. Problema: la ruta más corta cambiaba entre ejecuciones; se resolvió recorriendo los vecinos en orden alfabético |
| 14/11/2026 | Revisión de la carga de la red: enlaces repetidos, enlaces escritos al revés y lazos (`PC1,PC1`) | ***David y Jared*** | Los vecinos se guardan en conjuntos y los lazos se rechazan en el código con su mensaje de error |
| 14/11/2026 | Etapa 3: alfabeto {p, r, t}, lenguaje L (dos timeouts seguidos) y 10 cadenas válidas y 10 inválidas | ***Jared y Cristian*** | Lenguaje L definido; las 20 cadenas se comprobaron con un programa |
| 15/11/2026 | Etapa 4: expresiones regulares ER1, ER2 y ER3, `expresiones.py` y carga del archivo de eventos | ***Jared*** | Expresiones terminadas. Problema: con `re.match` se aceptaban nombres como `PC1a`; se cambió a `re.fullmatch` y se prohibió el cero inicial |
| 15/11/2026 | Etapa 5: diseño y simulación del AFN | ***Jared*** | `AFN.png` y simulación por conjuntos de estados. Problema: el símbolo ∅ causaba `UnicodeEncodeError` en la terminal de Windows; se cambió por `{}` |
| 16/11/2026 | Etapa 6: conversión AFN → AFD por el método de subconjuntos | ***Jared y David*** | Tabla de 9 estados y `AFD.png`. David revisó cada casilla de la tabla contra el AFN; el AFN y el AFD coincidieron en todas las cadenas de longitud 0 a 10 |
| 16/11/2026 | Etapa 7: gramática de las consultas, tokenizador y derivaciones por la izquierda | ***Cristian*** | Gramática G con 8 producciones y 5 derivaciones comprobadas |
| 17/11/2026 | Etapa 7: separación de las variables S y B, cadenas no generables y demostración de que el lenguaje no es regular (lema de bombeo) | ***Cristian y Jared*** | `no(ruta(...))` ya no se puede generar; demostración terminada |
| 17/11/2026 | Etapa 8: diseño del autómata de pila y trazas de la pila | ***Cristian*** | `AP.png` y validación de consultas. Se eligió la producción mirando el token actual para dar mensajes con el número de token |
| 18/11/2026 | Etapa 8: evaluación de las consultas con el grafo y el AFD | ***Cristian y David*** | Consultas anidadas funcionando. Problema: `RecursionError` con 1000 niveles de anidamiento; se atrapa y se muestra un mensaje |
| 18/11/2026 | Etapa 9: `main.py`, menú de 8 opciones e integración de los módulos | ***Los tres integrantes*** | Programa completo. Problemas corregidos: codificación UTF-8, aviso al conservar los datos cargados, registro mal formado mostrado como ACTIVO y el mensaje "1 enlaces" (función `plural()`) |
| 19/11/2026 | Ciclo de estados Activo → Sobrecargado → Falla → Recuperación en `automatas.py` y opciones 6 y 7 del menú, diagrama `Ciclo_estados.png` | ***Jared y Cristian*** | Los cuatro estados aparecen con los datos de ejemplo (PC3 se cambió a `prpt`). Se acordó que `falla(X)` sigue usando el AFD; se comprobó que el ciclo pasa por FALLA si y solo si el AFD acepta |
| 19/11/2026 | Etapa 10: diseño de los 15 casos de prueba del sistema (P01 a P15) | ***David y Cristian*** | `test_sistema.py` y `casos_prueba.md`; 15 de 15 pasaron |
| 20/11/2026 | Etapas 11 y 12: revisión del código, docstrings, README y bitácora | ***Cristian y Jared*** | Docstrings en todas las funciones y README con instrucciones de ejecución y ejemplos |
| 20/11/2026 | Reporte final (casos de prueba, problemas por integrante, conclusiones y referencias), presentación y organización de las carpetas de entrega `Equipo_09_Proyecto` | ***Los tres integrantes*** | `Proyecto_Final.pdf`, `Presentacion.pptx` y `Presentacion.pdf` terminados; ZIP de entrega armado |

## Organización del equipo

| Integrante | Responsabilidad principal |
|---|---|
| David | Definición del problema, red de ejemplo, modelado con grafos y algoritmos (Etapas 1 y 2), esqueleto del menú y coordinación de los casos de prueba |
| Jared | Lenguaje formal, expresiones regulares, AFN, conversión a AFD y ciclo de estados (Etapas 3 a 6), revisión de consistencia de la documentación |
| Cristian | Gramática, lenguaje libre de contexto y autómata de pila (Etapas 7 y 8), integración de consultas y README |
| Los tres | Integración, pruebas del sistema, documentación final, bitácora, presentación y defensa |

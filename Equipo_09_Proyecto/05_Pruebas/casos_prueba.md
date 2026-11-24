# Casos de prueba del sistema completo

Proyecto 4: Network Graph Analyzer. Equipo 9: Jared Alejandro Galarza Limón, Cristian Adair Sagahon Arredondo y David Torres Alemendarez.

Son **15 casos de prueba**. Cada uno ejecuta `02_Codigo/main.py` como lo haría un usuario: se le mandan las opciones y los datos que escribiría en el teclado y se revisa lo que muestra el programa después de la última acción. Los casos están programados en `test_sistema.py`.

- **Entrada:** lo que se escribe en orden, separado por `→`. `''` es presionar Enter sin escribir nada (carga el archivo de ejemplo).
- **Resultado obtenido:** lo que mostró el programa de verdad. La tabla se generó con `python test_sistema.py --tabla` el 21/11/2026. En las salidas largas solo aparecen las líneas importantes.
- **Estado:** "Pasó" si el resultado obtenido contiene todo el resultado esperado.

Para ejecutar los casos o volver a generar la tabla:

```bash
cd 05_Pruebas
python -m unittest -v test_sistema
python test_sistema.py --tabla
```

## Resumen

| Tipo | Casos | Pasaron |
|---|---|---|
| Entradas válidas / casos normales | P01 a P06 | 6 de 6 |
| Entradas inválidas | P07 a P10 | 4 de 4 |
| Casos límite | P11 a P13 | 3 de 3 |
| Entradas inesperadas | P14 y P15 | 2 de 2 |
| **Total** | **15** | **15 de 15** |

Los casos P04, P05 y P12 revisan el ciclo de estados Activo → Sobrecargado → Falla → Recuperación.

## Tabla de casos

| ID | Tipo | Caso | Entrada | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| P01 | Válida / normal | Cargar la red de ejemplo | `1 → ''` | Red cargada: 11 dispositivos y 10 enlaces. | Red cargada: 11 dispositivos y 10 enlaces. | Pasó |
| P02 | Válida / normal | Ruta más corta Server1 a PC3 (hay un ciclo en la red) | `1 → '' → 4 → Server1 → PC3` | Server1 -> Switch2 -> Router2 -> Switch3 -> PC3<br>Saltos: 4 | Ruta más corta: Server1 -> Switch2 -> Router2 -> Switch3 -> PC3<br>Saltos: 4 | Pasó |
| P03 | Válida / normal | Conectividad con un equipo aislado (PC1 y PC4) | `1 → '' → 3 → PC1 → PC4` | No: no existe ningún camino entre PC1 y PC4. | No: no existe ningún camino entre PC1 y PC4. | Pasó |
| P04 | Válida / normal | Cargar pings: estado actual de cada equipo en el ciclo | `6 → ''` | PC1         prprpr         ACTIVO<br>PC3         prpt           SOBRECARGADO<br>Server1     ptptpr         RECUPERACIÓN<br>Server2     prptpt         FALLA | PC1         prprpr         ACTIVO         no<br>PC3         prpt           SOBRECARGADO   no<br>Server1     ptptpr         RECUPERACIÓN   sí<br>Server2     prptpt         FALLA          sí | Pasó |
| P05 | Válida / normal | Ciclo completo Activo → Sobrecargado → Falla → Recuperación → Activo | `7 → prptptprpr` | Resultado AFN: ACEPTA<br>Resultado AFD: ACEPTA<br>Ciclo de estados: ACTIVO -pr-> ACTIVO -pt-> SOBRECARGADO -pt-> FALLA -pr-> RECUPERACIÓN -pr-> ACTIVO<br>Estado actual del dispositivo: ACTIVO | Resultado AFN: ACEPTA<br>Resultado AFD: ACEPTA<br>Ciclo de estados: ACTIVO -pr-> ACTIVO -pt-> SOBRECARGADO -pt-> FALLA -pr-> RECUPERACIÓN -pr-> ACTIVO<br>Estado actual del dispositivo: ACTIVO | Pasó |
| P06 | Válida / normal | Consulta anidada y(conectado(PC1,Server1),no(falla(Server1))) | `1 → '' → 6 → '' → 8 → y(conectado(PC1,Server1),no(falla(Server1))) → n` | Resultado: FALSO | Resultado: FALSO | Pasó |
| P07 | Inválida | Nombre de dispositivo mal escrito (PC01) | `1 → '' → 4 → PC01` | Error: 'PC01' no es un nombre válido. | Error: 'PC01' no es un nombre válido. Use Router, Switch, PC o Server seguido de un número sin ceros al inicio (ejemplo: PC1). | Pasó |
| P08 | Inválida | Archivo de red con 4 líneas incorrectas | `1 → ../05_Pruebas/datos_prueba/red_con_errores.txt` | Línea 2:<br>Línea 3: 'PC1,PC1' conecta un dispositivo consigo mismo.<br>Línea 4:<br>Línea 5: | - Línea 2: formato inválido 'router1,Switch2'. Se espera Dispositivo,Dispositivo o un solo Dispositivo (ejemplo: Router1,Switch1).<br>- Línea 3: 'PC1,PC1' conecta un dispositivo consigo mismo.<br>- Línea 4: formato inválido 'Switch1;PC2'. Se espera Dispositivo,Dispositivo o un solo Dispositivo (ejemplo: Router1,Switch1).<br>- Línea 5: formato inválido 'Laptop1'. Se espera Dispositivo,Dispositivo o un solo Dispositivo (ejemplo: Router1,Switch1). | Pasó |
| P09 | Inválida | Consulta con un paréntesis sin cerrar | `1 → '' → 8 → y(conectado(PC1,Server1),no(falla(Server1)) → n` | Error: La consulta termina antes de tiempo: falta ')'. | Error: La consulta termina antes de tiempo: falta ')'. | Pasó |
| P10 | Inválida | Consulta que niega una ruta: no(ruta(PC1,PC2)) | `1 → '' → 8 → no(ruta(PC1,PC2)) → n` | se esperaba una consulta de sí/no<br>llegó 'ruta' | Error: Token 3: se esperaba una consulta de sí/no (conectado, falla, no, y, o) y llegó 'ruta'. | Pasó |
| P11 | Límite | Archivo de red vacío | `1 → ../05_Pruebas/datos_prueba/red_vacia.txt` | El archivo no tiene ningún dispositivo. | No se cargó el archivo. Se encontraron estos problemas:<br>- El archivo no tiene ningún dispositivo. | Pasó |
| P12 | Límite | Un solo timeout seguido de respuesta: ptpr (no llega a falla) | `7 → ptpr` | Resultado AFD: RECHAZA<br>Ciclo de estados: ACTIVO -pt-> SOBRECARGADO -pr-> ACTIVO<br>Estado actual del dispositivo: ACTIVO | Resultado AFD: RECHAZA<br>Ciclo de estados: ACTIVO -pt-> SOBRECARGADO -pr-> ACTIVO<br>Estado actual del dispositivo: ACTIVO | Pasó |
| P13 | Límite | Consulta con 1000 niveles de anidamiento | `1 → '' → 6 → '' → 8 → no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no(no...` | La consulta es válida, pero tiene demasiados niveles de anidamiento | Error: La consulta es válida, pero tiene demasiados niveles de anidamiento para evaluarla (el límite es de alrededor de 990 niveles). | Pasó |
| P14 | Inesperada | Archivo que no existe | `1 → no_existe.txt` | No se encontró el archivo: no_existe.txt | No se cargó el archivo. Se encontraron estos problemas:<br>- No se encontró el archivo: no_existe.txt | Pasó |
| P15 | Inesperada | Texto cualquiera como registro de pings ('hola') | `7 → hola` | no pertenecen al alfabeto {p, r, t}<br>Resultado AFD: RECHAZA<br>no se puede determinar | Aviso: estos símbolos no pertenecen al alfabeto {p, r, t}: a, h, l, o<br>Resultado AFD: RECHAZA<br>Estado del dispositivo: no se puede determinar, el registro está mal formado (cada ping debe escribirse pr o pt). | Pasó |

## Pruebas de apoyo de los modelos

Además de los 15 casos, `test_grafo.py`, `test_expresiones.py`, `test_automatas.py` y `test_gramatica.py` revisan cada modelo por separado (por ejemplo, que el AFN y el AFD coincidan en todas las cadenas de longitud 0 a 10). No cuentan como casos de prueba del sistema; sirven para comprobar el diseño. Se ejecutan todas con `python -m unittest`.

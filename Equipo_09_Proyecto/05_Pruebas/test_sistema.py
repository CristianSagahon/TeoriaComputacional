# Pruebas del SISTEMA COMPLETO: 15 casos de prueba.
#
# Cada caso ejecuta main.py como lo haría un usuario: se le mandan las
# opciones y datos que escribiría en el teclado y se revisa lo que el
# programa muestra después de la ÚLTIMA acción.
#
# Ejecutar desde la carpeta 05_Pruebas:
#   python -m unittest -v test_sistema      (pruebas)
#   python test_sistema.py --tabla           (tabla con los resultados obtenidos)

import os
import subprocess
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
CODIGO = os.path.join(AQUI, "..", "02_Codigo")
MAIN = os.path.join(CODIGO, "main.py")
DATOS = "../05_Pruebas/datos_prueba/"  # relativo a 02_Codigo, donde corre main.py

CARGAR_RED = ["1", ""]       # opción 1 + Enter (red de ejemplo)
CARGAR_EVENTOS = ["6", ""]   # opción 6 + Enter (eventos de ejemplo)
ANIDADA_1000 = "no(" * 1000 + "falla(PC1)" + ")" * 1000

# id, tipo de caso, descripción, entradas del usuario, textos esperados
CASOS = [
    ("P01", "Válida / normal", "Cargar la red de ejemplo",
     CARGAR_RED, ["Red cargada: 11 dispositivos y 10 enlaces."]),
    ("P02", "Válida / normal", "Ruta más corta Server1 a PC3 (hay un ciclo en la red)",
     CARGAR_RED + ["4", "Server1", "PC3"],
     ["Server1 -> Switch2 -> Router2 -> Switch3 -> PC3", "Saltos: 4"]),
    ("P03", "Válida / normal", "Conectividad con un equipo aislado (PC1 y PC4)",
     CARGAR_RED + ["3", "PC1", "PC4"], ["No: no existe ningún camino entre PC1 y PC4."]),
    ("P04", "Válida / normal", "Cargar pings: estado actual de cada equipo en el ciclo",
     CARGAR_EVENTOS,
     ["PC1         prprpr         ACTIVO", "PC3         prpt           SOBRECARGADO",
      "Server1     ptptpr         RECUPERACIÓN", "Server2     prptpt         FALLA"]),
    ("P05", "Válida / normal", "Ciclo completo Activo → Sobrecargado → Falla → Recuperación → Activo",
     ["7", "prptptprpr"],
     ["Resultado AFN: ACEPTA", "Resultado AFD: ACEPTA",
      "Ciclo de estados: ACTIVO -pr-> ACTIVO -pt-> SOBRECARGADO -pt-> FALLA "
      "-pr-> RECUPERACIÓN -pr-> ACTIVO", "Estado actual del dispositivo: ACTIVO"]),
    ("P06", "Válida / normal", "Consulta anidada y(conectado(PC1,Server1),no(falla(Server1)))",
     CARGAR_RED + CARGAR_EVENTOS + ["8", "y(conectado(PC1,Server1),no(falla(Server1)))", "n"],
     ["Resultado: FALSO"]),
    ("P07", "Inválida", "Nombre de dispositivo mal escrito (PC01)",
     CARGAR_RED + ["4", "PC01"], ["Error: 'PC01' no es un nombre válido."]),
    ("P08", "Inválida", "Archivo de red con 4 líneas incorrectas",
     ["1", DATOS + "red_con_errores.txt"],
     ["Línea 2:", "Línea 3: 'PC1,PC1' conecta un dispositivo consigo mismo.", "Línea 4:", "Línea 5:"]),
    ("P09", "Inválida", "Consulta con un paréntesis sin cerrar",
     CARGAR_RED + ["8", "y(conectado(PC1,Server1),no(falla(Server1))", "n"],
     ["Error: La consulta termina antes de tiempo: falta ')'."]),
    ("P10", "Inválida", "Consulta que niega una ruta: no(ruta(PC1,PC2))",
     CARGAR_RED + ["8", "no(ruta(PC1,PC2))", "n"],
     ["se esperaba una consulta de sí/no", "llegó 'ruta'"]),
    ("P11", "Límite", "Archivo de red vacío",
     ["1", DATOS + "red_vacia.txt"], ["El archivo no tiene ningún dispositivo."]),
    ("P12", "Límite", "Un solo timeout seguido de respuesta: ptpr (no llega a falla)",
     ["7", "ptpr"],
     ["Resultado AFD: RECHAZA", "Ciclo de estados: ACTIVO -pt-> SOBRECARGADO -pr-> ACTIVO",
      "Estado actual del dispositivo: ACTIVO"]),
    ("P13", "Límite", "Consulta con 1000 niveles de anidamiento",
     CARGAR_RED + CARGAR_EVENTOS + ["8", ANIDADA_1000, "n"],
     ["La consulta es válida, pero tiene demasiados niveles de anidamiento"]),
    ("P14", "Inesperada", "Archivo que no existe",
     ["1", "no_existe.txt"], ["No se encontró el archivo: no_existe.txt"]),
    ("P15", "Inesperada", "Texto cualquiera como registro de pings ('hola')",
     ["7", "hola"], ["no pertenecen al alfabeto {p, r, t}", "Resultado AFD: RECHAZA",
                     "no se puede determinar"]),
]

PREGUNTAS = [  # textos que el programa escribe al pedir datos
    "Opción: ",
    "Ruta del archivo de red (Enter = datos/red_ejemplo.txt): ",
    "Ruta del archivo de eventos (Enter = datos/eventos_ejemplo.txt): ",
    "Dispositivo origen: ",
    "Dispositivo destino: ",
    "Escriba un registro de pings (ej. prptpt) o un dispositivo con registro cargado (ej. Server1): ",
    "Consulta: ",
    "¿Mostrar la pila paso a paso? (s/n): ",
]


def ejecutar(entradas):
    """Ejecuta main.py con esas entradas (y '0' para salir) y regresa la salida."""
    texto = "\n".join(entradas + ["0"]) + "\n"
    proceso = subprocess.run([sys.executable, MAIN], input=texto, cwd=CODIGO,
                             capture_output=True, encoding="utf-8", timeout=30)
    return proceso.stdout


def salida_de_la_ultima_accion(salida):
    """Se queda solo con lo que mostró la última acción antes de salir,
    sin el menú ni las preguntas."""
    bloques = salida.split("===== NETWORK GRAPH ANALYZER =====")
    bloque = bloques[-2]  # el último bloque es el menú + "Hasta luego."
    lineas = []
    for linea in bloque.splitlines():
        if linea.strip() == "" or linea[:2] in [f"{n}." for n in range(10)]:
            continue  # líneas del menú
        if "Ejemplos: ruta(" in linea:
            continue  # ayuda fija que muestra la opción 8
        for pregunta in PREGUNTAS:
            linea = linea.replace(pregunta, "")
        if linea.strip():
            lineas.append(linea.strip())
    return lineas


class PruebasSistema(unittest.TestCase):
    pass


def crear_prueba(ident, entradas, esperados):
    def prueba(self):
        obtenido = "\n".join(salida_de_la_ultima_accion(ejecutar(entradas)))
        for texto in esperados:
            self.assertIn(texto, obtenido)
    prueba.__doc__ = ident
    return prueba


for _id, _tipo, _descripcion, _entradas, _esperados in CASOS:
    setattr(PruebasSistema, f"test_{_id}", crear_prueba(_id, _entradas, _esperados))


def imprimir_tabla():
    """Imprime la tabla de casos de prueba con lo que el programa mostró de verdad."""
    print("| ID | Tipo | Caso | Entrada | Resultado esperado | Resultado obtenido | Estado |")
    print("|---|---|---|---|---|---|---|")
    for ident, tipo, descripcion, entradas, esperados in CASOS:
        lineas = salida_de_la_ultima_accion(ejecutar(entradas))
        obtenido = "\n".join(lineas)
        estado = "Pasó" if all(e in obtenido for e in esperados) else "FALLÓ"
        if len(lineas) > 4:  # salidas largas: solo las líneas importantes
            lineas = [l for l in lineas if any(e in l for e in esperados)] or lineas[:4]
        entrada = " → ".join(repr(e) if e.strip() != e or e == "" else e for e in entradas)
        celda = "<br>".join(l.replace("|", "\\|") for l in lineas)
        esperado = "<br>".join(e.replace("|", "\\|") for e in esperados)
        if len(entrada) > 90:
            entrada = entrada[:87] + "..."
        print(f"| {ident} | {tipo} | {descripcion} | `{entrada}` | {esperado} | {celda} | {estado} |")


if __name__ == "__main__":
    if "--tabla" in sys.argv:
        imprimir_tabla()
    else:
        unittest.main(verbosity=2)

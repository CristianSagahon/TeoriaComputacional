# main.py
# Network Graph Analyzer: menú principal e integración de todas las partes.
# Equipo 9: David, Jared y Cristian.


import os
import sys

import automatas
import gramatica
import grafo as modulo_grafo
from expresiones import es_identificador_valido, es_registro_bien_formado

# Las trazas usan símbolos como δ, ε y →. Algunas terminales de Windows no
# los pueden escribir si la salida se redirige, así que se fuerza UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
RED_POR_DEFECTO = os.path.join(CARPETA_DATOS, "red_ejemplo.txt")
EVENTOS_POR_DEFECTO = os.path.join(CARPETA_DATOS, "eventos_ejemplo.txt")

MENU = """
===== NETWORK GRAPH ANALYZER =====
1. Cargar red desde archivo
2. Mostrar red (lista de adyacencia y grados)
3. Consultar conectividad entre dos dispositivos
4. Buscar ruta más corta
5. Detectar dispositivos aislados
6. Cargar archivo de eventos (pings)
7. Analizar registro de pings (AFN, AFD y ciclo de estados)
8. Ejecutar consulta (gramática y autómata de pila)
0. Salir"""


# ---------------------------------------------------------------------------
# Funciones de apoyo
# ---------------------------------------------------------------------------

def plural(cantidad, singular, plural_):
    """plural(1, 'enlace', 'enlaces') → '1 enlace'; con 2 → '2 enlaces'."""
    return f"{cantidad} {singular if cantidad == 1 else plural_}"


def pedir(mensaje):
    """Lee una línea del usuario sin espacios a los lados."""
    return input(mensaje).strip()


def pedir_dispositivo(grafo, mensaje):
    """
    Pide un nombre de dispositivo, lo valida con ER1 y revisa que exista
    en la red. Regresa el nombre o None si hubo un error (ya mostrado).
    """
    nombre = pedir(mensaje)
    if not es_identificador_valido(nombre):
        print(f"Error: '{nombre}' no es un nombre válido. Use Router, Switch, PC o "
              "Server seguido de un número sin ceros al inicio (ejemplo: PC1).")
        return None
    if nombre not in grafo:
        print(f"Error: el dispositivo {nombre} no existe en la red cargada.")
        return None
    return nombre


def hay_red(estado):
    """Revisa que ya se haya cargado una red y avisa si no."""
    if estado["grafo"] is None:
        print("Primero cargue una red (opción 1).")
        return False
    return True


def mostrar_errores(errores, habia_datos):
    """Muestra los errores de un archivo rechazado."""
    print("No se cargó el archivo. Se encontraron estos problemas:")
    for error in errores:
        print("  - " + error)
    if habia_datos:
        print("Se conservan los datos que ya estaban cargados.")


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

def opcion_cargar_red(estado):
    """Opción 1: lee el archivo de red, lo valida y lo guarda en estado."""
    ruta = pedir("Ruta del archivo de red (Enter = datos/red_ejemplo.txt): ")
    if ruta == "":
        ruta = RED_POR_DEFECTO
    grafo, errores = modulo_grafo.cargar_red(ruta)
    if errores:
        mostrar_errores(errores, estado["grafo"] is not None)
        return
    estado["grafo"] = grafo
    print(f"Red cargada: {plural(len(grafo), 'dispositivo', 'dispositivos')} y "
          f"{plural(modulo_grafo.contar_enlaces(grafo), 'enlace', 'enlaces')}.")


def opcion_mostrar_red(estado):
    """Opción 2: lista de adyacencia con el grado de cada dispositivo."""
    if not hay_red(estado):
        return
    grafo = estado["grafo"]
    grados = modulo_grafo.calcular_grados(grafo)
    print(f"Dispositivos: {len(grafo)}   Enlaces: {modulo_grafo.contar_enlaces(grafo)}")
    print(f"{'Dispositivo':<12} {'Grado':>5}  Vecinos")
    for dispositivo in sorted(grafo):
        vecinos = ", ".join(sorted(grafo[dispositivo])) or "(ninguno)"
        print(f"{dispositivo:<12} {grados[dispositivo]:>5}  {vecinos}")


def opcion_conectividad(estado):
    """Opción 3: dice si existe un camino entre dos dispositivos (BFS)."""
    if not hay_red(estado):
        return
    origen = pedir_dispositivo(estado["grafo"], "Dispositivo origen: ")
    if origen is None:
        return
    destino = pedir_dispositivo(estado["grafo"], "Dispositivo destino: ")
    if destino is None:
        return
    if modulo_grafo.estan_conectados(estado["grafo"], origen, destino):
        print(f"Sí: {origen} y {destino} están conectados.")
    else:
        print(f"No: no existe ningún camino entre {origen} y {destino}.")


def opcion_ruta(estado):
    """Opción 4: ruta con menos saltos entre dos dispositivos (BFS)."""
    if not hay_red(estado):
        return
    origen = pedir_dispositivo(estado["grafo"], "Dispositivo origen: ")
    if origen is None:
        return
    destino = pedir_dispositivo(estado["grafo"], "Dispositivo destino: ")
    if destino is None:
        return
    ruta = modulo_grafo.ruta_mas_corta(estado["grafo"], origen, destino)
    if ruta is None:
        print(f"No existe ruta entre {origen} y {destino}.")
    else:
        print("Ruta más corta: " + " -> ".join(ruta))
        print(f"Saltos: {len(ruta) - 1}")


def opcion_aislados(estado):
    """Opción 5: dispositivos con grado 0."""
    if not hay_red(estado):
        return
    aislados = modulo_grafo.dispositivos_aislados(estado["grafo"])
    if aislados:
        print("Dispositivos aislados (grado 0): " + ", ".join(aislados))
    else:
        print("No hay dispositivos aislados.")


def opcion_cargar_eventos(estado):
    """Opción 6: lee el archivo de pings y muestra el estado de cada equipo."""
    ruta = pedir("Ruta del archivo de eventos (Enter = datos/eventos_ejemplo.txt): ")
    if ruta == "":
        ruta = EVENTOS_POR_DEFECTO
    eventos, errores = automatas.cargar_eventos(ruta)
    if errores:
        mostrar_errores(errores, estado["eventos"] is not None)
        return
    estado["eventos"] = eventos
    print(f"Registros cargados: {len(eventos)}")
    print(f"  {'Dispositivo':<11} {'Registro':<14} {'Estado actual':<14} Falla registrada")
    for dispositivo in sorted(eventos):
        registro = eventos[dispositivo]
        falla = "sí" if automatas.hubo_falla(registro) else "no"
        print(f"  {dispositivo:<11} {registro:<14} "
              f"{automatas.estado_dispositivo(registro):<14} {falla}")
    if estado["grafo"] is not None:
        faltantes = sorted(d for d in eventos if d not in estado["grafo"])
        if faltantes:
            print("Aviso: estos dispositivos no están en la red cargada: "
                  + ", ".join(faltantes))


def opcion_analizar_pings(estado):
    """Opción 7: pasa un registro de pings por el AFN, el AFD y el ciclo de estados."""
    texto = pedir("Escriba un registro de pings (ej. prptpt) o un dispositivo "
                  "con registro cargado (ej. Server1): ")
    if es_identificador_valido(texto):
        if estado["eventos"] is None or texto not in estado["eventos"]:
            print(f"Error: no hay registro de pings cargado para {texto} (opción 6).")
            return
        print(f"Registro de {texto}: {estado['eventos'][texto]}")
        cadena = estado["eventos"][texto]
    else:
        cadena = texto

    acepta_afn, recorrido_afn = automatas.simular_afn(cadena)
    acepta_afd, recorrido_afd = automatas.simular_afd(cadena)

    simbolos_extra = sorted(set(cadena) - automatas.AFN_ALFABETO)
    if simbolos_extra:
        print("Aviso: estos símbolos no pertenecen al alfabeto {p, r, t}: "
              + ", ".join(simbolos_extra))

    print("Recorrido AFN: " + automatas.formatear_recorrido(recorrido_afn))
    print("Resultado AFN: " + ("ACEPTA" if acepta_afn else "RECHAZA"))
    print("Recorrido AFD: " + automatas.formatear_recorrido_afd(recorrido_afd))
    print("Resultado AFD: " + ("ACEPTA" if acepta_afd else "RECHAZA"))
    if acepta_afn == acepta_afd:
        print("El AFN y el AFD coinciden.")
    else:  # no debería pasar nunca; se deja para detectar errores
        print("ADVERTENCIA: el AFN y el AFD no coinciden.")
    if not es_registro_bien_formado(cadena):
        print("Estado del dispositivo: no se puede determinar, el registro está mal "
              "formado (cada ping debe escribirse pr o pt).")
        return
    if acepta_afd:
        print("Falla registrada: SÍ (hubo dos timeouts seguidos)")
    else:
        print("Falla registrada: NO (nunca hubo dos timeouts seguidos)")
    estado_final, recorrido_ciclo = automatas.simular_ciclo(cadena)
    print("Ciclo de estados: " + automatas.formatear_recorrido_ciclo(recorrido_ciclo))
    print("Estado actual del dispositivo: " + estado_final)


def opcion_consulta(estado):
    """Opción 8: tokeniza, valida con el autómata de pila y evalúa una consulta."""
    print("Ejemplos: ruta(PC1,Server2)   aislados()   "
          "y(conectado(PC1,Server1),no(falla(Server1)))")
    texto = pedir("Consulta: ")
    ver_pila = pedir("¿Mostrar la pila paso a paso? (s/n): ").lower() == "s"

    resultado, traza, error = gramatica.ejecutar_consulta(
        texto, estado["grafo"], estado["eventos"])

    if ver_pila and traza:
        print(f"{'Paso':>4}  {'Estado':<6} {'Pila (tope a la izquierda)':<34} Acción")
        for numero, (estado_ap, _, pila, accion) in enumerate(traza):
            print(f"{numero:>4}  {estado_ap:<6} {pila:<34} {accion}")

    if error:
        print("Error: " + error)
    elif isinstance(resultado, bool):
        print("Resultado: " + ("VERDADERO" if resultado else "FALSO"))
    elif resultado is None:
        print("Resultado: no existe ruta entre esos dispositivos.")
    elif texto.strip().startswith("ruta"):
        print("Resultado: " + " -> ".join(resultado))
    elif len(resultado) == 0:
        print("Resultado: no hay dispositivos aislados.")
    else:
        print("Resultado: " + ", ".join(resultado))


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

OPCIONES = {
    "1": opcion_cargar_red,
    "2": opcion_mostrar_red,
    "3": opcion_conectividad,
    "4": opcion_ruta,
    "5": opcion_aislados,
    "6": opcion_cargar_eventos,
    "7": opcion_analizar_pings,
    "8": opcion_consulta,
}


def main():
    """Ciclo del menú: muestra opciones hasta que el usuario elige 0."""
    estado = {"grafo": None, "eventos": None}
    while True:
        print(MENU)
        opcion = pedir("Opción: ")
        if opcion == "0":
            print("Hasta luego.")
            break
        if opcion not in OPCIONES:
            print(f"Opción no válida: '{opcion}'. Escriba un número del 0 al 8.")
            continue
        OPCIONES[opcion](estado)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma terminado.")

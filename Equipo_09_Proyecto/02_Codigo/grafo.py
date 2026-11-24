

from collections import deque

from expresiones import es_linea_red_valida


def crear_grafo():
    """Regresa un grafo vacío."""
    return {}


def agregar_dispositivo(grafo, dispositivo):
    """Agrega un dispositivo sin enlaces (si ya existe, no hace nada)."""
    if dispositivo not in grafo:
        grafo[dispositivo] = set()


def agregar_enlace(grafo, origen, destino):
    """Agrega un enlace en los dos sentidos, porque el grafo es no dirigido."""
    agregar_dispositivo(grafo, origen)
    agregar_dispositivo(grafo, destino)
    grafo[origen].add(destino)
    grafo[destino].add(origen)


def cargar_red(ruta_archivo):
    """
    Lee el archivo de red y construye el grafo.

    Regresa una tupla (grafo, errores):
      - Si el archivo no tiene errores, errores es una lista vacía.
      - Si hay errores, grafo es None y errores trae un mensaje por problema.
    Se rechaza el archivo completo si alguna línea está mal, para no
    trabajar con una red a medias.
    """
    errores = []
    grafo = crear_grafo()

    try:
        with open(ruta_archivo, encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        return None, ["No se encontró el archivo: " + ruta_archivo]
    except OSError as error:
        return None, ["No se pudo leer el archivo: " + str(error)]

    for numero, linea in enumerate(lineas, start=1):
        linea = linea.strip()

        # Líneas vacías y comentarios se ignoran.
        if linea == "" or linea.startswith("#"):
            continue

        if not es_linea_red_valida(linea):
            errores.append(f"Línea {numero}: formato inválido '{linea}'. "
                           "Se espera Dispositivo,Dispositivo o un solo Dispositivo "
                           "(ejemplo: Router1,Switch1).")
            continue

        partes = linea.split(",")
        if len(partes) == 1:
            agregar_dispositivo(grafo, partes[0])
        elif partes[0] == partes[1]:
            errores.append(f"Línea {numero}: '{linea}' conecta un dispositivo "
                           "consigo mismo.")
        else:
            agregar_enlace(grafo, partes[0], partes[1])

    if errores:
        return None, errores
    if len(grafo) == 0:
        return None, ["El archivo no tiene ningún dispositivo."]
    return grafo, []


def contar_enlaces(grafo):
    """Cada enlace aparece dos veces (A→B y B→A), por eso se divide entre 2."""
    return sum(len(vecinos) for vecinos in grafo.values()) // 2


def calcular_grados(grafo):
    """Regresa un diccionario dispositivo → número de enlaces."""
    return {dispositivo: len(vecinos) for dispositivo, vecinos in grafo.items()}


def dispositivos_aislados(grafo):
    """Regresa en orden alfabético los dispositivos con grado 0."""
    return sorted(d for d, vecinos in grafo.items() if len(vecinos) == 0)


def bfs(grafo, origen):
    """
    Búsqueda en anchura desde 'origen'.

    Regresa un diccionario 'padre': para cada dispositivo alcanzado guarda
    desde qué dispositivo se llegó a él (el origen tiene padre None).
    Los vecinos se recorren en orden alfabético para que el resultado
    sea siempre el mismo.
    """
    padre = {origen: None}
    cola = deque([origen])

    while cola:
        actual = cola.popleft()
        for vecino in sorted(grafo[actual]):
            if vecino not in padre:
                padre[vecino] = actual
                cola.append(vecino)
    return padre


def estan_conectados(grafo, origen, destino):
    """True si existe algún camino entre los dos dispositivos."""
    return destino in bfs(grafo, origen)


def ruta_mas_corta(grafo, origen, destino):
    """
    Regresa la lista de dispositivos de la ruta con menos saltos,
    o None si no hay camino. Como BFS visita por niveles, la primera vez
    que llega al destino lo hace por el camino más corto.
    """
    padre = bfs(grafo, origen)
    if destino not in padre:
        return None

    # Se reconstruye la ruta caminando hacia atrás desde el destino.
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = padre[actual]
    ruta.reverse()
    return ruta


def matriz_adyacencia(grafo):
    """
    Regresa (nombres, matriz). matriz[i][j] es 1 si nombres[i] y nombres[j]
    están conectados y 0 si no. Se usa para mostrar y documentar la red.
    """
    nombres = sorted(grafo)
    matriz = []
    for fila in nombres:
        matriz.append([1 if columna in grafo[fila] else 0 for columna in nombres])
    return nombres, matriz

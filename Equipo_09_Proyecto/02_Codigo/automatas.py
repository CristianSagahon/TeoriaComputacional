

from expresiones import es_linea_eventos_valida, es_registro_bien_formado

# ---------------------------------------------------------------------------
# AFN (Etapa 5)
# ---------------------------------------------------------------------------
# Cada transición lleva a un CONJUNTO de estados. Si un par (estado, símbolo)
# no aparece en el diccionario, la transición va al conjunto vacío.

AFN_ESTADOS = {"q0", "q1", "q2", "q3", "q4", "q5", "q6"}
AFN_ALFABETO = {"p", "r", "t"}
AFN_INICIAL = "q0"
AFN_FINALES = {"q5"}
AFN_TRANSICIONES = {
    ("q0", "p"): {"q1", "q2"},  # ping normal (q1) o "aquí empieza la falla" (q2)
    ("q1", "r"): {"q0"},        # el ping normal fue contestado
    ("q1", "t"): {"q0"},        # o tuvo timeout, pero no es el inicio de la falla
    ("q2", "t"): {"q3"},        # primer timeout de la falla
    ("q3", "p"): {"q4"},        # siguiente ping
    ("q4", "t"): {"q5"},        # segundo timeout seguido: falla detectada
    ("q5", "p"): {"q6"},        # después de la falla pueden venir más pings
    ("q6", "r"): {"q5"},
    ("q6", "t"): {"q5"},
}


def simular_afn(cadena):
    """
    Simula el AFN siguiendo TODOS los caminos posibles a la vez:
    se guarda el conjunto de estados en los que podría estar el autómata.

    Regresa (acepta, recorrido). recorrido es una lista de pares
    (símbolo leído, conjunto de estados después de leerlo); el primer par
    es ("", {q0}) y representa el inicio.
    """
    actuales = {AFN_INICIAL}
    recorrido = [("", actuales)]

    for simbolo in cadena:
        siguientes = set()
        for estado in actuales:
            siguientes = siguientes | AFN_TRANSICIONES.get((estado, simbolo), set())
        actuales = siguientes
        recorrido.append((simbolo, actuales))
        if len(actuales) == 0:
            break  # ningún camino sigue vivo: ya no puede aceptar

    acepta = len(actuales & AFN_FINALES) > 0
    return acepta, recorrido


def formatear_conjunto(estados):
    """Convierte {"q3", "q0"} en el texto "{q0, q3}" (ordenado)."""
    if len(estados) == 0:
        return "{}"  # conjunto vacío (en la documentación se escribe ∅)
    return "{" + ", ".join(sorted(estados)) + "}"


def formatear_recorrido(recorrido):
    """Texto del recorrido, por ejemplo: {q0} -p-> {q1, q2} -t-> {q0, q3}."""
    texto = formatear_conjunto(recorrido[0][1])
    for simbolo, estados in recorrido[1:]:
        texto += f" -{simbolo}-> " + formatear_conjunto(estados)
    return texto


# ---------------------------------------------------------------------------
# AFD (Etapa 6)
# ---------------------------------------------------------------------------
# Obtenido A MANO del AFN con el método de subconjuntos (ver documento de la
# Etapa 6). Cada estado del AFD representa un conjunto de estados del AFN.
# Z es el estado de error (conjunto vacío): una vez ahí, ya no se sale.

AFD_SUBCONJUNTOS = {
    "A": {"q0"},
    "B": {"q1", "q2"},
    "C": {"q0", "q3"},
    "D": {"q1", "q2", "q4"},
    "E": {"q0", "q3", "q5"},
    "F": {"q1", "q2", "q4", "q6"},
    "G": {"q0", "q5"},
    "H": {"q1", "q2", "q6"},
    "Z": set(),
}
AFD_ESTADOS = set(AFD_SUBCONJUNTOS)
AFD_ALFABETO = {"p", "r", "t"}
AFD_INICIAL = "A"
AFD_FINALES = {"E", "G"}  # los subconjuntos que contienen q5
AFD_TRANSICIONES = {
    ("A", "p"): "B", ("A", "r"): "Z", ("A", "t"): "Z",
    ("B", "p"): "Z", ("B", "r"): "A", ("B", "t"): "C",
    ("C", "p"): "D", ("C", "r"): "Z", ("C", "t"): "Z",
    ("D", "p"): "Z", ("D", "r"): "A", ("D", "t"): "E",
    ("E", "p"): "F", ("E", "r"): "Z", ("E", "t"): "Z",
    ("F", "p"): "Z", ("F", "r"): "G", ("F", "t"): "E",
    ("G", "p"): "H", ("G", "r"): "Z", ("G", "t"): "Z",
    ("H", "p"): "Z", ("H", "r"): "G", ("H", "t"): "E",
    ("Z", "p"): "Z", ("Z", "r"): "Z", ("Z", "t"): "Z",
}


def simular_afd(cadena):
    """
    Simula el AFD: en cada paso hay UN solo estado actual.

    Regresa (acepta, recorrido), donde recorrido es una lista de pares
    (símbolo leído, estado después de leerlo); el primero es ("", "A").
    Un símbolo que no está en el alfabeto manda al estado de error Z.
    """
    actual = AFD_INICIAL
    recorrido = [("", actual)]

    for simbolo in cadena:
        if simbolo in AFD_ALFABETO:
            actual = AFD_TRANSICIONES[(actual, simbolo)]
        else:
            actual = "Z"
        recorrido.append((simbolo, actual))

    return actual in AFD_FINALES, recorrido


def formatear_recorrido_afd(recorrido):
    """Texto del recorrido, por ejemplo: A -p-> B -t-> C."""
    texto = recorrido[0][1]
    for simbolo, estado in recorrido[1:]:
        texto += f" -{simbolo}-> {estado}"
    return texto


def hubo_falla(registro):
    """
    True si el registro pertenece a L, es decir, si en algún momento hubo
    dos timeouts seguidos. Lo decide el AFD.
    """
    acepta, _ = simular_afd(registro)
    return acepta


# ---------------------------------------------------------------------------
# Ciclo de estados del dispositivo
# ---------------------------------------------------------------------------


CICLO_ESTADOS = ["ACTIVO", "SOBRECARGADO", "FALLA", "RECUPERACIÓN"]
CICLO_ALFABETO = {"pr", "pt"}
CICLO_INICIAL = "ACTIVO"
CICLO_TRANSICIONES = {
    ("ACTIVO", "pr"): "ACTIVO",
    ("ACTIVO", "pt"): "SOBRECARGADO",
    ("SOBRECARGADO", "pr"): "ACTIVO",          # se recuperó de un timeout aislado
    ("SOBRECARGADO", "pt"): "FALLA",           # segundo timeout seguido
    ("FALLA", "pr"): "RECUPERACIÓN",           # vuelve a responder
    ("FALLA", "pt"): "FALLA",
    ("RECUPERACIÓN", "pr"): "ACTIVO",          # segunda respuesta: ya está estable
    ("RECUPERACIÓN", "pt"): "FALLA",           # recae antes de estabilizarse
}


def separar_pings(registro):
    """'ptptpr' → ['pt', 'pt', 'pr']. Regresa None si el registro está mal formado."""
    if not es_registro_bien_formado(registro):
        return None
    return [registro[i:i + 2] for i in range(0, len(registro), 2)]


def simular_ciclo(registro):
    """
    Recorre el ciclo de estados con el registro, un ping a la vez.

    Regresa (estado_final, recorrido). recorrido es una lista de pares
    (ping leído, estado después de leerlo); el primero es ("", "ACTIVO").
    Si el registro está mal formado regresa (None, []).
    """
    pings = separar_pings(registro)
    if pings is None:
        return None, []
    actual = CICLO_INICIAL
    recorrido = [("", actual)]
    for ping in pings:
        actual = CICLO_TRANSICIONES[(actual, ping)]
        recorrido.append((ping, actual))
    return actual, recorrido


def formatear_recorrido_ciclo(recorrido):
    """Texto del recorrido, por ejemplo: ACTIVO -pt-> SOBRECARGADO -pt-> FALLA."""
    texto = recorrido[0][1]
    for ping, estado in recorrido[1:]:
        texto += f" -{ping}-> {estado}"
    return texto


def estado_dispositivo(registro):
    """
    Estado ACTUAL de un equipo: el estado en el que termina el ciclo
    (ACTIVO, SOBRECARGADO, FALLA o RECUPERACIÓN). None si está mal formado.
    """
    estado, _ = simular_ciclo(registro)
    return estado


def cargar_eventos(ruta_archivo):
    """
    Lee el archivo de eventos y regresa (eventos, errores).

    eventos es un diccionario dispositivo → registro de pings,
    por ejemplo {"Server1": "ptptpr"}.
    Igual que con la red, si alguna línea está mal se rechaza el archivo
    completo (eventos = None) y se regresan todos los mensajes de error.
    """
    errores = []
    eventos = {}

    try:
        with open(ruta_archivo, encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        return None, ["No se encontró el archivo: " + ruta_archivo]
    except OSError as error:
        return None, ["No se pudo leer el archivo: " + str(error)]

    for numero, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue

        # ER3: Dispositivo:registro, donde el registro son pings pr o pt.
        if not es_linea_eventos_valida(linea):
            errores.append(f"Línea {numero}: formato inválido '{linea}'. "
                           "Se espera Dispositivo:registro con pings pr o pt "
                           "(ejemplo: Server1:ptptpr).")
            continue

        dispositivo, registro = linea.split(":")
        if dispositivo in eventos:
            errores.append(f"Línea {numero}: el dispositivo {dispositivo} "
                           "ya tenía un registro en este archivo.")
        else:
            eventos[dispositivo] = registro

    if errores:
        return None, errores
    if len(eventos) == 0:
        return None, ["El archivo no tiene ningún registro de eventos."]
    return eventos, []

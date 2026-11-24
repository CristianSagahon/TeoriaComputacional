

import re

import automatas
import grafo as modulo_grafo
from expresiones import es_identificador_valido

# ---------------------------------------------------------------------------
# Gramática G = (V, T, P, S)   (Etapa 7)
# ---------------------------------------------------------------------------
# Los terminales son TOKENS: palabras reservadas, paréntesis, coma e "id"
# (cualquier nombre de dispositivo que cumpla ER1).

PALABRAS_RESERVADAS = {"ruta", "aislados", "conectado", "falla", "no", "y", "o"}
SIMBOLOS = {"(", ")", ","}

VARIABLES = {"S", "B"}
TERMINALES = PALABRAS_RESERVADAS | SIMBOLOS | {"id"}
SIMBOLO_INICIAL = "S"
PRODUCCIONES = {
    "S": [
        ["ruta", "(", "id", ",", "id", ")"],          # S → ruta(id,id)
        ["aislados", "(", ")"],                       # S → aislados()
        ["B"],                                        # S → B
    ],
    "B": [
        ["conectado", "(", "id", ",", "id", ")"],     # B → conectado(id,id)
        ["falla", "(", "id", ")"],                    # B → falla(id)
        ["no", "(", "B", ")"],                        # B → no(B)
        ["y", "(", "B", ",", "B", ")"],               # B → y(B,B)
        ["o", "(", "B", ",", "B", ")"],               # B → o(B,B)
    ],
}

# ---------------------------------------------------------------------------
# Separación en tokens (análisis léxico)
# ---------------------------------------------------------------------------
# Expresión auxiliar: un trozo es un bloque de espacios, una palabra
# (letras y dígitos), un paréntesis o coma, o cualquier otro carácter suelto
# (que será un error).
ER_TROZO = r"\s+|[A-Za-z0-9]+|[(),]|."


def tokenizar(consulta):
    """
    Convierte el texto de una consulta en una lista de tokens.

    Cada token es una tupla (tipo, valor):
      ("conectado", "conectado"), ("id", "PC1"), ("(", "("), ...
    Regresa (tokens, error). Si todo está bien, error es None;
    si no, tokens es None y error explica el problema.
    """
    tokens = []
    for trozo in re.finditer(ER_TROZO, consulta):
        texto = trozo.group()
        posicion = trozo.start() + 1  # posición contando desde 1

        if texto.isspace():
            continue  # los espacios solo separan, se ignoran
        if texto in SIMBOLOS or texto in PALABRAS_RESERVADAS:
            tokens.append((texto, texto))
        elif es_identificador_valido(texto):
            tokens.append(("id", texto))
        elif texto.isalnum():
            return None, (f"Posición {posicion}: '{texto}' no es una palabra de "
                          "consulta ni un dispositivo válido.")
        else:
            return None, f"Posición {posicion}: el carácter '{texto}' no está permitido."

    if len(tokens) == 0:
        return None, "La consulta está vacía."
    return tokens, None


def tipos_de_tokens(tokens):
    """Solo los tipos, por ejemplo ['falla', '(', 'id', ')']. Útil para mostrar."""
    return [tipo for tipo, _ in tokens]


# ---------------------------------------------------------------------------
# Autómata de pila   (Etapa 8)
# ---------------------------------------------------------------------------


FONDO = "Z0"  # símbolo del fondo de la pila

TABLA_DE_ELECCION = {
    ("S", "ruta"): 0, ("S", "aislados"): 1,                    # P1, P2
    ("S", "conectado"): 2, ("S", "falla"): 2, ("S", "no"): 2,  # P3 (S → B)
    ("S", "y"): 2, ("S", "o"): 2,
    ("B", "conectado"): 0, ("B", "falla"): 1, ("B", "no"): 2,  # P4, P5, P6
    ("B", "y"): 3, ("B", "o"): 4,                              # P7, P8
}

NUMERO_DE_PRODUCCION = {  # solo para mostrar el nombre P1..P8 en la traza
    ("S", 0): "P1", ("S", 1): "P2", ("S", 2): "P3",
    ("B", 0): "P4", ("B", 1): "P5", ("B", 2): "P6", ("B", 3): "P7", ("B", 4): "P8",
}


def texto_pila(pila):
    """La pila se guarda como lista con el TOPE AL FINAL. Para mostrarla
    se escribe con el tope a la izquierda: ['Z0', ')', 'B'] → 'B ) Z0'."""
    return " ".join(reversed(pila))


def validar_consulta(tokens):
    """
    Ejecuta el autómata de pila sobre la lista de tokens.

    Regresa (valida, traza, error):
      - valida: True si la consulta pertenece al lenguaje de la gramática.
      - traza: lista de pasos (estado, entrada restante, pila, acción).
      - error: None si es válida, o un mensaje que explica el problema.
    """
    entrada = tipos_de_tokens(tokens)
    posicion = 0                      # índice del siguiente token por leer
    estado = "q0"
    pila = [FONDO]
    traza = []

    def anotar(accion):
        """Guarda un paso de la traza con el estado actual de la pila."""
        restante = " ".join(entrada[posicion:]) or "ε"
        traza.append((estado, restante, texto_pila(pila), accion))

    # Transición inicial: δ(q0, ε, Z0) = (q1, S Z0)
    anotar("inicio")
    pila.append(SIMBOLO_INICIAL)
    estado = "q1"
    anotar("δ(q0, ε, Z0) = (q1, S Z0)")

    while True:
        tope = pila[-1]
        actual = entrada[posicion] if posicion < len(entrada) else None

        if tope == FONDO:
            if actual is None:
                # δ(q1, ε, Z0) = (q2, Z0): se acepta
                estado = "q2"
                anotar("δ(q1, ε, Z0) = (q2, Z0)  ACEPTA")
                return True, traza, None
            mensaje = (f"Sobra texto después del final de la consulta, "
                       f"a partir del token {posicion + 1} ('{tokens[posicion][1]}').")
            anotar("RECHAZA: " + mensaje)
            return False, traza, mensaje

        if tope in VARIABLES:
            eleccion = TABLA_DE_ELECCION.get((tope, actual))
            if eleccion is None:
                if actual is None:
                    mensaje = "La consulta termina antes de tiempo."
                elif tope == "B":
                    mensaje = (f"Token {posicion + 1}: se esperaba una consulta de sí/no "
                               f"(conectado, falla, no, y, o) y llegó '{tokens[posicion][1]}'.")
                else:
                    mensaje = (f"Token {posicion + 1}: '{tokens[posicion][1]}' no puede "
                               "iniciar una consulta.")
                anotar("RECHAZA: " + mensaje)
                return False, traza, mensaje
            derecha = PRODUCCIONES[tope][eleccion]
            pila.pop()
            for simbolo in reversed(derecha):  # al revés, para que el primero quede arriba
                pila.append(simbolo)
            nombre = NUMERO_DE_PRODUCCION[(tope, eleccion)]
            anotar(f"expandir {nombre}: {tope} → {' '.join(derecha)}")
            continue

        # El tope es un terminal: debe coincidir con el token actual.
        if actual == tope:
            pila.pop()
            posicion += 1
            anotar(f"emparejar '{tope}'")
            continue

        if actual is None:
            mensaje = f"La consulta termina antes de tiempo: falta '{tope}'."
        else:
            mensaje = (f"Token {posicion + 1}: se esperaba '{tope}' "
                       f"y llegó '{tokens[posicion][1]}'.")
        anotar("RECHAZA: " + mensaje)
        return False, traza, mensaje


# ---------------------------------------------------------------------------
# Evaluación de una consulta ya validada
# ---------------------------------------------------------------------------
# Se recorre la lista de tokens siguiendo la misma forma que la gramática.
# _evaluar regresa (valor, índice del siguiente token).

class ErrorDeConsulta(Exception):
    """Error al evaluar: por ejemplo, un dispositivo que no está en la red.
    Es la única clase del proyecto; solo sirve para poder lanzar el error desde
    cualquier nivel de la consulta anidada y atraparlo en ejecutar_consulta."""


def _revisar_dispositivo(nombre, grafo):
    """Lanza ErrorDeConsulta si el dispositivo no está en la red cargada."""
    if nombre not in grafo:
        raise ErrorDeConsulta(f"El dispositivo {nombre} no existe en la red cargada.")


def _evaluar(tokens, i, grafo, eventos):
    """
    Evalúa la consulta que empieza en tokens[i] y regresa
    (valor, índice del token que sigue después de ella).
    Para no, y, o se llama a sí misma con las consultas de adentro.
    El guion bajo inicial indica que es de uso interno de este archivo.
    """
    palabra = tokens[i][0]

    if palabra in ("ruta", "conectado"):
        origen, destino = tokens[i + 2][1], tokens[i + 4][1]   # palabra ( id , id )
        _revisar_dispositivo(origen, grafo)
        _revisar_dispositivo(destino, grafo)
        if palabra == "ruta":
            valor = modulo_grafo.ruta_mas_corta(grafo, origen, destino)
        else:
            valor = modulo_grafo.estan_conectados(grafo, origen, destino)
        return valor, i + 6

    if palabra == "aislados":                                  # aislados ( )
        return modulo_grafo.dispositivos_aislados(grafo), i + 3

    if palabra == "falla":                                     # falla ( id )
        nombre = tokens[i + 2][1]
        _revisar_dispositivo(nombre, grafo)
        if eventos is None or nombre not in eventos:
            raise ErrorDeConsulta(f"No hay registro de pings para {nombre}. "
                                  "Cargue un archivo de eventos que lo incluya.")
        return automatas.hubo_falla(eventos[nombre]), i + 4

    if palabra == "no":                                        # no ( B )
        valor, i = _evaluar(tokens, i + 2, grafo, eventos)
        return (not valor), i + 1                              # se salta ')'

    # y ( B , B )   u   o ( B , B )
    izquierda, i = _evaluar(tokens, i + 2, grafo, eventos)
    derecha, i = _evaluar(tokens, i + 1, grafo, eventos)       # se salta ','
    if palabra == "y":
        return (izquierda and derecha), i + 1
    return (izquierda or derecha), i + 1


def ejecutar_consulta(texto, grafo, eventos):
    """
    Proceso completo de la opción 8 del menú:
    tokenizar → validar con el autómata de pila → evaluar.

    Regresa (resultado, traza, error). Si hay error, resultado es None.
    """
    tokens, error = tokenizar(texto)
    if error:
        return None, [], error

    valida, traza, error = validar_consulta(tokens)
    if not valida:
        return None, traza, error

    if grafo is None:
        return None, traza, "Primero cargue una red (opción 1)."
    try:
        resultado, _ = _evaluar(tokens, 0, grafo, eventos)
    except ErrorDeConsulta as problema:
        return None, traza, str(problema)
    except RecursionError:
        # El autómata de pila no tiene límite (usa una lista), pero _evaluar
        # es recursiva y Python solo permite unas 1000 llamadas anidadas.
        return None, traza, ("La consulta es válida, pero tiene demasiados niveles "
                             "de anidamiento para evaluarla (el límite es de alrededor "
                             "de 990 niveles).")
    return resultado, traza, None

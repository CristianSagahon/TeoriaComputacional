
import re

# ER1: identificador de dispositivo.
# Ejemplos válidos: Router1, Switch2, PC10, Server1
ER_IDENTIFICADOR = r"(Router|Switch|PC|Server)[1-9][0-9]*"

# ER2: línea del archivo de red.
# Un enlace "Dispositivo,Dispositivo" o un solo dispositivo sin enlaces.
ER_LINEA_RED = ER_IDENTIFICADOR + r"(," + ER_IDENTIFICADOR + r")?"

# ER3: línea del archivo de eventos.
# "Dispositivo:eventos", donde cada ping es pr (respuesta) o pt (timeout).
ER_REGISTRO_PINGS = r"(p[rt])+"   # la parte de ER3 que va después de los dos puntos
ER_LINEA_EVENTOS = ER_IDENTIFICADOR + r":" + ER_REGISTRO_PINGS


def es_identificador_valido(texto):
    """Regresa True si el texto completo es un nombre de dispositivo válido."""
    return re.fullmatch(ER_IDENTIFICADOR, texto) is not None


def es_linea_red_valida(linea):
    """Regresa True si la línea completa tiene el formato del archivo de red."""
    return re.fullmatch(ER_LINEA_RED, linea) is not None


def es_linea_eventos_valida(linea):
    """Regresa True si la línea completa tiene el formato del archivo de eventos."""
    return re.fullmatch(ER_LINEA_EVENTOS, linea) is not None


def es_registro_bien_formado(registro):
    """True si el registro solo tiene pings completos (pr o pt), al menos uno."""
    return re.fullmatch(ER_REGISTRO_PINGS, registro) is not None

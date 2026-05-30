# ============================================================
#  ParseBurger — Módulo 5: Tokenizador
#  Clase 5 — Gramática regular
#
#  Normaliza el texto del usuario antes de pasarlo al parser.
#  Aplica correcciones de léxico cerrado y elimina palabras
#  funcionales irrelevantes para la estructura del pedido.
# ============================================================

NORMALIZACIONES = {
    "clasica":        ["clásica"],
    "perro_caliente": ["perro caliente", "perro-caliente"],
    "hotdog":         ["hot dog", "hot-dog"],
}

IGNORAR = {"pedir", "favor", "por", "me", "por_favor"}

# Mapa de caracteres con tilde → sin tilde
_TILDES = str.maketrans("áéíóúÁÉÍÓÚüÜñÑ", "aeiouAEIOUuUnN")

def tokenizar(texto):
    """
    Convierte el texto del usuario en una lista de tokens normalizados.
    """
    texto = texto.lower().strip()

    # Eliminar puntuación
    for c in ".,!?¿¡;:\"'":
        texto = texto.replace(c, " ")

    # Normalizar frases multi-palabra
    for token_norm, variantes in NORMALIZACIONES.items():
        for var in variantes:
            if var in texto:
                texto = texto.replace(var, token_norm)

    # Normalizar caracteres con tilde
    texto = texto.translate(_TILDES)

    # Filtrar palabras irrelevantes
    tokens = [t for t in texto.split() if t not in IGNORAR]
    return tokens

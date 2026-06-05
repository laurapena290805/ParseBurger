# **** Léxico con rasgos morfológicos (DAGs en Python) ****

lexico_dcg = {
    # Verbos de pedido
    "quiero":   {"cat": "VERBO_PEDIR", "pers": "1", "num": "sg"},
    "quisiera": {"cat": "VERBO_PEDIR", "pers": "1", "num": "sg"},
    "dame":     {"cat": "VERBO_PEDIR", "pers": "2", "num": "sg"},
    "ponme":    {"cat": "VERBO_PEDIR", "pers": "2", "num": "sg"},

    # Cantidades
    "un":     {"cat": "CANTIDAD", "num": "sg", "gen": "masc"},
    "una":    {"cat": "CANTIDAD", "num": "sg", "gen": "fem"},
    "dos":    {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "tres":   {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "cuatro": {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "cinco":  {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "otro":   {"cat": "CANTIDAD", "num": "sg", "gen": "neu"},
    "otra":   {"cat": "CANTIDAD", "num": "sg", "gen": "neu"},

    # Productos
    "hamburguesa":  {"cat": "TIPO_BURGER", "num": "sg", "gen": "fem"},
    "hamburguesas": {"cat": "TIPO_BURGER", "num": "pl", "gen": "fem"},
    "clasica":      {"cat": "TIPO_BURGER", "num": "sg", "gen": "fem"},
    "clasicas":     {"cat": "TIPO_BURGER", "num": "pl", "gen": "fem"},
    "doble":        {"cat": "TIPO_BURGER", "num": "sg", "gen": "masc"},
    "dobles":       {"cat": "TIPO_BURGER", "num": "pl", "gen": "masc"},
    "especial":     {"cat": "TIPO_BURGER", "num": "sg", "gen": "neu"},
    "especiales":    {"cat": "TIPO_BURGER", "num": "pl", "gen": "neu"},
    "vegana":       {"cat": "TIPO_BURGER", "num": "sg", "gen": "fem"},
    "veganas":      {"cat": "TIPO_BURGER", "num": "pl", "gen": "fem"},

    # Modificadores
    "sin":      {"cat": "NEG"},
    "con":      {"cat": "POS"},
    "extra":    {"cat": "EXTRA"},
    "mucho":    {"cat": "INTENSIF"},
    "bastante": {"cat": "INTENSIF"},
    "poco":     {"cat": "INTENSIF"},
    "y":        {"cat": "CONJ"},
    "pero":     {"cat": "CONJ_ADV"},

    # Ingredientes
    "cebolla":   {"cat": "INGREDIENTE"},
    "queso":     {"cat": "INGREDIENTE"},
    "tomate":    {"cat": "INGREDIENTE"},
    "lechuga":   {"cat": "INGREDIENTE"},
    "pepinillo": {"cat": "INGREDIENTE"},
    "mayonesa":  {"cat": "INGREDIENTE"},
    "mostaza":   {"cat": "INGREDIENTE"},
    "ketchup":   {"cat": "INGREDIENTE"},
    "carne":     {"cat": "INGREDIENTE"},
    "tocino":    {"cat": "INGREDIENTE"},
}

# Tabla de concordancia de género
CONCORDANCIA_GEN = {
    ("masc", "masc"): True,
    ("fem",  "fem"):  True,
    ("neu",  "masc"): True,    # "dos dobles" ✓
    ("neu",  "fem"):  True,    # "dos hamburguesas" ✓
    ("neu",  "neu"):  True,    # "dos especiales" ✓
    ("masc", "neu"):  True,    # "un especial" ✓
    ("fem",  "neu"):  True,    # "una especial" ✓
    ("masc", "fem"):  False,   # "un hamburguesa" ✗
    ("fem",  "masc"): False,   # "una doble" ✗
}


# Algoritmo de unificación
def unificar(dag1, dag2):
    """
    Combina dos DAGs de rasgos.
    Retorna el DAG unificado, o None si hay conflicto.
    """
    resultado = dict(dag1)
    for rasgo, valor in dag2.items():
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
            elif resultado[rasgo] != valor:
                return None    # mismo rasgo, valores distintos → CONFLICTO
        else:
            resultado[rasgo] = valor
    return resultado


# Parser DCG
def dcg_parse_pedido(tokens):
    """
    Verifica concordancia de género/número entre CANTIDAD y PRODUCTO
    usando el algoritmo de unificación.
    Retorna un dict con los rasgos semánticos del pedido, o None si falla.
    """
    pos       = 0
    resultado = {}

    if pos >= len(tokens):
        return None
    w_verbo = lexico_dcg.get(tokens[pos])
    if not w_verbo or w_verbo["cat"] != "VERBO_PEDIR":
        return None
    resultado["verbo"] = tokens[pos]
    pos += 1

    if pos >= len(tokens):
        return None
    w_cant = lexico_dcg.get(tokens[pos])
    if not w_cant or w_cant["cat"] != "CANTIDAD":
        return None
    resultado["cantidad_token"]  = tokens[pos]
    resultado["cantidad_rasgos"] = w_cant
    pos += 1

    if pos >= len(tokens):
        return None
    w_prod = lexico_dcg.get(tokens[pos])
    if not w_prod or w_prod["cat"] != "TIPO_BURGER":
        return None

    ADJETIVOS_BURGER = {"clasica", "doble", "especial", "vegana", "clasicas", "dobles", "especiales", "veganas"}
    nombre_producto  = tokens[pos]

    # "in" para comparar contra los dos tokens válidos — antes decía == (tupla) lo cual nunca es True
    if (tokens[pos] in ("hamburguesa", "hamburguesas")
            and pos + 1 < len(tokens)
            and tokens[pos + 1] in ADJETIVOS_BURGER):
        pos += 1
        nombre_producto = f"hamburguesa {tokens[pos]}"
        # Los rasgos del producto pasan a ser los del adjetivo (clasica, doble, etc.)
        w_prod = lexico_dcg.get(tokens[pos], w_prod)

    pos += 1

    # ── Concordancia en dos pasos ──────────────────────────────
    #
    # Paso 1: género via CONCORDANCIA_GEN
    #   Necesario porque "neu" (dos/tres/cuatro) es compatible con
    #   fem y masc, pero unificar() lo rechazaría por ser valores distintos.
    num_cant = w_cant["num"]
    num_prod = w_prod["num"]
    gen_cant = w_cant["gen"]
    gen_prod = w_prod["gen"]

    if not CONCORDANCIA_GEN.get((gen_cant, gen_prod), True):
        return None  # "un hamburguesa" ✗, "una doble" ✗
 
    rasgos_num_cant = {"num": w_cant["num"]}
    rasgos_num_prod = {"num": w_prod["num"]}
    if unificar(rasgos_num_cant, rasgos_num_prod) is None:
        return None  # "un hamburguesas" ✗, "una clasicas" ✗
 
    resultado["producto"]        = nombre_producto
    resultado["producto_rasgos"] = w_prod

    # 4. Modificadores opcionales
    mods = []
    ultimo_tipo = None   # guarda el tipo del último MOD para coordinar ingredientes
    while pos < len(tokens):
        tok = tokens[pos]
        w   = lexico_dcg.get(tok)
        if not w:
            break
        cat = w["cat"]

        if cat in ("NEG", "POS", "EXTRA", "INTENSIF"):
            tipo_mod = "POS" if cat == "INTENSIF" else cat
            pos += 1
            if pos < len(tokens):
                w_ing = lexico_dcg.get(tokens[pos])
                if w_ing and w_ing["cat"] == "INGREDIENTE":
                    mods.append({"tipo": tipo_mod, "ing": tokens[pos]})
                    ultimo_tipo = tipo_mod
                    pos += 1
        elif cat in ("CONJ", "CONJ_ADV"):
            if ultimo_tipo and pos + 1 < len(tokens):
                w_sig = lexico_dcg.get(tokens[pos + 1])
                if w_sig and w_sig["cat"] == "INGREDIENTE":
                    pos += 1
                    mods.append({"tipo": ultimo_tipo, "ing": tokens[pos]})
                    pos += 1
                    continue
            pos += 1
        else:
            break

    resultado["modificadores"] = mods
    return resultado


def dcg_parse_np(tokens, pos):
    """
    Parsea un NP_PEDIDO a partir de `pos`.
    Retorna (resultado_dict, nueva_pos) o (None, pos).
    Es la unidad mínima: CANTIDAD PRODUCTO [MODS].
    """
    resultado = {}
    start = pos

    # CANTIDAD
    if pos >= len(tokens):
        return None, start
    w_cant = lexico_dcg.get(tokens[pos])
    if not w_cant or w_cant["cat"] != "CANTIDAD":
        return None, start
    resultado["cantidad_token"]  = tokens[pos]
    resultado["cantidad_rasgos"] = w_cant
    pos += 1

    # PRODUCTO
    if pos >= len(tokens):
        return None, start
    w_prod = lexico_dcg.get(tokens[pos])
    if not w_prod or w_prod["cat"] != "TIPO_BURGER":
        return None, start

    ADJETIVOS_BURGER = {"clasica","doble","especial","vegana",
                        "clasicas","dobles","especiales","veganas"}
    nombre_producto = tokens[pos]
    if (tokens[pos] in ("hamburguesa","hamburguesas")
            and pos + 1 < len(tokens)
            and tokens[pos + 1] in ADJETIVOS_BURGER):
        pos += 1
        nombre_producto = f"hamburguesa {tokens[pos]}"
        w_prod = lexico_dcg.get(tokens[pos], w_prod)
    pos += 1

    # Concordancia
    gen_cant = w_cant["gen"]
    gen_prod = w_prod["gen"]
    if not CONCORDANCIA_GEN.get((gen_cant, gen_prod), True):
        return None, start
    if unificar({"num": w_cant["num"]}, {"num": w_prod["num"]}) is None:
        return None, start

    resultado["producto"]        = nombre_producto
    resultado["producto_rasgos"] = w_prod

    # MODS opcionales
    mods = []
    ultimo_tipo = None
    while pos < len(tokens):
        tok = tokens[pos]
        w   = lexico_dcg.get(tok)
        if not w:
            break
        cat = w["cat"]
        if cat in ("NEG", "POS", "EXTRA", "INTENSIF"):
            tipo_mod = "POS" if cat == "INTENSIF" else cat
            pos += 1
            if pos < len(tokens):
                w_ing = lexico_dcg.get(tokens[pos])
                if w_ing and w_ing["cat"] == "INGREDIENTE":
                    mods.append({"tipo": tipo_mod, "ing": tokens[pos]})
                    ultimo_tipo = tipo_mod
                    pos += 1
        elif cat in ("CONJ", "CONJ_ADV"):
            if ultimo_tipo and pos + 1 < len(tokens):
                w_sig = lexico_dcg.get(tokens[pos + 1])
                if w_sig and w_sig["cat"] == "INGREDIENTE":
                    pos += 1
                    mods.append({"tipo": ultimo_tipo, "ing": tokens[pos]})
                    pos += 1
                    continue
            # No es ingrediente coordinado — podría ser "y <NP>"
            break
        else:
            break

    resultado["modificadores"] = mods
    return resultado, pos


def dcg_parse_lista_pedidos(tokens):
    """
    Parsea VERBO NP_LIST donde NP_LIST = NP (y NP)*.
    Soporta también "quiero dos hamburguesas una clasica y otra vegana"
    donde "dos hamburguesas" es un encabezado genérico seguido de sub-pedidos.
    Retorna lista de dicts (uno por sub-pedido) o None si falla.
    """
    pos = 0
    # Verbo
    if pos >= len(tokens):
        return None
    w_verbo = lexico_dcg.get(tokens[pos])
    if not w_verbo or w_verbo["cat"] != "VERBO_PEDIR":
        return None
    verbo = tokens[pos]
    pos += 1

    # Primer NP obligatorio
    np1, pos1 = dcg_parse_np(tokens, pos)
    if np1 is None:
        return None

    if pos1 < len(tokens):
        w_siguiente = lexico_dcg.get(tokens[pos1])
        if w_siguiente and w_siguiente["cat"] == "CANTIDAD":
            # El primer NP era un encabezado genérico; ignorarlo y releer
            pos = pos1
            np1, pos = dcg_parse_np(tokens, pos)
            if np1 is None:
                return None

    if pos1 > pos:
        pos = pos1

    np1["verbo"] = verbo
    pedidos = [np1]

    while pos < len(tokens):
        w = lexico_dcg.get(tokens[pos])
        if not w or w["cat"] not in ("CONJ", "CONJ_ADV"):
            break
        pos_conj = pos
        pos += 1
        np2, pos2 = dcg_parse_np(tokens, pos)
        if np2 is None:
            pos = pos_conj   # retroceder si no hay NP tras la conjunción
            break
        np2["verbo"] = verbo
        pedidos.append(np2)
        pos = pos2

    if pos < len(tokens):
        return None  # tokens sin consumir
    return pedidos
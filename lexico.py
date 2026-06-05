
lexico_dcg = {
    "quiero":   {"cat": "VERBO_PEDIR", "pers": "1", "num": "sg"},
    "quisiera": {"cat": "VERBO_PEDIR", "pers": "1", "num": "sg"},
    "dame":     {"cat": "VERBO_PEDIR", "pers": "2", "num": "sg"},
    "ponme":    {"cat": "VERBO_PEDIR", "pers": "2", "num": "sg"},

    "un":     {"cat": "CANTIDAD", "num": "sg", "gen": "masc"},
    "una":    {"cat": "CANTIDAD", "num": "sg", "gen": "fem"},
    "dos":    {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "tres":   {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "cuatro": {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "cinco":  {"cat": "CANTIDAD", "num": "pl", "gen": "neu"},
    "otro":   {"cat": "CANTIDAD", "num": "sg", "gen": "neu"},
    "otra":   {"cat": "CANTIDAD", "num": "sg", "gen": "neu"},

    "hamburguesa":  {"cat": "TIPO_BURGER", "num": "sg", "gen": "fem"},
    "hamburguesas": {"cat": "TIPO_BURGER", "num": "pl", "gen": "fem"},
    "clasica":      {"cat": "TIPO_BURGER", "num": "sg", "gen": "fem"},
    "clasicas":     {"cat": "TIPO_BURGER", "num": "pl", "gen": "fem"},
    "doble":        {"cat": "TIPO_BURGER", "num": "sg", "gen": "neu"},
    "dobles":       {"cat": "TIPO_BURGER", "num": "pl", "gen": "neu"},
    "especial":     {"cat": "TIPO_BURGER", "num": "sg", "gen": "neu"},
    "especiales":   {"cat": "TIPO_BURGER", "num": "pl", "gen": "neu"},
    "vegana":       {"cat": "TIPO_BURGER", "num": "sg", "gen": "fem"},
    "veganas":      {"cat": "TIPO_BURGER", "num": "pl", "gen": "fem"},

    "sin":      {"cat": "NEG"},
    "con":      {"cat": "POS"},
    "extra":    {"cat": "EXTRA"},
    "mucho":    {"cat": "INTENSIF"},
    "bastante": {"cat": "INTENSIF"},
    "poco":     {"cat": "INTENSIF"},
    "y":        {"cat": "CONJ"},
    "pero":     {"cat": "CONJ_ADV"},

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
    "salsa":     {"cat": "INGREDIENTE"},
}

# Palabras que pueden actuar como EXTRA en posición de modificador,
# aunque en el léxico estén registradas con otra categoría primaria.
# Esto evita duplicar entradas en lexico_dcg manteniendo el dict plano.
PALABRAS_EXTRA = {"doble", "extra"}

CONCORDANCIA_GEN = {
    ("masc", "masc"): True,
    ("fem",  "fem"):  True,
    ("neu",  "masc"): True,
    ("neu",  "fem"):  True,
    ("neu",  "neu"):  True,
    ("masc", "neu"):  True,
    ("fem",  "neu"):  True,
    ("masc", "fem"):  False,
    ("fem",  "masc"): False,
}


def unificar(dag1, dag2):
    resultado = dict(dag1)
    for rasgo, valor in dag2.items():
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
            elif resultado[rasgo] != valor:
                return None
        else:
            resultado[rasgo] = valor
    return resultado


def dcg_parse_pedido(tokens):
    pos = 0
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

    gen_cant = w_cant["gen"]
    gen_prod = w_prod["gen"]
    if not CONCORDANCIA_GEN.get((gen_cant, gen_prod), True):
        return None
    if unificar({"num": w_cant["num"]}, {"num": w_prod["num"]}) is None:
        return None

    resultado["producto"]        = nombre_producto
    resultado["producto_rasgos"] = w_prod

    mods, pos = _parse_mods(tokens, pos)
    resultado["modificadores"] = mods
    return resultado if pos == len(tokens) else None


def dcg_parse_np(tokens, pos):
    resultado = {}
    start = pos

    if pos >= len(tokens):
        return None, start
    w_cant = lexico_dcg.get(tokens[pos])
    if not w_cant or w_cant["cat"] != "CANTIDAD":
        return None, start
    resultado["cantidad_token"]  = tokens[pos]
    resultado["cantidad_rasgos"] = w_cant
    pos += 1

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

    gen_cant = w_cant["gen"]
    gen_prod = w_prod["gen"]
    if not CONCORDANCIA_GEN.get((gen_cant, gen_prod), True):
        return None, start
    if unificar({"num": w_cant["num"]}, {"num": w_prod["num"]}) is None:
        return None, start

    resultado["producto"]        = nombre_producto
    resultado["producto_rasgos"] = w_prod

    mods, pos = _parse_mods(tokens, pos)
    resultado["modificadores"] = mods
    return resultado, pos


def _parse_mods(tokens, pos):
    """
    Parsea la lista de modificadores a partir de pos.
    Retorna (lista_mods, nueva_pos).

    Reconoce:
      NEG  INGREDIENTE          → sin queso
      POS  INGREDIENTE          → con queso
      POS  EXTRA  INGREDIENTE   → con extra queso / con doble queso
      POS  INTENSIF INGREDIENTE → con mucho queso
      EXTRA INGREDIENTE         → extra queso / doble queso   ← NUEVO
      CONJ INGREDIENTE          → y queso (hereda tipo anterior)
    """
    mods = []
    ultimo_tipo = None

    while pos < len(tokens):
        tok = tokens[pos]
        w   = lexico_dcg.get(tok)

        # ── NEG: "sin <ING>" ─────────────────────────────────
        if w and w["cat"] == "NEG":
            pos += 1
            if pos < len(tokens):
                w_ing = lexico_dcg.get(tokens[pos])
                if w_ing and w_ing["cat"] == "INGREDIENTE":
                    mods.append({"tipo": "NEG", "ing": tokens[pos]})
                    ultimo_tipo = "NEG"
                    pos += 1
                    continue
            break

        # ── POS: "con [extra|doble|INTENSIF] <ING>" o "con <ING>" ──
        if w and w["cat"] == "POS":
            pos += 1
            if pos >= len(tokens):
                break
            tok2 = tokens[pos]
            w2   = lexico_dcg.get(tok2)

            # "con extra|doble <ING>"
            if tok2 in PALABRAS_EXTRA and pos + 1 < len(tokens):
                w_ing = lexico_dcg.get(tokens[pos + 1])
                if w_ing and w_ing["cat"] == "INGREDIENTE":
                    mods.append({"tipo": "EXTRA", "ing": tokens[pos + 1],
                                 "cuantificador": tok2})
                    ultimo_tipo = "EXTRA"
                    pos += 2
                    continue

            # "con mucho|bastante|poco <ING>"
            if w2 and w2["cat"] == "INTENSIF" and pos + 1 < len(tokens):
                w_ing = lexico_dcg.get(tokens[pos + 1])
                if w_ing and w_ing["cat"] == "INGREDIENTE":
                    mods.append({"tipo": "POS", "ing": tokens[pos + 1],
                                 "intensidad": tok2})
                    ultimo_tipo = "POS"
                    pos += 2
                    continue

            # "con <ING>"
            if w2 and w2["cat"] == "INGREDIENTE":
                mods.append({"tipo": "POS", "ing": tok2})
                ultimo_tipo = "POS"
                pos += 1
                continue

            break

        # ── EXTRA suelto: "extra|doble <ING>" ────────────────
        # Cubre "doble queso" cuando ya se consumió el producto.
        if tok in PALABRAS_EXTRA and pos + 1 < len(tokens):
            w_ing = lexico_dcg.get(tokens[pos + 1])
            if w_ing and w_ing["cat"] == "INGREDIENTE":
                mods.append({"tipo": "EXTRA", "ing": tokens[pos + 1],
                             "cuantificador": tok})
                ultimo_tipo = "EXTRA"
                pos += 2
                continue

        # ── CONJ: "y|pero <ING>" (hereda último tipo) ────────
        if w and w["cat"] in ("CONJ", "CONJ_ADV"):
            saved = pos
            pos += 1
            if pos < len(tokens):
                w_ing = lexico_dcg.get(tokens[pos])
                if w_ing and w_ing["cat"] == "INGREDIENTE" and ultimo_tipo:
                    mods.append({"tipo": ultimo_tipo, "ing": tokens[pos]})
                    pos += 1
                    continue
            # No era ingrediente coordinado → revertir y salir
            pos = saved
            break

        # No reconocido → salir del bucle de mods
        break

    return mods, pos


def dcg_parse_lista_pedidos(tokens):
    pos = 0
    if pos >= len(tokens):
        return None
    w_verbo = lexico_dcg.get(tokens[pos])
    if not w_verbo or w_verbo["cat"] != "VERBO_PEDIR":
        return None
    verbo = tokens[pos]
    pos += 1

    np1, pos1 = dcg_parse_np(tokens, pos)
    if np1 is None:
        return None

    if pos1 < len(tokens):
        w_sig = lexico_dcg.get(tokens[pos1])
        if w_sig and w_sig["cat"] == "CANTIDAD":
            pos = pos1
            np1, pos = dcg_parse_np(tokens, pos)
            if np1 is None:
                return None
        else:
            pos = pos1
    else:
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
            pos = pos_conj
            break
        np2["verbo"] = verbo
        pedidos.append(np2)
        pos = pos2

    if pos < len(tokens):
        return None
    return pedidos
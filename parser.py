# **** Clase Nodo — árbol de derivación ****

class Nodo:
    def __init__(self, etiqueta, hijos=None):
        self.etiqueta = etiqueta
        self.hijos    = hijos if hijos else []

    def mostrar(self, nivel=0):
        sangria   = "  " * nivel
        resultado = sangria + self.etiqueta + "\n"
        for hijo in self.hijos:
            if isinstance(hijo, Nodo):
                resultado += hijo.mostrar(nivel + 1)
            else:
                resultado += "  " * (nivel + 1) + str(hijo) + "\n"
        return resultado

    def __repr__(self):
        return self.mostrar()


# **** Parser recursivo descendente ****

def parse(simbolo, tokens, pos, gram):
    """Un solo árbol — retorna (Nodo, nueva_pos) o (None, pos)."""
    if simbolo not in gram:
        if pos < len(tokens) and tokens[pos] == simbolo:
            return tokens[pos], pos + 1
        return None, pos

    for produccion in gram[simbolo]:
        nodo_actual = Nodo(simbolo)
        pos_actual  = pos
        exito       = True

        for subsimbolo in produccion:
            hijo, pos_actual = parse(subsimbolo, tokens, pos_actual, gram)
            if hijo is None:
                exito = False
                break
            nodo_actual.hijos.append(hijo)

        if exito:
            return nodo_actual, pos_actual

    return None, pos


def parse_todos(simbolo, tokens, pos, gram):
    """
    Todos los árboles posibles.
    Si len(resultado) > 1 → ambigüedad detectada.
    """
    if simbolo not in gram:
        if pos < len(tokens) and tokens[pos] == simbolo:
            return [(tokens[pos], pos + 1)]
        return []

    resultados = []

    for produccion in gram[simbolo]:
        candidatos = [([], pos)]

        for sub in produccion:
            nuevos = []
            for hijos, p in candidatos:
                for hijo, p2 in parse_todos(sub, tokens, p, gram):
                    nuevos.append((hijos + [hijo], p2))
            candidatos = nuevos
            if not candidatos:
                break

        for hijos, p_final in candidatos:
            resultados.append((Nodo(simbolo, hijos), p_final))

    return resultados
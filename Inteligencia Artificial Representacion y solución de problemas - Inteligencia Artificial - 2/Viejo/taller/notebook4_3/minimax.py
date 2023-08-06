import numpy as np

def minimax_search(juego, estado):
    jugador = juego.a_jugar(estado)
    # Determina cuál jugador tiene el turno
    if jugador == 2: # Juegan las X (MAX)        
        valor, accion = max_value(juego, estado)
    else: # Juegan las O (MIN)
        valor, accion = min_value(juego, estado)
    return accion

def max_value(juego, estado):
    if juego.es_terminal(estado):
        jugador = juego.a_jugar(estado)
        return juego.utilidad(estado, jugador), None
    v = -np.infty
    for a in juego.acciones(estado):
        v2, a2 = min_value(juego, juego.resultado(estado, a))
        if v2 > v:
            v = v2
            accion = a
    return v, accion

def min_value(juego, estado):
    if juego.es_terminal(estado):
        jugador = juego.a_jugar(estado)
        return juego.utilidad(estado, jugador), None
    v = np.infty
    for a in juego.acciones(estado):
        v2, a2 = max_value(juego, juego.resultado(estado, a))
        if v2 < v:
            v = v2
            accion = a
    return v, accion
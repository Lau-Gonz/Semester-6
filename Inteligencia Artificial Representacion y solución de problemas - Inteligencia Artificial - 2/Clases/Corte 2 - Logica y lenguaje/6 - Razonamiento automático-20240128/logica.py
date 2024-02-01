'''
Módulo con las clases para implementar una base de conocimiento.
'''
import numpy as np


class Regla :
    '''
    Implementación de las reglas (cláusula definida)
    Input: 
        - regla, que es una cadena de la forma p1 & ... & pn > q
    '''

    def __init__(self, regla:str) :
        self.nombre = regla
        indice_conectivo = regla.find('>')
        if indice_conectivo > 0:
            antecedente = regla[:indice_conectivo].split('&')
            consecuente = regla[indice_conectivo + 1:]
        else:
            antecedente = regla.split('&')
            consecuente = ''
        self.antecedente = antecedente
        self.consecuente = consecuente

    def __str__(self) -> str:
        return self.nombre

class LPQuery:

    '''
    Implementación de una base de conocimiento.
    Input:  
        - base_conocimiento_lista, que es una lista de cláusulas definidas
                de la forma p1 & ... & pn > q
    '''

    def __init__(self, base_conocimiento_lista:list):
        self.hechos = []
        self.reglas = []
        self.atomos = []
        for formula in base_conocimiento_lista:
            self.tell(formula)

    def tell(self, formula:str):
        '''
        Incluye una fórmula en la base de conocimientos.
        Determina primero si la fórmula es una regla o un hecho.
        Revisa si debe actualizar la lista de átomos en self.atomos
        Input:
            - formula, que es una cadena de la forma 
                * p1 & ... & pn > q 
                * p
        '''
        # chequeamos si tenemos una regla
        indice_conectivo = formula.find('>')
        if indice_conectivo > 0:
            # chequeamos si no está ya en las reglas
            if formula not in [regla.nombre for regla in self.reglas]:
                regla = Regla(formula)
                self.reglas.append(regla)
                # chequeamos si debemos actualiar los átomos
                for a in regla.antecedente:
                    if '-' in a:
                        atomo = a[1:]
                    else:
                        atomo = a
                    if atomo not in self.atomos:
                        self.atomos.append(a)
                if '-' in regla.consecuente:
                    atomo = regla.consecuente[1:]
                else:
                    atomo = regla.consecuente
                if atomo not in self.atomos:
                    self.atomos.append(atomo)
        elif formula not in self.hechos:
            # asumimos que tenemos un hecho
            self.hechos.append(formula)
            # chequeamos si debemos actualizar los átomos
            if '-' in formula:
            	atomo = formula[1:]
            else:
            	atomo = formula
            if atomo not in self.atomos:
            	self.atomos.append(atomo)

    def __str__(self) -> str:
        cadena = 'Hechos:\n'
        for hecho in self.hechos:
            cadena += '\t' + hecho + '\n'
        cadena += '\nReglas:\n'
        for regla in self.reglas:
            cadena += '\t' + regla.nombre + '\n'
        return cadena

    def reglas_aplicables(self, objetivo:str) -> list:
        '''
        Devuelve una lista con las reglas cuyo consecuente es el objetivo.
        Input:
            - objetivo, cadena que se asume es un literal
        Output:
            - lista de reglas
        '''
        return [r for r in self.reglas if r.consecuente == objetivo]

    def test_objetivo(self, literal:str) -> str:
        '''
        Devuelve True/False dependiendo si el literal es un hecho de la base.
        Input:
            - literal, que es una cadena
        Output:
            - True/False dependiendo si el literal es un hecho de la base.
        '''
        return literal in self.hechos


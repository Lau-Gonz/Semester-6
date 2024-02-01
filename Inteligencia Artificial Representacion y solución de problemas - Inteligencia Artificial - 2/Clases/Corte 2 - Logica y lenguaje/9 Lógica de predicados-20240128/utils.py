import nltk
from nltk import Tree
from nltk.parse import FeatureEarleyChartParser
import re

def arbol_sin_caracteristicas(s:str) -> Tree:
    '''
    Toma un árbol de una cadena, de la cual elimina las características
    que se encuentran entre paréntesis cuadrados, y devuelve un Tree de nltk.
    Input:
        - s, una cadena con un árbol en representación plana
    Output:
        - un árbol de la clase Tree de la librería nltk
    '''
    s = s.replace('[', '{')
    s = s.replace(']', '}')
    s = re.sub('{.*?}', '', s)
    try:
        arbol = Tree.fromstring(s)
    except:
        s = re.sub(',.*?>}', '', s)  
        arbol = Tree.fromstring(s)
    return arbol

def parsear(tokens:list, parser:FeatureEarleyChartParser, verbose=False) -> Tree:
    '''
    Toma una lista de tokens y devuelve el árbol de análisis
    usando el parser suministrado.
    Input:
        - toekns, una lista de cadenas con una oración
        - parser, un parser FeatureEarleyChartParser de nltk
        - verbose, booleano para imprimir información
    Output:
        - un árbol de la clase Tree de la librería nltk o None
    '''
    if verbose:
        print(f'Haciendo el parsing de la oración:\n\n\t{" ".join(tokens)}\n')
    trees = parser.parse(tokens)
    arboles = []
    for t in trees:
        if verbose:
            print(f'El árbol lineal obtenido es:\n\n\t{t}\n')
        return arbol_sin_caracteristicas(str(t))
    if verbose:
        print('¡El parser no produjo ningún árbol!')
    return None
    
def obtener_formula(tokens:list, parser:FeatureEarleyChartParser, clausura:bool=False) -> nltk.sem.logic:
    '''
    Toma una lista de tokens y devuelve su representación lógica.
    Input:
        - toekns, una lista de cadenas con una oración.
        - parser, un parser FeatureEarleyChartParser de nltk.
        - clausura, un booleano para devolver la fórmula clausurada o no.
    Output:
        - formula clausurada
    '''
    trees = parser.parse(tokens)
    for t in trees:
        formula = t.label().get('SEM')
        return formula
    return None


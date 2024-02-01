from nltk import Tree
from nltk.grammar import FeatureGrammar
from nltk.parse import FeatureEarleyChartParser
import re
import pandas as pd

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
    return Tree.fromstring(s)

def parsear(tokens:str, parser, verbose=False) -> Tree:
    '''
    Toma una lista de tokens y devuelve el árbol de análisis
    usando el parser suministrado.
    Input:
        - toekns, una lista de cadenas con una oración
        - parser, un parser de nltk
        - verbose, booleano para imprimir información
    Output:
        - un árbol de la clase Tree de la librería nltk o None
    '''
    if verbose:
        print(f'Parsing la oración:\n\n\t{" ".join(tokens)}\n')
    trees = parser.parse(tokens)
    arboles = []
    for t in trees:
        arboles.append(str(t))
    if len(arboles) > 0:
        arbol = arboles[0]
        if verbose:
            print(f'El árbol lineal obtenido es:\n\n\t{arbol}\n')
        return arbol_sin_caracteristicas(arbol)
    else:
        if verbose:
            print('¡El parser no produjo ningún árbol!')
        return None

def obtener_tp(df:pd.DataFrame, verbose=False) -> int:
    '''
    Toma unos resultados de clasificación y devuelve los true positive.
    Input:
        - df, que es un pandas dataframe con las siguientes columnas:
            * oracion,
            * gold, que es el gold standard de la forma si/no
            * resultado, que es el resultado de clasificación de la forma si/no
        - verbose, booleano para presentar información
    Output:
        - número de true positive
    '''
    data = df.copy()
    data['g_positivo'] = data['gold'].apply(lambda x: 1 if x == 'si' else 0)
    data['positivo'] = data['resultado'].apply(lambda x: 1 if x == 'si' else 0)
    data['tp'] = data['g_positivo'] * data['positivo']
    if verbose:
        print(data.head())
    return sum(data['tp'].to_list())

def obtener_fp(df:pd.DataFrame, verbose=False) -> int:
    '''
    Toma unos resultados de clasificación y devuelve los false positive.
    Input:
        - df, que es un pandas dataframe con las siguientes columnas:
            * oracion,
            * gold, que es el gold standard de la forma si/no
            * resultado, que es el resultado de clasificación de la forma si/no
    Output:
        - número de false positive
    '''
    data = df.copy()
    data['f_positivo'] = data['gold'].apply(lambda x: 0 if x == 'si' else 1)
    data['positivo'] = data['resultado'].apply(lambda x: 1 if x == 'si' else 0)
    data['fp'] = data['f_positivo'] * data['positivo']
    if verbose:
        print(data.head())
    return sum(data['fp'].to_list())

def obtener_fn(df:pd.DataFrame, verbose=False) -> int:
    '''
    Toma unos resultados de clasificación y devuelve los false negative.
    Input:
        - data, que es un pandas dataframe con las siguientes columnas:
            * oracion,
            * gold, que es el gold standard de la forma si/no
            * resultado, que es el resultado de clasificación de la forma si/no
    Output:
        - número de false negative
    '''
    data = df.copy()
    data['f_negativo'] = data['gold'].apply(lambda x: 0 if x == 'no' else 1)
    data['negativo'] = data['resultado'].apply(lambda x: 1 if x == 'no' else 0)
    data['fn'] = data['f_negativo'] * data['negativo']
    if verbose:
        print(data.head())
    return sum(data['fn'].to_list())

def obtener_tn(df:pd.DataFrame, verbose=False) -> int:
    '''
    Toma unos resultados de clasificación y devuelve los true negative.
    Input:
        - data, que es un pandas dataframe con las siguientes columnas:
            * oracion,
            * gold, que es el gold standard de la forma si/no
            * resultado, que es el resultado de clasificación de la forma si/no
    Output:
        - número de true negative
    '''
    data = df.copy()
    data['g_negativo'] = data['gold'].apply(lambda x: 1 if x == 'no' else 1)
    data['negativo'] = data['resultado'].apply(lambda x: 1 if x == 'no' else 0)
    data['tn'] = data['g_negativo'] * data['negativo']
    if verbose:
        print(data.head())
    return sum(data['tn'].to_list())

def medir_F1(data:pd.DataFrame, verbose=False) -> float:
    '''
    Devuelve la medida F1 de la clasificación.
    Input:
        - data que es un pandas dataframe con por lo menos las siguientes columnas
            * oracion,
            * gold, que es el gold standard de la forma si/no
            * resultado, que es el resultado de clasificación de la forma si/no
        - verbose, booleano para presentar información
    Output:
        - medida F1
    '''
    tp = obtener_tp(data)
    fp = obtener_fp(data)
    fn = obtener_fn(data)
    try:
        precision = tp / (tp + fp)
    except:
        precision = 0
    try:
        recall = tp / (tp + fn)
    except:
        recall = 0
    try:
        f1 = (2 * precision * recall)/(precision + recall)
    except:
        f1 = 0
    if verbose:
        print(f'Precision:\n\n\t{precision}\n')        
        print(f'Recall:\n\n\t{recall}\n')
        print(f'F1:\n\n\t{f1}\n')
    return f1

def medir_accuracy(data:pd.DataFrame, verbose=False) -> float:
    '''
    Devuelve el accuracy de la clasificación.
    Input:
        - data que es un pandas dataframe con por lo menos las siguientes columnas
            * oracion,
            * gold, que es el gold standard de la forma si/no
            * resultado, que es el resultado de clasificación de la forma si/no
        - verbose, booleano para presentar información
    Output:
        - accuracy
    '''
    tp = obtener_tp(data)
    fp = obtener_fp(data)
    fn = obtener_fn(data)
    tn = obtener_tn(data)
    try:
        accuracy = (tp + tn)/(tp + fp + fn + tn)
    except:
        print('¡Oops, parece que no hay datos!')
        accuracy = None
    if verbose:
        print(f'Accuracy:\n\n\t{f1}\n')
    return accuracy

def test_gramatica_carac(prueba_oraciones:str, gramatica:str=None, trace:int=-1) -> list:
    '''
    Toma una lista de oraciones y prueba la gramática. 
    Devuelve una lista de errores.
    Input:
        - oraciones, un string con el nombre de un csv con 
          por lo menos las siguientes columnas
            * oracion,
            * gold, que es el gold standard de la forma si/no
        - gramatica, cadena con la gramática
        - trace, valor entero para indicar qué tanta 
          información se debe proporcionar durante el proceso
    Output:
        - errores, archivo con csv con las columnas 
            * num_oracion
            * error
    ''' 
    data = pd.read_csv(prueba_oraciones)
    if trace > 1:
        print(data.head())
    oraciones = data['oracion'].to_list()
    gold = data['gold'].to_list()
    resultado = []
    errores = pd.DataFrame({'numero':[], 'error':[]})
    gramatica_ = FeatureGrammar.fromstring(gramatica)
    trace_parser = 0 if trace < 2 else trace - 2
    parser = FeatureEarleyChartParser(gramatica_, trace=trace_parser)
    if trace > 0:
        print('Procesando oraciones...')
    for i, oracion in enumerate(oraciones):
        if trace > 1:
            print(f'Procesando \"{oracion}\"')
        try:
            tokens = oracion.split()
            arboles = [str(t) for t in parser.parse(tokens)]
            if len(arboles) == 0:
                resultado.append('no')
                if gold[i] == 'si':
                    errores.loc[len(errores)] = [oracion, 'falso negativo']
            else:
                resultado.append('si')
                if gold[i] == 'no':
                    errores.loc[len(errores)] = [oracion, 'falso positivo']
        except Exception as e: 
            resultado.append('no')
            errores.loc[len(errores)] = [oracion, str(e)]
    data['resultado'] = resultado
    errores.to_csv('errores.csv')
    f1 = medir_F1(data)
    if trace > 0:
        print('Errores guardados en archivo.')
        print(f'Medida F1:\n\n\t{f1}')
    return f1
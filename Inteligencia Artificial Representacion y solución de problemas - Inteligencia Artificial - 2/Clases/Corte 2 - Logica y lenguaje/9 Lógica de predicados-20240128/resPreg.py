import re
import nltk
from nltk import load_parser
from nltk.grammar import FeatureGrammar
from nltk.parse import FeatureEarleyChartParser
import numpy as np
from itertools import product
from parseMod import Modelo
from logUtils import Ytoria
import utils
from logica import LPQuery


nltk.download('punkt', quiet=True)
sent_detector = nltk.data.load('tokenizers/punkt/spanish.pickle')
lp = nltk.sem.logic.LogicParser()


def preprocess_text(text:str) -> list:
    '''
    Pequeño preprocesamiento:
        * Eliminamos el punto final de la oración
        * Todo a minúsculas
        * Pone espacio alrededor de símbolos de interrogación
    Input:
        - text
    Output:
        - List of sentences
    '''
    sentences = sent_detector.tokenize(text.strip())
    sentences = [s for s in sentences if s not in ['.', ',', ';', ':']]
    new_sentences = []
    for sentence in sentences:
        # sentence = sentence.lower()
        sentence = re.sub(r"([¿?])", r" \1 ", sentence)
        if sentence[-1] in ['.', ' ']:
            sentence = sentence[:-1]
        if sentence[0] == ' ':
            sentence = sentence[1:]
        new_sentences.append(sentence)
    return new_sentences


def test_parser(texto:str, parser:nltk.parse, verbose:bool=False) -> list:
    '''
    Toma un texto y prueba el parser. Devuelve una lista de errores.
    Input:
        - texto, cadena con oraciones
        - parser, un objeto nltk para parsing semántico
        - verbose, booleano para imprimir detalles del proceso
    Output:
        - errores, lista de tuplas de la forma (num_oracion, estatus, error)
    ''' 
    errores = []
    formulas = []
    oraciones = preprocess_text(texto)
    for i, oracion in enumerate(oraciones):
        if verbose:
            print(f'Procesando \"{oracion}\"')
        tokens = oracion.split(' ')
        try:
            formula = utils.obtener_formula(tokens, parser)
            formulas.append(formula)
        except Exception as e:
            errores.append((i, oracion, e))
            formula = 'Fallo parser: ' + str(e) 
        if formula is None:
            errores.append((i, oracion, 'fallo parser'))
        else:
            if verbose:
                print(f'{oracion} => {formula}')
    if verbose:
        print(f'Porcentaje de aciertos: {(1 - len(errores)/len(oraciones))*100}% ({len(oraciones) - len(errores)}/{len(oraciones)})')
    return errores, formulas

                                 
def responde_pregunta(formulas_texto:nltk.sem.logic, pregunta:nltk.sem.logic, bk:LPQuery, verbose:bool=False):
    '''
    Toma una pregunta e intenta dar una respuesta
    Input:
        - formula_texto, una fórmula en nltk que se asume fundamentada.
        - pregunta_, una fórmula en nltk que se asume fundamentada y con un operador lambda.
        - bk, una base de conocimiento
        - verbose, booleano para imprimir detalles del proceso
    '''
    # ------------------------------------------
    # Verificamos representación de la pregunta 
    # ------------------------------------------
    variables = [v for v in list(pregunta.free())]
    assert(len(variables) >= 1), f'Error: se esperaba por lo menos una variable libre y se obtuvieron {len(variables)}'
    # ------------------------------------------
    # Encontramos constantes a partir de texto
    # ------------------------------------------
    M = Modelo()
    M.poblar_con(Ytoria(formulas_texto))
    # ------------------------------------------
    # Creamos la lista de candidatos
    # ------------------------------------------
    listas_candidatos = [obtener_candidatos(var, M) for var in variables]
    listas_tipos = [tipo_variable(var) for var in variables]
    listas_tipos = [[listas_tipos[i]]*len(listas_candidatos[i]) for i in range(len(variables))]
    listas_candidatos = list(product(*listas_candidatos))
    listas_tipos = list(product(*listas_tipos))
    respuestas = []
    for i, candidatos in enumerate(listas_candidatos):
        # ------------------------------------------------
        # Reemplazamos el candidato por la variable libre
        # ------------------------------------------------
        tipos = listas_tipos[i]
        formula = pregunta
        for j, candidato in enumerate(candidatos):
            if tipos[j] == 'bloque':
                var = 'x'
            elif tipos[j] == 'direccion':
                var = 'D'
            else:
                raise Exception('Algo raro con el tipo de variable', tipos[j])
            formula = lp.parse(fr'\{var}.{formula}({candidato})').simplify()
            formula = str(formula)
        if verbose:
            print(f'Candidato:\n\t{tuple([str(c) for c in candidatos])} => {formula}\n')
        # Verificamos implicación para la fórmula
        res = bk.ask(formula, verbose=False)
        if res == 'exito':
            respuestas.append(tuple([str(c) for c in candidatos]))
    return respuestas
            
    
def resuelve_preguntas(formulas_texto:nltk.sem.logic, preguntas:list, bk:LPQuery, verbose:bool=False) -> list:
    '''
    Intenta resolver una lista de preguntas sobre el texto
    Input:
        - formula_texto, una fórmula en nltk que se asume fundamentada.
        - preguntas, una lista de preguntas como fórmulas en nltk.
        - bk, una base de conocimiento
        - verbose, booleano para imprimir detalles del proceso
    '''
    # ------------------------------------
    # Intentamos responder cada pregunta
    # ------------------------------------
    intentos_respuestas = []
    for i, pregunta in enumerate(preguntas):
        if verbose:
            print(f'\nIntentando resolver la pregunta {i}\n')
        respuesta = responde_pregunta(formulas_texto=formulas_texto,\
                                      pregunta=pregunta,\
                                      bk=bk,\
                                      verbose=False)
        intentos_respuestas.append(respuesta)
        if verbose:
            if respuesta is not None:
                print(f'La respuesta a la pregunta {i} es:\n\t{respuesta}\n')
            else:
                print(f'No se encontró respuesta a la pregunta. {preguntas[i]}')
    return intentos_respuestas


def pipeline_responder_preguntas(text_data:dict, 
                                 gramatica_texto:str, 
                                 gramatica_preguntas:str, 
                                 bk:LPQuery,
                                 verbose:bool=True) -> tuple:
    '''
    Toma un texto, unas preguntas e intenta resolverlas. 
    Input:
        - text_data, un diccionario con las siguientes claves:
            * texto: una cadena con las oraciones
            * preguntas: una lista de cadenas con preguntas
            * respuestas: una lista de listas de cadenas con las respuestas posibles
        - gramatica_texto, cadena con el nombre de archivo de la gramática para 
                     hacer parsing del texto a DRT
        - gramatica_preguntas, cadena con el nombre de archivo de la gramática para 
                     hacer parsing de las preguntas al cálculo lambda
        - bk, una base de conocimiento
        - verbose, booleano para imprimir detalles del proceso
    Output:
        - respuestas, una lista con las respuestas a las preguntas
        - errores_parser, una lista con los errores del parser
    ''' 
    # ------------------------------------
    # Verificación de gramática del texto
    # ------------------------------------
    gramatica = FeatureGrammar.fromstring(gramatica_texto)
    parser = FeatureEarleyChartParser(gramatica)
    texto = text_data['texto']
    print(f'Verificando gramática para el texto...')
    errores_parser, formulas_texto = test_parser(texto, parser, verbose=verbose)
    if len(errores_parser) > 0:
        print('='*20)
        print('Errores parser')
        print('='*20)
        print(errores_parser)
        print('='*20)
        return None
    print('Gramática sin errores.')
    print('Continuamos con el procesamiento...')    
    print('')
    # ---------------------------------------
    # Verificación de gramática de preguntas
    # ---------------------------------------
    parser = load_parser(gramatica_preguntas, trace=0)
    preguntas = ' '.join(text_data['preguntas'])
    print(f'Verificando gramática para preguntas...')
    errores_parser, lista_preguntas = test_parser(preguntas, parser, verbose=verbose)
    if len(errores_parser) > 0:
        print('='*20)
        print('Errores parser')
        print('='*20)
        print(errores_parser)
        print('='*20)
        return None
    print('Gramática sin errores.')
    print('Continuamos con el procesamiento...')    
    print('')
    # ---------------------------------------
    # Representamos las preguntas
    # ---------------------------------------
    print('Intentamos resolver las preguntas...')
    intentos_respuestas = resuelve_preguntas(formulas_texto=formulas_texto,\
                                    preguntas=lista_preguntas,\
                                    bk=bk,\
                                    verbose=verbose)
    soluciones = text_data['respuestas']
    aciertos = []
    for i, pregunta in enumerate(text_data['preguntas']):
        print(f'La respuesta a la pregunta {pregunta} es {intentos_respuestas[i]}')
        respuesta = np.all([r in intentos_respuestas[i] for r in soluciones[i]])
        if respuesta:
            print('\t=> Respuesta correcta')
            aciertos.append(1)
        else:
            print('\t=> Respuesta incorrecta')
            print('Falta: ', [r for r in soluciones[i] if r not in intentos_respuestas[i]])
            aciertos.append(0)
    print(f'Porcentaje de aciertos: {np.mean(aciertos)*100}')


def tipo_variable(var):
    if var.name in ['x']:
        return 'bloque'
    elif var.name in ['D']:
        return 'direccion'
    else:
        raise Exception(f'¡El tipo de la variable {var.name} es desconocido!')
    

def obtener_candidatos(var, M):
    if var.name in ['x']:
        return M.entidades["individuo"]
    elif var.name in ['D']:
        return M.predicados
    else:
        raise Exception(f'¡El tipo de la variable {var.name} es desconocido!')
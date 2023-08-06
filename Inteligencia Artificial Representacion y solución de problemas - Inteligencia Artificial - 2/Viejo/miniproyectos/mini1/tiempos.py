from time import time, sleep
from tqdm.auto import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

def obtiene_tiempos(fun, args, num_it=10):
    tiempos_fun = []
    for i in range(num_it):
        arranca = time()
        x = fun(*args)
        para = time()
        tiempos_fun.append(para - arranca)
    return tiempos_fun

def compara_funciones(funs = None, arg = None, nombres = None, N=10):
    nms = []
    ts = []
    for i, fun in enumerate(funs):
        nms += [nombres[i] for x in range(N)]
        ts += obtiene_tiempos(fun, [arg], N)
    data = pd.DataFrame({'Función':nms, 'Tiempo':ts})
    return data

def compara_funciones_sobreargumentos(funs, args, nombres, N=10):
    data_list = []

    pbar = tqdm(total=len(funs), desc='\rComparando funciones', position=0, leave=True)

    for i, arg in enumerate(args):
        nms = []
        argumentos = []
        ts = []

        pbar2 = tqdm(total=len(funs), desc='\rProbando función seleccionada iter. {}'.format(i),
                     position=1,
                     leave=True)

        for i, fun in enumerate(funs):
            nms += [nombres[i] for x in range(N)]
            argumentos += [i for x in range(N)]
            ts += obtiene_tiempos(fun, [arg], N)

            pbar2.update()
            sleep(0.1)


        data_list.append(pd.DataFrame({'Función':nms, 'Num_argumento':argumentos, 'Tiempo':ts}))
        pbar.update()
        sleep(0.1)

    return pd.concat(data_list)




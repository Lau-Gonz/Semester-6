from ambientes import Wumpus
from agentes import HeroeUE
import utils

W = Wumpus(wumpus=(3,3), oro=(2,2), pozos=[(2,0), (3,1)])
agente = HeroeUE()

# Create episode
episodio = utils.Episode(environment=W,\
        agent=agente,\
        model_name='Baseline',\
        num_rounds=100)
# Run
episodio.run(verbose=4)
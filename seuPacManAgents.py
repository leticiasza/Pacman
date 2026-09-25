# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action) #simula a ação e devolve o estado resultante
        newPos = successorGameState.getPacmanPosition() #calcula a posição do Pac-Man depois de se mover
        newFood = successorGameState.getFood() #grid de verdadeiro ou falso das comidas que sobraram; newFood.asList() transforma em lista de posições
        newGhostStates = successorGameState.getGhostStates() #estado de cada fantasma (posição, assustado, direção)
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates] #tempo que resta do fantasma com medo. 0 = fantasma perigoso

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()


def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='3'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    def getAction(self, gameState: GameState):
        """Seu código vem aqui
        Adicione o código para minimax
        """

        def minimax(agentIndex=0, depth=0, state=gameState):
            # 1) Condição de parada: jogo acabou ou profundidade máxima atingida
            if state.isWin() or state.isLose() or depth == self.depth: #jogo acaba com vitória, derrota ou quando todas as rodadas permitidas já foram jogadas
                return self.evaluationFunction(state)

            # 2) Calcula o próximo agente e a próxima profundidade
            numAgents = state.getNumAgents()
            nextAgent = (agentIndex + 1) % numAgents #o % faz com quem o ciclo volte: após o último fanstama jogar vem o 0 e quando termina o ciclo a profundidade aumenta
            # a profundidade só aumenta quando o "ciclo" volta pro Pac-Man,
            # ou seja, quando o agente atual é o último fantasma
            if agentIndex == numAgents - 1:
                nextDepth = depth + 1 #calculo da próxima profundidade
            else:
                nextDepth = depth

            legalActions = state.getLegalActions(agentIndex)

            # Caso extremo: agente sem ações legais disponíveis
            if not legalActions:
                return self.evaluationFunction(state) #evita que max/min fiquem com +- infinito ou que bestAction  fique None numa chamada interna

            # 3) Turno do Pac-Man (agentIndex == 0), maximização
            if agentIndex == 0: #indice do Pac-Man é sempre 0
                bestValue = -float('inf') #cria uma variável -infinito para que o algoritmo possa fazer a comparação a fim de o código ache a maior nota entre as ações
                bestAction = None

                #simulação do quanto vale a pena seguir um caminho
                for action in legalActions: #passa por cada ação legal
                    successor = state.generateSuccessor(agentIndex, action) #simula o resultado que se daria se o agente (agentIndex) passasse por ali. não altera o estado do original
                    score = minimax(nextAgent, nextDepth, successor) #chama os próximos agentes, produndidades seguidamente para testar as ações deles
                    #Pac-Man maximiza, Fantasma minimiza

                    if score > bestValue:
                        bestValue = score      #Maximização. calcula a melhor movimentação depois guarda a pontuação e a ação
                        bestAction = action

                # Só retornamos a AÇÃO na chamada de nível mais externo
                # (quando estamos na profundidade 0, chamada original de getAction)
                if depth == 0: #Pac-Man só joga na depth == 0
                    return bestAction
                return bestValue

            # 4) Turno dos fantasmas (agentIndex > 0), minimização
            else:
                worstValue = float('inf') #cria uma variável infinito para que o algoritmo possa fazer a comparação a fim de o código ache a maior nota entre as ações

                for action in legalActions:
                    successor = state.generateSuccessor(agentIndex, action) #simula o resultado que se daria se o agente (agentIndex) passasse por ali. não altera o estado do original
                    score = minimax(nextAgent, nextDepth, successor) #chama os próximos agentes, produndidades seguidamente para testar as ações deles

                    if score < worstValue:
                        worstValue = score #Minimização

                return worstValue

        return minimax()


def betterEvaluationFunction(currentGameState: GameState): #coleta dos dados de cada uma das funções abaixo
    pos = currentGameState.getPacmanPosition()
    food = currentGameState.getFood().asList()
    ghostStates = currentGameState.getGhostStates()

    # Calcula a distância de Manhattan para a comida mais próxima
    foodDistances = [manhattanDistance(pos, f) for f in food] #calcula distância 
    if len(foodDistances) > 0:
        minFoodDistance = min(foodDistances)
    else:
        minFoodDistance = 0

    # Distância para o fantasma mais próximo
    ghostDistances = [manhattanDistance(pos, ghost.getPosition()) for ghost in ghostStates]
    minGhostDistance = min(ghostDistances)

    # Aumenta a pontuação se o fantasma estiver assustado, mas penaliza se estiver muito perto
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    if min(scaredTimes) > 0:
        minGhostDistance = 0  # Ignora fantasmas assustados

    return currentGameState.getScore() - (1.5 / (minFoodDistance + 1)) + (2 / (minGhostDistance + 1))


# Abbreviation
better = betterEvaluationFunction

import random
from Player import *
from Constants import *
from Construction import *
from Ant import *
from Move import *
from Building import *
from GameState import addCoords
from AIPlayerUtils import *
from Location import *
from Inventory import *
from GameState import *
##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Ben me up Scotty")
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        chosenMove = None
        chosenMoveList = []
        eval = 0.0
        moves = listAllLegalMoves(currentState)
        for move in moves:
            nextState = self.checkState(currentState, move)
            nextStateEval = self.examineState(nextState)
            if nextStateEval > eval:
                chosenMoveList[:] = []
                chosenMoveList.append(move)
                eval = nextStateEval
            elif nextStateEval == eval:
                chosenMoveList.append(move)
        #Return the chosen move
        if chosenMoveList == []:
            randDir = random.randint(0, len(moves)-1)
            chosenMove = moves[randDir]
        else:
            randDir = random.randint(0, len(chosenMoveList)-1)
            chosenMove = chosenMoveList[randDir]
        return chosenMove

    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    #Clones the current state and returns the next state based on a given move
    #Return - Gamestate
    def checkState(self, currentState, currMove):
        #make a clone of the current State
        nextState = currentState.clone()
        #Apply Our Move
        #If we have a MOVE_ANT moveType
        if currMove.moveType == MOVE_ANT:
            startCoord = currMove.coordList[0]
            endCoord = currMove.coordList[-1]
            #take ant from start coord
            antToMove = nextState.board[startCoord[0]][startCoord[1]].ant
            #change ant's coords and hasMoved status
            antToMove.coords = (endCoord[0], endCoord[1])
            antToMove.hasMoved = True
            #remove ant from location
            nextState.board[startCoord[0]][startCoord[1]].ant = None
            #put ant at last loc in coordList
            nextState.board[endCoord[0]][endCoord[1]].ant = antToMove
        #If we have a BUILD moveType
        elif currMove.moveType == BUILD:
            coord = currMove.coordList[0]
            currentPlayerInv = nextState.inventories[nextState.whoseTurn]
            #subtract the cost of the item from the player's food count
            if currMove.buildType == TUNNEL:
                currentPlayerInv.foodCount -= CONSTR_STATS[currMove.buildType][BUILD_COST]
                tunnel = Building(coord, TUNNEL, nextState.whoseTurn)
                nextState.board[coord[0]][coord[1]].constr = tunnel
            else:
                currentPlayerInv.foodCount -= UNIT_STATS[currMove.buildType][COST]
                ant = Ant(coord, currMove.buildType, nextState.whoseTurn)
                ant.hasMoved = True
                nextState.board[coord[0]][coord[1]].ant = ant
                nextState.inventories[nextState.whoseTurn].ants.append(ant)
        elif currMove.moveType == END:
            return nextState

        return nextState

    #Examines a given state and assigns a score from 0.0 - 1.0 to that state
    #return - float
    def examineState(self, currentState):
        eval = 0.5
        #Win/Loss Statements
        enemyTurn = 0
        if(currentState.whoseTurn == 0):
            enemyTurn = 1
        if self.checkGameOver(currentState, enemyTurn) == True or self.checkGameOver(currentState, currentState.whoseTurn):
            return 0.0
        elif self.checkGameOver(currentState, currentState.whoseTurn) == True or self.checkGameOver(currentState, enemyTurn) == False:
            return 1.0

        #Get both players inventories
        myInv = None
        oInv = None
        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                myInv = inv
            else:
                oInv = inv

        #add .1 for each worker ant, maximize benefit at two workers
        numWorkers = self.getNumAntType(myInv, WORKER)
        if (numWorkers <= 2):
            eval += numWorkers * 0.1
        else:
            eval += 0.2

        #add .05 for each worker carrying food
        for ant in myInv.ants:
            if ant.type == WORKER and ant.carrying:
                eval += 0.05

        #add different in health of your queen and enemy queen
        eval += (myInv.getQueen().health - oInv.getQueen().health)

        #add total value of ants on each side and add the difference
        for ant in myInv.ants:
            eval += 0.1 * ant.type
        for ant in oInv.ants:
            eval -= 0.1 * ant.type

        #add difference in amount of food
        eval += 0.1 * (myInv.foodCount - oInv.foodCount)
        if eval >= 1.0:
            eval = 0.9
        return eval

    #############################
    ##                          #
    ##      HELPER METHODS      #
    ##                          #
    #############################

    ##checkGameOver
    #False == Loss
    #True == Win
    #None == inconclusive
    def checkGameOver(self, currentState, myTurn):
        queen = getCurrPlayerQueen(currentState)
        #If our queen is dead, we lost
        if queen == None:
            return False
        #if we have 11 food we won
        for inv in currentState.inventories:
            if inv.player == myTurn and inv.foodCount == 11:
                return True
        return None

    ##getNumAnt
    #returns number of a specific type of ant - int
    def getNumAntType(self, inv, antType):
        antCount = 0
        for ant in inv.ants:
            if ant.type == antType:
                antCount += 1
        return antCount

    #returns the Food Coordinates [(int,int)]
    def getFoodCoords(self, currentState):
        coords = []
        for i in range(0,10):
            for j in range(0,4):
                if currentState.board[i][j].constr is not None and currentState.board[i][j].constr.type == FOOD:
                    coords.append((i,j))
        return coords

    #Calculates how close we are to either the food or anthill depending on WORKER carrying status
    #Return evaluation - float
    def evalDistToObj(self, currentState, antNumber):
        ants = []
        for ant in getCurrPlayerInventory(currentState).ants:
            if ant == WORKER:
                ants.append((ant.coords))
        if ants[antNumber].carrying == False:
            return (1 - (stepsToReach(currentState, ants[antNumber], self.getFoodCoords[antNumber])/10))
        if ants[0].carrying == True:
            return (1 - (stepsToReach(currentState, ants[antNumber], getCurrPlayerInventory(currentState).getAnthill)/10))
        return 0.0


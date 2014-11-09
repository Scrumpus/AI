import random
import unittest
from Location import *
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import *
from Building import *
from AIPlayerUtils import *
from GameState import *

##
#Source for Homework 4 recieved from Bobby Stiles since neither Scott
#nor I had homework 4 that worked to our satisfaction

##
#AIPlayer
#Description: The responsibility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    depthLimit = 3

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        #PLEASE NOTE: If you see this comment and this AI is called "Food Gatherer: ____"
        #When you are renaming the AI you must continue to call it Food Gatherer if you
        #continue the dual goal of gathering food as fast as possible AND having offensive
        #units attack the enemy as fast as possible, then you must continue to call it
        #"Food Gatherer".  Simply give it a new subtitle.
        super(AIPlayer, self).__init__(inputPlayerId, "Agent Sack-Belch-Pew")

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
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            moves = []
            for i in range(0, 11):
                move = None
                while move is None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr = True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   # stuff on foe's side
            moves = []
            for i in range(0, 2):
                move = None
                while move is None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr = True
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
        return self.depthLimitedSearch(currentState, currentState.whoseTurn, 0, Node(None, currentState, None, None))

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

    ##
    #depthLimitedSearch
    #Description: Find the best move to make given a state of the game
    #
    #Parameters:
    #   state - The state of the board to evaluate
    #   playerID - The ID of the player whose turn it is
    #   currDepth - How far into the tree we currently are
    #   currNode - The current parent node we are expanding
    ##
    def depthLimitedSearch(self, state, playerID, currDepth, currNode):
        if currDepth == self.depthLimit:
            return self.evalGameState(currNode.state)

        moves = listAllLegalMoves(state)
        currEval = self.evalGameState(state.fastclone())

        nodeList = []
        for move in moves:
            nextState = self.getNextState(state, move)

            # for ant in nextState.inventories[state.whoseTurn].ants:
            #     ant.hasMoved = False

            # nextState.whoseTurn = playerID
            node = Node(move, nextState, None, currNode)
            node.eval = self.evalGameState(node.state)

            # Only expand a node if it's score is above the threshold
            # As we get closer to victory, our scores get higher, so add a
            # fraction of the current state evaluation to account for this
            if node.state.whoseTurn is self.playerId:
                if node.eval > max(0.70, currEval + (currEval / 25)):
                    node.eval = self.depthLimitedSearch(nextState, playerID, currDepth + 1, node)
            else:
                if node.eval < min(0.30, currEval + (currEval / 25)):
                    node.eval = self.depthLimitedSearch(nextState, playerID, currDepth + 1, node)
            nodeList.append(node)

        # If we're at the root node, return the best move rather than the average score
        if currDepth == 0:
            return (self.bestMoveInNodeList(nodeList)).move
        else:
            if state.whoseTurn is self.playerId:
                extreme = self.bestMoveInNodeList(nodeList)
            else:
                extreme = self.worstMoveInNodeList(nodeList)
            return extreme.eval

    ##
    #bestMoveInNodeList
    #Description: Given a list of nodes, find the move that results in the highest
    #evaluation score.
    #
    #Parameters:
    #   nodeList - The list of nodes we are looking for the best move in
    ##
    def bestMoveInNodeList(self, nodeList):
        bestMove = None
        highestScore = 0.0

        for node in nodeList:
            if node.eval > highestScore:
                bestMove = node
                highestScore = node.eval

        return bestMove

    ##
    #worstMoveInNodeList
    #Description: Given a list of nodes, find the move that results in the lowest
    #evaluation score.
    #
    #Parameters:
    #   nodeList - The list of nodes we are looking for the best move in
    ##
    def worstMoveInNodeList(self, nodeList):
        worstMove = None
        lowestScore = 99999.0

        for node in nodeList:
            if node.eval < lowestScore:
                worstMove = node
                lowestScore = node.eval

        return worstMove

    ##
    #getNextState
    #Desctription: Given a move, figure out how that move would affect the state
    #and return that changed state.
    #
    #Parameters:
    #   currentState - The current state of the game
    #   move - The move chosen that could change the currentState
    #
    #Return: A copy of the currentState after it has been changed by the move
    ##
    def getNextState(self, currentState, move):
        returnState = currentState.fastclone()

        #check move type
        if move.moveType == MOVE_ANT:
            startCoord = move.coordList[0]
            endCoord = move.coordList[-1]

            #take ant from start coord
            antToMove = getAntAt(returnState, startCoord)
            #if the ant is null, return
            if antToMove is None:
                return returnState

            #change ant's coords and hasMoved status
            antToMove.coords = (endCoord[0], endCoord[1])
            antToMove.hasMoved = True

        elif move.moveType == BUILD:
            coord = move.coordList[0]
            currentPlayerInv = returnState.inventories[returnState.whoseTurn]

            #subtract the cost of the item from the player's food count
            if move.buildType == TUNNEL:
                currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

                tunnel = Building(coord, TUNNEL, returnState.whoseTurn)
                returnState.inventories[returnState.whoseTurn].constrs.append(tunnel)
            else:
                currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]

                ant = Ant(coord, move.buildType, returnState.whoseTurn)
                ant.hasMoved = True
                returnState.inventories[returnState.whoseTurn].ants.append(ant)

        elif move.moveType == END:
            #take care of end of turn business for ants and contructions
            for ant in returnState.inventories[returnState.whoseTurn].ants:
                constrUnderAnt = getConstrAt(returnState, ant.coords)
                if constrUnderAnt is not None:
                    #if constr is enemy's and ant hasn't moved, affect capture health of buildings
                    if type(constrUnderAnt) is Building and not ant.hasMoved and not constrUnderAnt.player == returnState.whoseTurn:
                        constrUnderAnt.captureHealth -= 1
                        if constrUnderAnt.captureHealth == 0 and constrUnderAnt.type != ANTHILL:
                            constrUnderAnt.player = returnState.whoseTurn
                            constrUnderAnt.captureHealth = CONSTR_STATS[constrUnderAnt.type][CAP_HEALTH]
                    #have all worker ants on food sources gather food
                    elif constrUnderAnt.type == FOOD and ant.type == WORKER:
                        ant.carrying = True
                    #deposit carried food (only workers carry)
                    elif (constrUnderAnt.type == ANTHILL or constrUnderAnt.type == TUNNEL) and ant.carrying:
                        returnState.inventories[returnState.whoseTurn].foodCount += 1
                        ant.carrying = False

                #reset hasMoved on all ants of player
                ant.hasMoved = False

            #set the turn to the opponent's move
            returnState.whoseTurn = 1 - returnState.whoseTurn

        return returnState

    ##
    #evalGameState
    #
    #Evaluates the current state of the game and returns a numerical (double) representation of
    #both opponents current success in the game.
    #
    #Parameters:
    #    currentState - A clone of the current state of the game board (GameState)
    ##
    def evalGameState(self, currentState):
        myInv = None
        enemyInv = None
        stateVal = 0.35

        #get our/the enemy's inventory
        for inv in currentState.inventories:
            if inv.player == self.playerId:
                myInv = inv
            elif inv.ants is not None and len(inv.ants) != 0:
                enemyInv = inv

        #first things first, get all the automatic wins/losses out of the way.
        #CASE 1: Loss of a queen
        if myInv.getQueen() is None:
            return 0.0 #Enemy wins
        elif enemyInv.getQueen() is None:
            return 1.0 #Our win!
        #CASE 2: reaching a foodCount of 11
        elif myInv.foodCount == 11:
            return 1.0 #Our win!
        elif enemyInv.foodCount == 11:
            return 0.0 #enemy winn
        #CASE 3: occupying an anthill
        if myInv.getAnthill().captureHealth == 0:
            return 0.0 #we lose
        elif enemyInv.getAnthill().captureHealth == 0:
            return 1.0 #we win!

        numWorkers = self.getNumOfAntType(myInv, WORKER)
        if numWorkers > 1:
            stateVal -= 0.07 * numWorkers
        else:
            stateVal += 0.035 * numWorkers

        numDrones = self.getNumOfAntType(myInv, DRONE)
        if numDrones > 2:
            stateVal -= 0.07 * numDrones
        else:
            stateVal += 0.035 * numDrones

        foodCoords = self.getFoodCoords(currentState)

        if self.getNumOfAntType(myInv, R_SOLDIER) != 0 and self.getNumOfAntType(myInv, SOLDIER) != 0:
            stateVal -= 0.2

        for ant in myInv.ants:
            if ant.type == QUEEN:
                # We do not want the queen on the anthill or our food
                if ant.coords == myInv.getAnthill().coords or ant.coords in foodCoords:
                    stateVal -= 0.1
                # Keep the queen on the player's side of the field
                stateVal -= ant.coords[1]*0.03
            elif ant.type == WORKER:
                    stateVal += self.getWorkerMoveVal(currentState, myInv, foodCoords, ant)
            elif ant.type == DRONE:
                    stateVal += self.getDroneMoveVal(currentState, enemyInv, ant)

        stateVal += float(myInv.foodCount) * 0.02

        if stateVal > 0.998:
            print "Evaluating state to: ", stateVal
        return min(0.998, round(stateVal, 3))

    ##
    #getWorkerMoveVal
    #Description: Get the evaluation score for a given worker ant.
    #Their goal is to gather food as fast as possible.
    #
    ##
    def getWorkerMoveVal(self, currentState, myInv, foodCoords, ant):
        # If the worker is carrying food
        returnVal = 0.00
        if ant.carrying:
            tempHillDist = stepsToReach(currentState, ant.coords, myInv.getAnthill().coords)
            # Assume for now we only have one tunnel
            tempTunnelDist = stepsToReach(currentState, ant.coords, myInv.getTunnels()[0].coords)

            if tempHillDist < tempTunnelDist:
                returnVal = stepsToReach(currentState, ant.coords, myInv.getAnthill().coords)
            else:
                returnVal = stepsToReach(currentState, ant.coords, myInv.getTunnels()[0].coords)

            if ant.coords in foodCoords:
                returnVal -= 0.025
        # If the worker is not carrying food
        else:
            distList = []
            for foodCoord in foodCoords:
                distList.append(stepsToReach(currentState, ant.coords, foodCoord))
            returnVal = min(distList)

            if ant.coords == myInv.getAnthill().coords or ant.coords == myInv.getTunnels()[0].coords:
                returnVal -= 0.025

        return (10.0-float(returnVal)) / 80.0

    ##
    #getDroneMoveVal
    #Description: Get the evaluation score for a given drone ant.
    #Their goal is to kill the enemy queen as fast as possible.
    ##
    def getDroneMoveVal(self, currentState, oInv, ant):
        returnVal = 0.0
        # Find which one of the enemy's ants is closest
        goalCoords = oInv.getQueen().coords
        #goalCoords = self.getNearestEnemy(currentState, ant.coords, UNIT_STATS[DRONE][RANGE], oInv)
        if goalCoords is None and ant.hasMoved:
            return 0.125
        elif goalCoords is None:
            return returnVal

        returnVal = stepsToReach(currentState, ant.coords, goalCoords)
        if returnVal == 0:
            return 0.0
        else:
            return (10.0-float(returnVal)) / 80.0

    ##
    #getNearestEnemy
    #Desciption: Get the location of the nearest enemy ant to a given set of coordinates
    #There is assumed to be a player's ant located at the given set of coordinates.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #   startCoords - The coordinates that we are determing which enemy ant is closest to.
    #   attackRange - The range of attack of the ant located at startCoords.
    #   oInv - The object representation of the opponent's inventory.
    #
    #Return: The coordinates of the nearest enemy ant
    ##
    def getNearestEnemy(self, currentState, startCoords, attackRange, oInv):
        minDist = 50
        goalCoords = None
        # Find which one of the enemy's ants in closest
        for oAnt in oInv.ants:
            dist = stepsToReach(currentState, startCoords, oAnt.coords)
            if dist < minDist:
                minDist = dist
                goalCoords = oAnt.coords
            # If the enemy ant is in the attack range, return None to
            # tell the calling method that the ant should stay where it is
            if minDist == attackRange:
                return None
        return goalCoords

    ##
    #getNumOfAntType
    #Description: Get the number of ants of a given type in a given inventory.
    #
    #Parameters:
    #   inv - The inventory we are searching through
    #   antType - The type of ant we are looking for
    #
    #Return: The number of ants found
    ##
    def getNumOfAntType(self, inv, antType):
        antCount = 0
        for ant in inv.ants:
            if ant.type == antType:
                antCount += 1
        return antCount

    ##
    #getFoodCoords
    #Description: Get the coordinates of all the player's food items on the board
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #
    #Return: The list of the two coordinates that signify the location of the food on the player's
    #   side of the field.
    ##
    def getFoodCoords(self, currentState):
        coords = []
        for i in range(0, 10):
            for j in range(0, 4):
                if getConstrAt(currentState, (i, j)) is not None and getConstrAt(currentState, (i, j)).type == FOOD:
                    coords.append((i, j))
        return coords

    ##
    #evalNodes
    #Description: Given a list of nodes, calculate and return their average score
    #
    #Parameters:
    #   nodeList - The list of nodes we are evaluating
    #
    #Return: The average of all the nodes evaluation scores
    ##
    def evalNodes(self, nodeList):
        returnVal = 0.0
        numNodes = len(nodeList)

        for node in nodeList:
            returnVal += node.eval

        return returnVal/float(numNodes)

##
#Node
#Description: The small class representing a node
##
class Node(object):
    move = None
    state = None
    eval = None
    parentNode = None

    def __init__(self, _move, _state, _eval, _parentNode):
        self.move = _move
        self.state = _state.fastclone()
        self.eval = _eval
        self.parentNode = _parentNode

##
#AITests
#Description: The unit test class for this AIPlayer class
##
class AITests(unittest.TestCase):
    state = None
    p1Inventory = None
    p2Inventory = None

    ##
    #setUp
    #
    #Description: This method is called at the start of every time to do any necessary setup
    #for the tests to work.
    ##
    def setUp(self):
        board = [[Location((col, row)) for row in xrange(0, BOARD_LENGTH)] for col in xrange(0, BOARD_LENGTH)]
        #Initialize all the ants
        p1Queen = Ant((1, 0), QUEEN, PLAYER_ONE)
        p2Queen = Ant((1, 8), QUEEN, PLAYER_TWO)
        p1Worker1 = Ant((0, 3), WORKER, PLAYER_ONE)
        p2Worker1 = Ant((4, 6), WORKER, PLAYER_TWO)
        p1Worker2 = Ant((6, 2), WORKER, PLAYER_ONE)
        p1Worker2.carrying = True
        p2Worker2 = Ant((6, 7), WORKER, PLAYER_TWO)
        p1Drone1 = Ant((4, 5), DRONE, PLAYER_ONE)
        p1Drone2 = Ant((2, 3), DRONE, PLAYER_ONE)
        p1Ants = [p1Queen, p1Worker1, p1Worker2, p1Drone1, p1Drone2]
        p2Ants = [p2Queen, p2Worker1, p2Worker2]

        #Initialize all the constructions
        p1Anthill = Building((1, 1), ANTHILL, PLAYER_ONE)
        p2Anthill = Building((1, 8), ANTHILL, PLAYER_TWO)
        p1Tunnel = Building((6, 2), TUNNEL, PLAYER_ONE)
        p2Tunnel = Building((7, 8), TUNNEL, PLAYER_TWO)

        allFood = [Construction((0, 3), FOOD), Construction((5, 2), FOOD), Construction((2, 8), FOOD), Construction((6, 7), FOOD)]

        #Populate the players' inventories
        self.p1Inventory = Inventory(PLAYER_ONE, p1Ants, [p1Anthill, p1Tunnel], 2)
        self.p2Inventory = Inventory(PLAYER_TWO, p2Ants, [p2Anthill, p2Tunnel], 2)
        nInventory = Inventory(NEUTRAL, [], allFood, 0)

        #Put the ants on the board
        for ant in p1Ants:
            board[ant.coords[0]][ant.coords[1]].ant = ant
        for ant in p2Ants:
            board[ant.coords[0]][ant.coords[1]].ant = ant
        #Put the constructs on the board
        for construct in self.p1Inventory.constrs:
            board[construct.coords[0]][construct.coords[1]].constr = construct
        for construct in self.p2Inventory.constrs:
            board[construct.coords[0]][construct.coords[1]].constr = construct
        #Put the food on the board
        for food in allFood:
            board[food.coords[0]][food.coords[1]].constr = food

        self.state = GameState(board, [self.p1Inventory, self.p2Inventory, nInventory], PLAY_PHASE, PLAYER_ONE)

    ##
    #testAnthillLoc
    #
    #Description: Very simple test to confirm that the anthills are where we expect them
    ##
    def testAnthillLoc(self):
        self.assertTrue(getConstrAt(self.state, (1, 8)) is not None and getConstrAt(self.state, (1, 8)).type == ANTHILL)
        self.assertTrue(getConstrAt(self.state, (1, 1)) is not None and getConstrAt(self.state, (1, 1)).type == ANTHILL)

    ##
    #testSameAntType
    #
    #Description: Very simple test to confirm that two ants located at different points are the same type
    ##
    def testSameAntType(self):
        self.assertEqual(getAntAt(self.state, (0, 3)).type, getAntAt(self.state, (6, 2)).type)
        self.assertEqual(getAntAt(self.state, (4, 6)).type, getAntAt(self.state, (6, 7)).type)

    ##
    #testStayStillMove
    #
    #Description: Give the getNextState method a move where the ant does not actually move any spaces
    #and confirm that the new state reflects that, but still registers that the ant has technically moved
    ##
    def testStayStillMove(self):
        antCoords = self.p1Inventory.ants[0].coords
        move = Move(MOVE_ANT, [antCoords], None)
        player = AIPlayer(1)
        newState = player.getNextState(self.state, move)
        val = player.evalGameState(newState)

        self.assertEqual(getAntAt(newState, (antCoords[0], antCoords[1])).coords, antCoords)
        self.assertTrue(getAntAt(newState, (antCoords[0], antCoords[1])).hasMoved)
        # Make sure the new state has the value we expect
        self.assertEqual(val, 0.67)

    ##
    #testFoodPickUpAndDrop
    #
    #Description: Make sure that the worker on top of the food has picked up the food at the end
    #of the turn, and the worker on the tunnel has dropped its food.
    ##
    def testFoodPickUpAndDrop(self):
        move = Move(END, None, None)
        player = AIPlayer(1)
        newState = player.getNextState(self.state, move)
        val = player.evalGameState(newState)

        self.assertTrue(getAntAt(newState, (6, 2)).carrying is False)
        self.assertTrue(getConstrAt(newState, (0, 3)).type == FOOD)
        self.assertTrue(getAntAt(newState, (0, 3)).carrying)
        # Make sure the new state has the value we expect
        self.assertEqual(val, 0.641)

    ##
    #testBuildingDroneWhenHillOccupied
    #
    #Description: Make sure unable to build drone when hill is occupied
    ##
    def testBuildingDroneWhenHillOccupied(self):
        oldAntArray = self.p1Inventory.ants
        hill = self.p1Inventory.getAnthill()
        #move queen to block anthill
        move1 = Move(MOVE_ANT, [(1,0), (1,1)], None)
        move2 = Move(BUILD, [hill.coords], DRONE)
        player = AIPlayer(1)

        newState = player.getNextState(self.state, move1)
        newState2 = player.getNextState(newState, move2)

        val = player.evalGameState(newState)

        #since unable to build drone, old array should be same as new array
        self.assertTrue(oldAntArray, newState2.inventories[newState2.whoseTurn].ants)
        self.assertEqual(val, 0.54)

    ##
    #tearDown
    #
    #Description: This method comes with the Python unittest and is called after
    #every successful test.
    ##
    def tearDown(self):
        print "Test passed!"

if __name__ == '__main__':
    unittest.main()

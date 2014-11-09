# -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from AIPlayerUtils import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords

#Constants used for the findTile helper method
LOOKING_FOR_CONSTR = 0
LOOKING_FOR_ANT = 1

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
    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__ (self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "AI Player HW2: Food Gatherer+")

    ##
    #getPlacement
    #Description: The getPlacement method corresponds to the
    #action taken on setup phase 1 and setup phase 2 of the game.
    #In setup phase 1, the AI player will be passed a copy of the
    #state as currentState which contains the board, accessed via
    #currentState.board. The player will then return a list of 10 tuple
    #coordinates (from their side of the board) that represent Locations
    #to place the anthill and 9 grass pieces. In setup phase 2, the player
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent’s side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of eleven 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x11,y11)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        if currentState.phase == SETUP_PHASE_1:
            return [(1, 0), (7, 2), (0, 3), (1, 3), (2, 3), (3, 2), (5, 0), (7, 3), (8, 3), (9, 3), (9, 0)]
        elif currentState.phase == SETUP_PHASE_2:
            moves = []
            foundOne = False
            oAntHill = oTunnel = (-1, -1)
            # Look for the opponent's anthill and tunnel and save the coordinates.
            # Once both are found, break from the loop.
            for i in range(0, 10):
                for j in range(6, 10):
                    if currentState.board[i][j].constr is not None and currentState.board[i][j].constr.type == ANTHILL:
                        oAntHill = (i, j)
                        if foundOne:
                            break
                        else:
                            foundOne = True
                    if currentState.board[i][j].constr is not None and currentState.board[i][j].constr.type == TUNNEL:
                        oTunnel = (i, j)
                        if foundOne:
                            break
                        else:
                            foundOne = True

            sumDist = xFoodCoord = yFoodCoord = -1

            # Find the longest shortest path to any spot
            # to maximize how far ants have to go to get the food
            for i in range(0, 10):
                for j in range(6, 10):
                    if currentState.board[i][j].constr is not None: continue

                    tempSumDist = stepsToReach(currentState, oAntHill, (i, j)) + stepsToReach(currentState, oTunnel, (i, j))

                    if tempSumDist > sumDist:
                        sumDist = tempSumDist
                        xFoodCoord = i
                        yFoodCoord = j

            moves.append((xFoodCoord, yFoodCoord))
            # Save the coordinates of the first food so we don't assign the same spot
            # And reset distance variable
            firstFoodX = xFoodCoord
            firstFoodY = yFoodCoord
            sumDist = -1
            # Now do it again for the second piece of food
            # This is horrifyingly inefficient but it works for now
            for i in range(0, 10):
                for j in range(6, 10):
                    if currentState.board[i][j].constr is not None: continue

                    tempSumDist = stepsToReach(currentState, oAntHill, (i, j)) + stepsToReach(currentState, oTunnel, (i, j))

                    if tempSumDist > sumDist and (firstFoodX != i and firstFoodY != j):
                        sumDist = tempSumDist
                        xFoodCoord = i
                        yFoodCoord = j

            moves.append((xFoodCoord, yFoodCoord))
            return moves
        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: The getMove method corresponds to the play phase of the game
    #and requests from the player a Move object. All types are symbolic
    #constants which can be referred to in Constants.py. The move object has a
    #field for type (moveType) as well as field for relevant coordinate
    #information (coordList). If for instance the player wishes to move an ant,
    #they simply return a Move object where the type field is the MOVE_ANT constant
    #and the coordList contains a listing of valid locations starting with an Ant
    #and containing only unoccupied spaces thereafter. A build is similar to a move
    #except the type is set as BUILD, a buildType is given, and a single coordinate
    #is in the list representing the build location. For an end turn, no coordinates
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):
        #Get both players inventories
        myInv = None
        oInv = None
        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                myInv = inv
            else:
                oInv = inv
        #If my inventory is still none, then I don't have one.
        if myInv is None:
            return Move(END, None, None)

        # Save the anthill
        aHill = myInv.getAnthill()
        # If the worker has died, build another one if we have the resources
        if (currentState.board[aHill.coords[0]][aHill.coords[1]].ant is None and self.getNumOfAntType(myInv, WORKER) == 0
                and myInv.foodCount >= UNIT_STATS[WORKER][COST]):
            return Move(BUILD, [aHill.coords], WORKER)

        # Keep at least one ranged soldier on the field at all times
        if (currentState.board[aHill.coords[0]][aHill.coords[1]].ant is None and self.getNumOfAntType(myInv, R_SOLDIER) == 0
                and myInv.foodCount >= UNIT_STATS[R_SOLDIER][COST]):
            return Move(BUILD, [aHill.coords], R_SOLDIER)

        # Find the first ant that needs moving
        ant = None
        for tempAnt in myInv.ants:
            if not tempAnt.hasMoved:
                ant = tempAnt
                break
        if ant is None:
            return Move(END, None, None)

        # Find where the food is on the player's side of the board
        foodCoords = self.getFoodCoords(currentState)

        # If the ant is the queen, just make sure it's not on the anthill
        if ant.type == QUEEN:
            return self.getQueenMove(currentState, foodCoords, ant, aHill)
        # If the ant is a worker
        if ant.type == WORKER:
            return self.getWorkerMove(currentState, myInv, foodCoords, ant)
        # If the ant is a ranged soldier
        if ant.type == R_SOLDIER:
            return self.getRangedMove(currentState, oInv, ant)

        return Move(END, None, None)

    ##
    #getQueenMove
    #Description: Get the move that the queen should perform this turn.
    #The queen is primarily concerned with staying off the anthill and food
    ##
    def getQueenMove(self, currentState, foodCoords, ant, aHill):
        if ant.coords == aHill.coords:
            # Get all legal moves for the queen and pick one randomly to do
            moves = listAllMovementPaths(currentState, ant.coords, UNIT_STATS[QUEEN][MOVEMENT])
            move = random.choice(moves)

            # Do not let the queen move onto a piece of food and possibly block a worker
            while True:
                notOnFood = True
                for foodCoord in foodCoords:
                    if foodCoord == move[len(move)-1]:
                        notOnFood = False
                if notOnFood: break
                else: move = random.choice(moves)

            return Move(MOVE_ANT, move, None)
        # If the queen is already not on the hill, it's fine where it is
        return Move(MOVE_ANT, [ant.coords], None)

    ##
    #getWorkerMove
    #Description: Get the move that a given worker should perform this turn.
    #The worker should be solely concerned with gathering food as quickly
    #as possible.
    ##
    def getWorkerMove(self, currentState, myInv, foodCoords, ant):
        moves = listAllMovementPaths(currentState, ant.coords, UNIT_STATS[WORKER][MOVEMENT])
        minDist = 50
        bestMove = None
        # If the worker is carrying food
        if ant.carrying:
            # For each move available to the ant 
            for move in moves:
                # Find the move that brings the ant closest to the anthill or tunnel
                coord = move[len(move)-1]
                tempHillDist = stepsToReach(currentState, coord, myInv.getAnthill().coords)
                # Assume for now we only have one tunnel
                tempTunnelDist = stepsToReach(currentState, coord, myInv.getTunnels()[0].coords)

                if tempHillDist < tempTunnelDist and tempHillDist < minDist:
                    minDist = tempHillDist
                    bestMove = move
                elif tempTunnelDist < tempHillDist and tempTunnelDist < minDist:
                    minDist = tempTunnelDist
                    bestMove = move
                # If we've found the hill or tunnel, don't bother looking at other moves
                if minDist == 0:
                    break
            return Move(MOVE_ANT, bestMove, None)
        # If the worker is not carrying food
        else:
            # For each move available to the ant
            for move in moves:
                # If the last coordinate in the set of movements is a food tile, take that move
                coord = move[len(move)-1]
                # Find which of the food items is closest and focus on that one
                distList = []
                for foodCoord in foodCoords:
                    distList.append(stepsToReach(currentState, coord, foodCoord))
                closestFood = min(distList)
                # If this move has the closest route to one of the food items, pick this move
                if closestFood < minDist:
                    minDist = closestFood
                    bestMove = move
                # If we've found the food, don't bother looking at other moves
                if minDist == 0:
                    break
            return Move(MOVE_ANT, bestMove, None)

    ##
    #getRangedMove
    #Description: Get the move that a ranged soldier should perform this turn.
    #The ranged soldier find the closest enemy ant and goes to attack it.
    def getRangedMove(self, currentState, oInv, ant):
        moves = listAllMovementPaths(currentState, ant.coords, UNIT_STATS[R_SOLDIER][MOVEMENT])
        minDist = 50
        goalCoords = None
        # Find which one of the enemy's ants in closest
        for oAnt in oInv.ants:
            dist = stepsToReach(currentState, ant.coords, oAnt.coords)
            if dist < minDist:
                minDist = dist
                goalCoords = oAnt.coords
            # If the enemy ant will be within attacking range, stay and attack
            if minDist < 3:
                return Move(MOVE_ANT, [ant.coords], None)

        minDist = 50
        bestMove = None
        # Find which valid move will take this ant closest to the goal coords
        for move in moves:
            coord = move[len(move)-1]
            dist = stepsToReach(currentState, coord, goalCoords)
            if dist < minDist:
                minDist = dist
                bestMove = move
            # If the move gets us within attacking range, take that move
            if minDist == 2: break

        return Move(MOVE_ANT, bestMove, None)

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
                if currentState.board[i][j].constr is not None and currentState.board[i][j].constr.type == FOOD:
                    coords.append((i, j))
        return coords

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
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes
    #a move and has a valid attack. It is assumed that an attack will always be made
    #because there is no strategic advantage from withholding an attack. The AIPlayer
    #is passed a copy of the state which again contains the board and also a clone of
    #the attacking ant. The player is also passed a list of coordinate tuples which
    #represent valid locations for attack. Hint: a random AI can simply return one of
    #these coordinates for a valid attack.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e.
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply
    #indicates to the AI whether it has won or lost the game. This is to help with
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)

    def registerWin(self, hasWon):
        #method template, not implemented
        pass

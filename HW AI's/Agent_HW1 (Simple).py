  # -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#the getPlacement and getMove or the original AI have been modified. The anthill
#is now place in the back corner and the grass is placed closest to the enemy. Worker ants
#move about their own territory and soldier ants move toward the enemy territory. I was
#unable to successfully make the worker ants pick up and drop off adjacent food.
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
        super(AIPlayer,self).__init__(inputPlayerId, "Winfred")
    
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
    #Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        numtoPlace = 0
        #place anthill, tunnel, and grass on your side
        if currentState.phase == SETUP_PHASE_1:
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Place anthill on back left or right corner randomly
                    if i == 0:
                        x = random.randint(0,1)
                        if x == 0:
                            if currentState.board[0][0].constr == None and (0,0) not in moves:
                                move = (0, 0)
                                currentState.board[0][0].constr == True
                        else:
                            if currentState.board[9][0].constr == None and (0,0) not in moves:
                                move = (9,0)
                                currentState.board[9][0].constr == True
                                
                    #randomly place tunnel, but not at closest row to enemy
                    elif i == 1:
                        x = random.randint(0,9)
                        y = random.randint(0,2)
                        if currentState.board[x][y].constr == None and (x,y) not in moves:
                            move = (x,y)
                            currentState.board[x][y].constr == True
                            
                    #place row of grass closest to the enemy
                    else:
                        x = random.randint(0,9)
                        if currentState.board[x][3].constr == None and (x,3) not in moves:
                            move = (x,3)
                            currentState.board[x][3].constr == True
                moves.append(move)
            return moves

        #randomly place food on enemy's side
        elif currentState.phase == SETUP_PHASE_2:   
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
        #Get my inventory
        myInv = None
        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                myInv = inv
                break
        #If my inventory is still none, then I don't have one.
        if myInv == None:
            return Move(END, None, None)
        #If you have the food for an ant tunnel, try to purchase something random.
        if myInv.foodCount >= CONSTR_STATS[TUNNEL][BUILD_COST]:
            #First detect whether you have an ant WORKER with nothing under it
            placeableAnts = []
            for ant in myInv.ants:
                if currentState.board[ant.coords[0]][ant.coords[1]].constr == None and ant.type == WORKER and not ant.hasMoved:
                    placeableAnts.append(ant)
            #Then detect whether you have an anthill with nothing on top of it
            placeableHill = False
            hill = myInv.getAnthill()
            if currentState.board[hill.coords[0]][hill.coords[1]].ant == None:
                placeableHill = True
            #Choose randomly between building ants or tunnels
            if len(placeableAnts) != 0 and placeableHill:
                #randint returns up to the max, so no need to add or subtract for placeableHill's sake
                toPlace = random.randint(0, 5)
                if toPlace == 5:
                    #build a tunnel
                    location = random.randint(0, len(placeableAnts) - 1)
                    return Move(BUILD, [placeableAnts[location].coords], TUNNEL)
                else:
                    #build an ant
                    return Move(BUILD, [hill.coords], random.randint(WORKER, R_SOLDIER))
            elif len(placeableAnts) != 0:
                #build a tunnel
                location = random.randint(0, len(placeableAnts) - 1)
                return Move(BUILD, [placeableAnts[location].coords], TUNNEL)
            elif placeableHill:
                #build an ant
                return Move(BUILD, [hill.coords], random.randint(WORKER, R_SOLDIER))
            else:
                #I have resources to build, but no place to build things
                pass
        #See if you can move any ants
        antsToMove = []
        for ant in myInv.ants:
            if not ant.hasMoved:
                antsToMove.append(ant)
        #Move first of these ants
        if antsToMove != []:
            chosen = antsToMove[0]
            coordList = [chosen.coords]
            totalCost = 0
            lastStep = None
            #Variable to check if worker has moved
            hasMoved = 0
            while totalCost < UNIT_STATS[chosen.type][MOVEMENT]:
                #pick a random direction that won't move me back.
                possibleDirections = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                validDirections = []
                for direction in possibleDirections:
                    nextLoc = addCoords(coordList[-1], direction)
                    #Check that the move would be inside the board bounds
                    if nextLoc[0] > 9 or nextLoc[0] < 0 or nextLoc[1] > 9 or nextLoc[1] < 0:
                        continue
                    #Check that the move cost would not exceed what this ant is capable of
                    costOfStep = currentState.board[nextLoc[0]][nextLoc[1]].getMoveCost()
                    if currentState.board[nextLoc[0]][nextLoc[1]].ant == None and UNIT_STATS[chosen.type][MOVEMENT] >= totalCost + costOfStep:
                        validDirections.append(direction)
                #If no directions are valid, break out of the loop.
                if validDirections == []:
                    break
                
                #Worker ant commands
                elif chosen.type == WORKER:
                    #Move toward adjacent food if not carrying
                    if chosen.carrying == False:
                        for direction in validDirections:
                            nextCoord = addCoords(coordList[-1], direction)
                            if currentState.board[nextCoord[0]][nextCoord[1]].constr == FOOD:
                                coordList.append(nextCoord)
                                totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
                                hasMoved = 1
                            
                    #Move toward adjacent anthill or tunnel if carrying
                    else:
                        for direction in validDirections:
                            nextCoord = addCoords(coordList[-1], direction)
                            if currentState.board[nextCoord[0]][nextCoord[1]].constr == ANTHILL or currentState.board[nextCoord[0]][nextCoord[1]].constr == TUNNEL and currentState.board[nextCoord[0]][nextCoord[1]].ant == None:
                                coordList.append(nextCoord)
                                totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
                                hasMoved = 1
                                
                    if hasMoved == 0:
                    #store backward moves in array
                        backMove = []
                        #move back or to the side if on border
                        if chosen.coords[1] >=3:
                            for direction in validDirections:
                                if direction[1] <= 0:
                                    backMove.append(direction)
                            randNum = random.randint(0, len(backMove) - 1)
                            nextCoord = addCoords(coordList[-1], backMove[randNum])
                            coordList.append(nextCoord)
                            totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
                        #random move if not on border
                        else:
                            #Choose a random direction
                            randDir = random.randint(0, len(validDirections) - 1)
                            #Apply it
                            nextCoord = addCoords(coordList[-1], validDirections[randDir])
                            coordList.append(nextCoord)
                            #Add its cost to the total move cost
                            totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
                        
                #Soldier/Drone commands
                elif chosen.type == SOLDIER or chosen.type == DRONE:
                    #have ants move and stay in enemy territory
                    if chosen.coords[1] <= 6:
                        #append foward valid directions to array
                        forwardMove = []
                        for direction in validDirections:
                            if direction[1] == 1:
                                forwardMove.append(direction)
                        #randomly choose forward direction
                        randDir = random.randint(0, len(forwardMove) - 1)
                        nextCoord = addCoords(coordList[-1], forwardMove[randDir])
                        coordList.append(nextCoord)
                        totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
                        
                    #move randomly if already on enemy side
                    else:
                        randDir = random.randint(0, len(validDirections) - 1)
                        nextCoord = addCoords(coordList[-1], validDirections[randDir])
                        coordList.append(nextCoord)
                        totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()

                #random move if not worker or soldier                     
                else:
                    #Choose a random direction
                    randDir = random.randint(0, len(validDirections) - 1)
                    #Apply it
                    nextCoord = addCoords(coordList[-1], validDirections[randDir])
                    coordList.append(nextCoord)
                    #Add its cost to the total move cost
                    totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
                    
            #return the move created
            return Move(MOVE_ANT, coordList, None)
        #If I can't to anything, end turn
        return Move(END, None, None)
    
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
    #
    #def registerWin(self, hasWon):
        #method templaste, not implemented
        #pass

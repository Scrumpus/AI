from Player import *
from Ant import *
from math import *
from AIPlayerUtils import *
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

    NUM_INPUTS = 5
    inputs = []

    weights = []
    values = []

    ALPHA = 0.1

    NUM_LAYERS = 2

    LAYER_ONE_NODES = 1
    LAYER_ONE_NODE_SIZE = 15

    LAYER_ZERO_SMALL_NODES = 5
    LAYER_ZERO_SMALL_NODE_SIZE = 2

    LAYER_ZERO_LARGE_NODES = 10
    LAYER_ZERO_LARGE_NODE_SIZE = 3

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Rattle My Tomcats!")

        print "Initializing: Rattle my Tomcats!"

        self.inputs = []
        self.values = []
        self.weights = []

        # initialize our input array to default values
        for i in range(self.NUM_INPUTS):
            self.inputs.append(1)

        #Layer 0: the left side
        self.weights.append([])
        self.values.append([])

        for i in range(self.LAYER_ZERO_SMALL_NODES):
            #Layer 0, Small Nodes:
            self.weights[0].append([])
            self.values[0].append([])

            for j in range(self.LAYER_ZERO_SMALL_NODE_SIZE):
                self.weights[0][len(self.weights[0])-1].append(random.uniform(-1, 1))
                self.values[0][len(self.values[0])-1].append(1)


        for i in range(0, self.LAYER_ZERO_LARGE_NODES):
            #Layer 0, Large Nodes:
            self.weights[0].append([])
            self.values[0].append([])

            for j in range(self.LAYER_ZERO_LARGE_NODE_SIZE):
                self.weights[0][len(self.weights[0])-1].append(random.uniform(-1, 1))
                self.values[0][len(self.values[0])-1].append(1)


        #Layer 1: the right side
        self.weights.append([])
        self.values.append([])

        for i in range(self.LAYER_ONE_NODES):
            #Layer 1, Nodes:
            self.weights[1].append([])
            self.values[1].append([])

            for j in range(self.LAYER_ONE_NODE_SIZE):
                self.weights[1][0].append(random.uniform(-1, 1))
                self.values[1][0].append(1)


        #Layer 2: output
        self.values.append([[1]])


        return


    # backProgogate
    #
    #
    def backProgogate(self, expected, actual):

        outputError = expected - actual

        print str(outputError) + "\t\t= " + str(expected) + "\t\t- " + str(actual)

        outputDelta = actual * (1-actual) * outputError

        deltas = []

        for inputNode in range(self.LAYER_ONE_NODE_SIZE):
            weight = self.weights[1][0][inputNode]
            b = self.values[1][0][inputNode]

            currError = outputDelta * weight

            #errors.append(currError)
            deltas.append(b * (1-b) * currError)

            self.weights[1][0][inputNode] += self.ALPHA * outputDelta * self.values[1][0][inputNode]


        for node in range(self.LAYER_ZERO_SMALL_NODES):
            for input in range(self.LAYER_ZERO_SMALL_NODE_SIZE):
                self.weights[0][node][input] += self.ALPHA * deltas[node]*self.values[0][node][input]


        for node in range(self.LAYER_ZERO_SMALL_NODES+1, self.LAYER_ZERO_LARGE_NODES):
            for input in range(self.LAYER_ZERO_LARGE_NODE_SIZE):
                self.weights[0][node][input] += self.ALPHA * deltas[node]*self.values[0][node][input]

        return

    # generateOutput
    #
    #
    def generateOutput(self):

        #small nodes in layer 0 of values is simply our inputs
        for i in range(self.NUM_INPUTS):
            self.values[0][i][0] = self.inputs[i]

        #large nodes in layer 0  are are all possible pairs of inputs
        largeNodeIndex = self.LAYER_ZERO_SMALL_NODES
        for i in range(0, self.NUM_INPUTS-1):
            for j in range(i+1, self.NUM_INPUTS):
                self.values[0][largeNodeIndex][0] = self.inputs[i]
                self.values[0][largeNodeIndex][1] = self.inputs[j]
                largeNodeIndex += 1

        # This should propagate our initial values through the rest of the object
        for layer in range(self.NUM_LAYERS):
            for node in range(len(self.values[layer])):

                nodeVal = 0
                for val in range(len(self.values[layer][node])):
                    # sum all weighted values
                    nodeVal += self.values[layer][node][val]*self.weights[layer][node][val]

                # apply exponential function and update value of next layer
                denominator = 1 + exp(-1 * nodeVal)
                self.values[layer+1][0][node] = 1/denominator

        return

    ##
    # currentUnitsRatio
    # Description: returns a ratio of the count of my ants to all ants on the board
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return - ratio of the count of my ants to all ants on the board
    ##
    def currentUnitsRatio(self, currentState):
        myAntsCount = len(getAntList(currentState, currentState.whoseTurn))
        allAntsCount = len(getAntList(currentState, None))
        return myAntsCount / float(allAntsCount)

    ##
    # currentHealthRatio
    # Description: returns a ratio of the count of my ants health to all ants health on the board
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return - ratio of the count of my ants to all ants on the board
    ##
    def currentHealthRatio(self, currentState):
        myAnts = getAntList(currentState, currentState.whoseTurn)
        enAnts = getAntList(currentState, not currentState.whoseTurn)

        myHealth = 0
        enHealth = 0

        for ant in myAnts:
            myHealth += ant.health

        for ant in enAnts:
            enHealth += ant.health

        self.inputs[0] = myHealth / float(enHealth + myHealth)
        self.inputs[1] = enHealth / float(enHealth + myHealth)

        return myHealth / float(enHealth + myHealth)


    ##
    # enQueenHealth
    # Description: returns wieghted measure of enemy queens health between 0.8 and 1, 1 is better for us
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return - ratio of the count of my ants to all ants on the board
    ##
    def EnQueenHealth(self, currentState):
        weight = 0.2

        enQueen = getAntList(currentState, not currentState.whoseTurn, [QUEEN])
        if enQueen == []:
            return 1

        health = float(enQueen[0].health) / 4.0
        self.inputs[2] = 1 - health

        return 1 - weight + (1-health)*weight


    ##
    # getDist
    # Descritption: returns the manhattan distance between the two given coordinates
    #
    # Paramaters:
    #   coords1 - first set of coords
    #   coords2 - second set of coords
    #
    # Return: manhattan distance between the two points
    ##
    def getDist(self,coords1, coords2):
        x = fabs(coords1[0] - coords2[0])
        y = fabs(coords1[1] - coords2[1])

        return x + y

    ##
    # fighterQuality
    # Descritption: returns number between 0 and 1 rating the quality of fighter ant positions
    #               proximity to the enemy queen is better
    #
    # Paramaters:
    #   currentState - the state to rate (haha that rhymes)
    #
    # Return: some number between 0 and 1
    ##
    def fighterQuality(self, currentState):
        # lets make a list of our fighter ants (Soldiers, Ranged, and Drones)
        fighters = getAntList(currentState, currentState.whoseTurn, [SOLDIER, R_SOLDIER, DRONE])
        if fighters == []:
            # if we don't have any fighters then lets not less this influence anything
            return 1

        # lets find the enemy queen
        enQueen = getAntList(currentState, not currentState.whoseTurn, [QUEEN])
        if enQueen == []:
            # cool we win, no need to do any more work
            return 1
        enQueen = enQueen[0].coords

        # for all of our fighters
        totalDist = 0
        for f in fighters:
            # lets see how far they are from us
            totalDist += self.getDist(enQueen, f.coords)


        # how much better is there current position than the worst case?
        worstCase = len(fighters) * 20.0

        self.inputs[3] = 1 - (totalDist / worstCase)

        return 1 - (totalDist / worstCase) * 0.1

    ##
    # workerQuality
    # Descritption: returns number between 0 and 1 rating the quality of worker positions
    #               based off of proximity to the food when not carrying anything and
    #               position to depo when carrying something
    #
    # Paramaters:
    #   currentState - the state to rate (haha that rhymes)
    #
    # Return: some number between 0 and 1
    ##
    def workerQuality(self, currentState):
        # lets make a list of our workers
        workers = getAntList(currentState, currentState.whoseTurn, [WORKER])
        if workers == []:
            return 1

        # and a list of all the food on the board
        food = []
        for x in xrange(0, 10):
            for y in xrange(0, 10):
                if currentState.board[x][y].constr != None:
                    if currentState.board[x][y].constr.type == FOOD:
                        food.append((x, y))

        # and a list of all the depos
        depos = currentState.inventories[currentState.whoseTurn].getTunnels()
        depos.append(currentState.inventories[currentState.whoseTurn].getAnthill())

        # now for every ant
        totalDist = 0
        for w in workers:

            # lets find out how far they are from the closest food/depo
            if w.carrying == True:
                # we need to drop stuff off
                minDist = 20
                for d in depos:
                    dist = self.getDist(w.coords, d.coords)
                    if dist < minDist:
                        minDist = dist
                totalDist += minDist
            else:
                # we need to pick up food
                minDist = 20

                for f in food:
                    dist = self.getDist(w.coords, f)
                    if dist < minDist:
                        minDist = dist
                totalDist += minDist

        # how much better is there current position than the worst case?
        worstCase = len(workers) * 20.0

        self.inputs[4] = 1 - (totalDist / worstCase)

        return 1 - (totalDist / worstCase)

    ##
    # rateState
    # Description: takes a game state and returns a number between 0 and 1 to indicate how good
    #       the state is for our ai to win
    #       1 = Win State
    #       0 = Lose State
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return - quality of the current state
    ##
    def rateState(self, currentState):



        # A state where the enemy queen has taken damage is good
        enQueenDamage = self.EnQueenHealth(currentState)

        if enQueenDamage == 1:
            # Well then I guess we win
            return 1

        # A state were we have more health than enemy is good
        healthRatio = self.currentHealthRatio(currentState)

        # A measurement that encourages workers to gather resources
        workerQuality = self.workerQuality(currentState)

        # A measurement that encourages fighters to attack the enemy queen
        fighterQuality = self.fighterQuality(currentState)

        result = healthRatio * enQueenDamage * workerQuality * fighterQuality

        self.generateOutput()
        self.backProgogate(result, self.values[2][0][0])

        # now lets combine all of those to determine the quality of the state
        #return result
        return self.values[2][0][0]

    ##
    #isValidAttack
    #Description: Determines whether the attack with the given parameters is valid
    #   Attacking ant is assured to exist and belong to the player whose turn it is
    #
    #Parameters:
    #   attackingAnt - The Ant that is attacking (Ant)
    #   attackCoord - The coordinates of the Ant that is being attacked ((int,int))
    #
    #Returns: None if there is no attackCoord, true if valid attack, or false if invalid attack
    ##
    def isValidAttack(self, attackingAnt, attackCoord, state):
        if attackCoord == None:
            return None

        #check for well-formed input from players
        if not self.isValidCoord(attackCoord):
            return False

        attackLoc = state.board[attackCoord[0]][attackCoord[1]]

        if attackLoc.ant == None or attackLoc.ant.player == attackingAnt.player:
            return False

        #we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])

        #pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            #return True if within range
            return True
        else:
            return False

    ##
    #isValidCoord
    #Description: Returns whether this coord represents a valid board location.
    #
    #Parameters:
    #   coord - The coord to be checked trying to be checked ((int, int))
    #
    #Returns: True if the coordinate is between (0,0) and (9,9)
    ##
    def isValidCoord(self, coord):
        #check for well-formed coord
        if type(coord) != tuple or len(coord) != 2 or type(coord[0]) != int or type(coord[1]) != int:
            return False

        #check boundaries
        if coord[0] < 0 or coord[1] < 0 or coord[0] >= BOARD_LENGTH or coord[1] >= BOARD_LENGTH:
            return False

        return True


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
    #resolveAttack
    #Description: Checks a player wants to attack and takes appropriate action.
    #
    #Parameters:
    #   attackingAnt - The Ant that has an available attack (Ant)
    #   currentPlayer - The Player whose turn it currently is (Player)
    ##
    def resolveAttack(self, attackingAnt, state):
        #check if player wants to attack
        myId = state.whoseTurn
        validAttackCoords = []
        opponentId = (state.whoseTurn + 1) % 2
        range = UNIT_STATS[attackingAnt.type][RANGE]
        for ant in state.inventories[opponentId].ants:
            if self.isValidAttack(attackingAnt, ant.coords, state):
                #keep track of valid attack coords (flipped for player two)
                validAttackCoords.append(state.coordLookup(ant.coords, myId))
        if validAttackCoords != []:
            #give instruction to human player
            #players must attack if possible and we know at least one is valid
            attackCoord = None
            validAttack = False

            #keep requesting coords until valid attack is given
            while attackCoord == None:
                #get the attack from the player (flipped for player two)
                attackCoord = state.coordLookup(
                    self.getAttack(state, attackingAnt.clone(), validAttackCoords),
                    myId)

                #check for the move's validity
                # validAttack = self.isValidAttack(attackingAnt, attackCoord)

            #decrement ants health
            attackedAnt = state.board[attackCoord[0]][attackCoord[1]].ant
            attackedAnt.health -= UNIT_STATS[attackingAnt.type][ATTACK]

            #check for dead ant
            if attackedAnt.health <= 0:
                #remove dead ant from board
                state.board[attackCoord[0]][attackCoord[1]].ant = None
                #remove dead ant from inventory
                state.inventories[opponentId].ants.remove(attackedAnt)



    ##
    # genNextState
    # Description: Given the current state and a move, generate the resulting state
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #   move - the move to execute
    #
    # Return: the generated state
    ##
    def genNextState(self, currentState, move):

        nextState = currentState.clone()

        #check move type
        if move.moveType == MOVE_ANT:
            self.doMove(nextState, move)
        elif move.moveType == BUILD:
            self.doBuild(nextState, move)
        elif move.moveType == END:
            self.doEndTurn(nextState, move)

        return nextState


    ##
    # doMove
    # Description: Part of genNextState Method, handles moving an ant
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #   move - the move to execute
    ##
    def doMove(self, nextState, move):
        startCoord = move.coordList[0]
        endCoord = move.coordList[-1]

        #take ant from start coord
        antToMove = nextState.board[startCoord[0]][startCoord[1]].ant

        #change ant's coords and hasMoved status
        antToMove.coords = (endCoord[0], endCoord[1])
        antToMove.hasMoved = True

        #remove ant from location
        nextState.board[startCoord[0]][startCoord[1]].ant = None

        #put ant at last loc in coordList
        nextState.board[endCoord[0]][endCoord[1]].ant = antToMove

        #check and take action for attack
        self.resolveAttack(antToMove, nextState)


    ##
    # doBuild
    # Description: Part of genNextState Method, building things
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #   move - the move to execute
    ##
    def doBuild(self, nextState, move):
        coord = move.coordList[0]
        currentPlayerInv = nextState.inventories[nextState.whoseTurn]

        #subtract the cost of the item from the player's food count
        if move.buildType == TUNNEL:
            currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

            tunnel = Building(coord, TUNNEL, nextState.whoseTurn)
            nextState.board[coord[0]][coord[1]].constr = tunnel
        else:
            currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]

            ant = Ant(coord, move.buildType, nextState.whoseTurn)
            ant.hasMoved = True
            nextState.board[coord[0]][coord[1]].ant = ant
            nextState.inventories[nextState.whoseTurn].ants.append(ant)

    ##
    # doEndTurn
    # Description: Part of genNextState Method, handles ending your turn
    #
    # Paramaters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #   move - the move to execute
    ##
    def doEndTurn(self, nextState, move):
        #take care of end of turn business for ants and contructions
        for ant in nextState.inventories[nextState.whoseTurn].ants:

            constrUnderAnt = nextState.board[ant.coords[0]][ant.coords[1]].constr
            if constrUnderAnt != None:
                #if constr is enemy's and ant hasnt moved, affect capture health of buildings
                if type(
                        constrUnderAnt) is Building and not ant.hasMoved and not constrUnderAnt.player == nextState.whoseTurn:
                    constrUnderAnt.captureHealth -= 1
                    if constrUnderAnt.captureHealth == 0 and constrUnderAnt.type != ANTHILL:
                        constrUnderAnt.player = nextState.whoseTurn
                        constrUnderAnt.captureHealth = CONSTR_STATS[constrUnderAnt.type][CAP_HEALTH]
                #have all worker ants on food sources gather food
                elif constrUnderAnt.type == FOOD and ant.type == WORKER:
                    ant.carrying = True
                #deposit carried food (only workers carry)
                elif (constrUnderAnt.type == ANTHILL or constrUnderAnt.type == TUNNEL) and ant.carrying == True:
                    nextState.inventories[nextState.whoseTurn].foodCount += 1
                    ant.carrying = False

            #reset hasMoved on all ants of player
            ant.hasMoved = False

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

        # lets list all the possible moves that we can make
        moves = listAllLegalMoves(currentState)

        # To start, no move is better than the others and the best state we have seen is the current state
        bestMoves = []
        bestMoveQuality = self.rateState(currentState)


        for move in moves:
            # Tunnels never did anyone any good.
            if move.buildType == TUNNEL:
                continue

            # generate the next resulting state given the move
            nextState = self.genNextState(currentState, move)

            # rate the quality of the state
            stateQuality = self.rateState(nextState)
            # print str(stateQuality)

            # if its the best state found then save that one
            if stateQuality > bestMoveQuality:
                bestMoves = [move]
                bestMoveQuality = stateQuality

            # if its equaly as good as the best move then add it to the list of best moves
            if stateQuality == bestMoveQuality:
                bestMoves.append(move)

            # if quality == 1 then we won, don't bother checking other types
            if stateQuality == 1:
                # print "SUCKS TO BE YOU!"
                bestMoves = [move]
                bestMoveQuality = stateQuality
                break

        # if no moves are better than the current state then don't do anything
        if bestMoves == []:
            return Move(END, None, None)

        # randomly choose a move from the list of best moves to execute
        bestMove = bestMoves[random.randint(0, len(bestMoves)-1)]
        return bestMove


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
## Unit Test
##
#
# # Player 1's units
# p1Queen = Ant((0, 0), QUEEN, PLAYER_ONE)
# p1Anthill = Building((0, 0), ANTHILL, PLAYER_ONE)
# p1Tunnel = Building((0, 1), TUNNEL, PLAYER_ONE)
# p1Inventory = Inventory(PLAYER_ONE, [p1Queen], [p1Anthill, p1Tunnel], 0)
#
# # Player 2's units
# p2Queen = Ant((3, 0), QUEEN, PLAYER_TWO)
# p2Anthill = Building((3, 0), ANTHILL, PLAYER_TWO)
# p2Tunnel = Building((3, 1), TUNNEL, PLAYER_TWO)
# p2Inventory = Inventory(PLAYER_TWO, [p2Queen], [p2Anthill, p2Tunnel], 0)
#
# # Things placed on the board
# board = [[Location((col, row)) for row in xrange(0, BOARD_LENGTH)] for col in xrange(0, BOARD_LENGTH)]
#
# board[0][0].ant = p1Queen
# board[3][0].ant = p2Queen
#
# board[0][0].constr = p1Anthill
# board[3][0].constr = p2Anthill
#
# board[0][1].constr = p1Tunnel
# board[3][1].constr = p2Tunnel
#
# # Original Game State
# gs = GameState(board, [p1Inventory, p2Inventory], MENU_PHASE, PLAYER_ONE)
#
# # Move to execute
# mv = Move(MOVE_ANT, [(0, 0), (1, 0), (2, 0)], None)
#
# # AI to rate the states
# aip = AIPlayer(PLAYER_ONE)
#
# # next Game State (ngs is a modified copy of gs)
# ngs = aip.genNextState(gs, mv)
#
# # Manually tweak the original game state to represent the expected outcome
# p1Queen.coords = (2, 0)
# board[0][0].ant = None
# board[2][0].ant = p1Queen
# p2Queen.health -= 1
#
# if aip.rateState(gs) != aip.rateState(ngs):
#     print "Error: the next state is not equal to the expected state"
# else:
#     print str(aip.author) +": Unit Test #1 Passed"
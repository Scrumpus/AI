import random
from Constants import *
from Ant import UNIT_STATS
from Construction import CONSTR_STATS
from Move import *

#
# AIPlayerUtils.py
#
# a set of methods that are likely to be handy for all kinds of AI
# players.
#
# Important Note:  All the methods in this file that take a GameState object
# will not attempt to access the 'board' member of the at object.  This makes
# these routines safe for a GameState that has been generated via the
# GameState.fastclone method.
#

##
# legalCoord
#
# determines whether a given coordinate is legal or not
#
#Parameters:
#   coord        - an x,y coordinate
#
# Return: true (legal) or false (illegal)
def legalCoord(coord):

    #make sure we have a tuple or list with two elements in it
    try:
        if (len(coord) != 2):
            return False
    except TypeError:
        print "ERROR:  parameter to legalCoord was not a tuple or list"
        raise

    x = coord[0]
    y = coord[1]
    return ( (x >= 0) and (x <= 9) and (y >= 0) and (y <= 9))


##
# getAntList()
#
# builds a list of all ants that meet a given specification
#
# Parameters:
#     currentState - a GameState or Node
#     pid   - all ants must belong to this player id.  Pass None to
#             indicate any player
#     types - a tuple of all the ant types wanted (see Constants.py)
#
def getAntList(currentState,
               pid = None,
               types = (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER) ):

    #start with a list of all ants that belong to the indicated player(s)
    allAnts = []
    for inv in currentState.inventories:
        if (pid == None) or (pid == inv.player):
            allAnts += inv.ants

    #fill the result with ants that are of the right type
    result = []
    for ant in allAnts:
        if ant.type in types:
            result.append(ant)

    return result
        

##
# getConstrList()
#
# builds a list of all constructs that meet a given specification.
#
# Caveat:  if you pass a GameState for the first parameter, food and grass will
# not be returned.
#
# Parameters:
#     currentState - a GameState or Node
#     pid   - all ants must belong to this player id.  Pass None to
#             indicate any player including unowned constructs like grass/food
#     types - a tuple of all the constr types wanted (see Constants.py)
#
def getConstrList(currentState,
                  pid = None,
                  types = (ANTHILL, TUNNEL, GRASS, FOOD) ):

    #start with a list of all constrs that belong to the indicated player(s)
    allConstrs = []
    for inv in currentState.inventories:
        if (pid == None) or (pid == inv.player):
            allConstrs += inv.constrs

    #fill the result with constrs that are of the right type
    result = []
    for constr in allConstrs:
        if constr.type in types:
            result.append(constr)

    return result
        

##
# getConstrAt
#
# determines which construct is at a given coordinate
#
# Parameters:
#    state  - a valid GameState object
#    coords - a valid coordinate (code does not check for invalid!)
#
# Return:  the construct at the coordinate or None if there is none
def getConstrAt(state, coords):
    #get a list of all constructs
    allConstrs = getConstrList(state)

    #search for one at the given coord
    for constr in allConstrs:
        if (constr.coords == coords):
            return constr

    return None  #not found

##
# getAntAt
#
# determines which ant is at a given coordinate
#
# Parameters:
#    state  - a valid GameState object
#    coords - a valid coordinate (code does not check for invalid!)
#
# Return:  the ant at the coordinate or None if there is none
def getAntAt(state, coords):
    #get a list of all constructs
    allAnts = getAntList(state)

    #search for one at the given coord
    for ant in allAnts:
        if (ant.coords == coords):
            return ant

    return None  #not found
    

##
# listAdjacent
#
# Parameters:
#     coord    - a tuple containing a valid x,y coordinate
#     reqEmpty - if 'true' listAdjacent will skip cells that are occupied
#
# Return: a list of all legal coords that are adjacent to the given space
#
def listAdjacent(coord):
    #catch invalid inputs
    if (not legalCoord(coord)):
        return [];

    #this set of coord deltas represent movement in each cardinal direction
    deltas = [ (-1, 0), (1, 0), (0, -1), (0, 1) ]
    x = coord[0]
    y = coord[1]
    result = []

    #calculate the cost after making each move
    for delta in deltas:
        newX = delta[0] + coord[0]
        newY = delta[1] + coord[1]

        #skip illegal moves
        if (not legalCoord((newX, newY))):
            continue

        result.append((newX, newY))

    return result


##
# listReachableAdjacent
#
# calculates all the adjacent cells that can be reached from a given coord.
#
# Parameters:
#    state        - a GameState object 
#    coords       - where the ant is
#    movement     - movement points the ant has
#
# Return:  a list of coords (tuples)   
def listReachableAdjacent(state, coords, movement):
    #build a list of all adjacent cells
    oneStep = listAdjacent(coords)

    #winnow the list based upon cell contents and cost to reach
    candMoves = []
    for cell in oneStep:
        ant = getAntAt(state, cell)
        constr = getConstrAt(state, cell)
        moveCost = 1  #default cost
        if (constr != None):
            moveCost = CONSTR_STATS[constr.type][MOVE_COST]
        if (ant == None) and (moveCost <= movement):
            candMoves.append(cell)

    return candMoves

##
# listReachableAdjacentOLD
#
# calculates all the adjacent cells that can be reached from a given coord.
#
# Parameters:
#    currentState - current game state
#    coords       - where the ant is
#    movement     - movement points ant has
#
# Return:  a list of coords (tuples)   
def listReachableAdjacentOLD(currentState, coords, movement):
    #build a list of all adjacent cells
    oneStep = listAdjacent(coords)

    #winnow the list based upon cell contents and cost to reach
    candMoves = []
    for cell in oneStep:
        loc = currentState.board[cell[0]][cell[1]]
        if (loc.ant == None) and (loc.getMoveCost() <= movement):
            candMoves.append(cell)

    return candMoves


##
# listAllMovementPaths              <!-- RECURSIVE -->
#
# calculates all the legal paths for a single ant to move from a given position.
# The ant doesn't actually have to be there for this method to return a valid
# answer.
#
# Parameters:
#    currentState - current game state
#    coords       - where the ant is
#    movement     - movement points ant has remaining
#
# Return: a list of lists of coords (tuples). Each sub-list of tuples is an
# acceptable set of coords for a Move object
def listAllMovementPaths(currentState, coords, movement):
    #base case: ant can't move any further
    if (movement <= 0): return []

    #construct a list of all valid one-step moves
    adjCells = listReachableAdjacent(currentState, coords, movement)
    oneStepMoves = []
    for cell in adjCells:
        oneStepMoves.append([coords, cell])

    #add those as valid moves
    validMoves = list(oneStepMoves)

    #recurse for each adj cell to see if we can take additional steps
    for move in oneStepMoves:
        #figure out what it would cost to get to the current dest
        moveCoords = move[-1]
        constrAtDest = getConstrAt(currentState, moveCoords)
        cost = 1   #default
        if constrAtDest != None:
            cost = CONSTR_STATS[constrAtDest.type][MOVE_COST]

        #get a list of all moves that will extend this one
        extensions = listAllMovementPaths(currentState, moveCoords, movement - cost)

        #create new moves by adding each extension to the base move
        for ext in extensions:
            newMove = list(move)      #create a clone
            for cell in ext[1:]:      #start at index '1' to skip overlap
                newMove.append(cell)
            validMoves.append(newMove)

    return validMoves


##
# stepsToReach
#
# estimates the shortest distance between two cells taking
# movement costs into account.
#
#Parameters:
#   currentState   - The state of the game (GameState)
#   src            - starting position (an x,y coord)
#   dst            - destination position (an x,y coord)
#
# Return: the costs in steps (an integer) or -1 on invalid input
def stepsToReach(currentState, src, dst):
    #check for invalid input
    if (not legalCoord(src)): return -1
    if (not legalCoord(dst)): return -1

    #a dictionary of already visted cells and the corresponding cost to reach
    visited = { src : 0 }
    #a list of to be processed cells
    queue = [ src ]

    #this loops processes cells in the queue until it is empty
    while(len(queue) > 0):
        cell = queue.pop(0)

        #if this cell is our destination we are done
        if (cell == dst):
            return visited[cell]

        #calc distance to all cells adj to this one assuming we reach them
        #from this one
        nextSteps = listAdjacent(cell)
        for newCell in nextSteps:
            constrAtDest = getConstrAt(currentState, newCell)
            cost = 1  #default
            if constrAtDest != None:
                cost = CONSTR_STATS[constrAtDest.type][MOVE_COST]
            dist = visited[cell] + cost

            #if the new distance is best so far, update the visited dict
            if (visited.has_key(newCell)):
                if (dist < visited[newCell]):
                    visited[newCell] = dist
            #if we've never seen this cell before also update dict and
            #enqueue this new cell to be processed at a future loop iteration
            else:
                visited[newCell] = dist
                queue.append(newCell)

    #we should never reach this point
    return -1

##
# listAllBuildMoves
#
# calcualtes all the legal BUILD moves that the current player can
# make
#
# Parameters
#   currentState - currentState of the game
#
# Returns: a list of Move objects
def listAllBuildMoves(currentState):
    result = []

    #if the anthill is unoccupied list a BUILD move for each ant
    #that there is enough food to build
    myInv = getCurrPlayerInventory(currentState)
    hill = myInv.getAnthill()
    if (getAntAt(currentState, hill.coords)  == None):
        for type in range(WORKER, R_SOLDIER + 1):
            cost = UNIT_STATS[type][COST]
            if (cost <= myInv.foodCount):
                result.append(Move(BUILD, [hill.coords], type))

    #if we don't have 3 food to build a tunnel then we're done
    if (myInv.foodCount < 3):
        return result
                
    #for each worker ant that is a legal position, you could build
    #a tunnel
    for ant in myInv.ants:
        if (ant.type != WORKER): continue   #only workers can build tunnels
        if (ant.hasMoved): continue         #this worker has already moved
        if (getConstrAt(currentState, ant.coords) == None):
            #see if there is adj food
            inTheClear = True   #assume ok to build until proven otherwise
            for coord in listAdjacent(ant.coords):
                if (not legalCoord((coord[0],coord[1]))):
                    continue

                #is there food here?
                constrHere = getConstrAt(currentState, coord)
                if (constrHere != None) and (constrHere.type == FOOD):
                    inTheClear = False
                    break

            #if no food was found then building a tunnel is valid
            if inTheClear:
                result.append(Move(BUILD, [ant.coords], TUNNEL))

    return result

##
# listAllMovementMoves
#
# calculates all valid MOVE_ANT moves for the current player in a
# given GameState
#
# Parameters:
#   currentState - the current state
#
# Returns:  a list of Move objects
def listAllMovementMoves(currentState):
    result = []

    #first get all MOVE_ANT moves for each ant in the inventory
    myInv = getCurrPlayerInventory(currentState)
    for ant in myInv.ants:
        #skip ants that have already moved
        if (ant.hasMoved): continue

        #create a Move object for each valid movement path
        allPaths = listAllMovementPaths(currentState,
                                        ant.coords,
                                        UNIT_STATS[ant.type][MOVEMENT])
        for path in allPaths:
            result.append(Move(MOVE_ANT, path, None))

    return result


##
# listAllLegalMoves
#
# determines all the legal moves that can be made by the player
# whose turn it currently is.
#
# Parameters:
#   currentState - the current state
#
# Returns:  a list of Move objects
def listAllLegalMoves(currentState):
    result = []
    result.extend(listAllMovementMoves(currentState))
    result.extend(listAllBuildMoves(currentState))
    result.append(Move(END, None, None))
    return result



##
# Return: a reference to the inventory of the player whose turn it is
def getCurrPlayerInventory(currentState):
    #Get my inventory
    resultInv = None
    for inv in currentState.inventories:
        if inv.player == currentState.whoseTurn:
            resultInv = inv
            break
        
    return resultInv
    
##
# Return: a reference to the QUEEN of the player whose turn it is
def getCurrPlayerQueen(currentState):
    #find the queen
    queen = None
    for inv in currentState.inventories:
        if inv.player == currentState.whoseTurn:
            queen = inv.getQueen()
            break
    return queen
    
##
# returns a character representation of a given ant
# (helper for asciiPrintState)
def charRepAnt(ant):
    if (ant == None):
        return " "
    elif (ant.type == QUEEN):
        return "Q"
    elif (ant.type == WORKER):
        return "W"
    elif (ant.type == DRONE):
        return "D"
    elif (ant.type == SOLDIER):
        return "S"
    elif (ant.type == R_SOLDIER):
        return "I"
    else:
        return "?"

##
# returns a character representation of a given construct
# (helper for asciiPrintState)
def charRepConstr(constr):
    if (constr == None):
        return " "
    if (constr.type == ANTHILL):
        return "^"
    elif (constr.type == TUNNEL):
        return "@"
    elif (constr.type == GRASS):
        return ";"
    elif (constr.type == FOOD):
        return "%"
    else:
        return "?"

##
# returns a character representation of a given location
# (helper for asciiPrintState)
def charRepLoc(loc):
    if (loc == None):
        return " "
    elif (loc.ant != None):
        return charRepAnt(loc.ant)
    elif (loc.constr != None):
        return charRepConstr(loc.constr)
    else:
        return "."


##
# asciiPrintState
#
# prints a text representation of a GameState to stdout.  This is useful for
# debugging.
#
# Parameters:
#    state - the state to print
#
def asciiPrintState(state):
    #select coordinate ranges such that board orientation will match the GUI
    #for either player
    coordRange = range(0,10)
    colIndexes = " 0123456789"
    if (state.whoseTurn == PLAYER_TWO):
        coordRange = range(9,-1,-1)
        colIndexes = " 9876543210"

    #print the board with a border of column/row indexes
    print colIndexes
    index = 0              #row index
    for x in coordRange:
        row = str(x)
        for y in coordRange:
            ant = getAntAt(state, (y, x))
            if (ant != None):
                row += charRepAnt(ant)
            else:
                constr = getConstrAt(state, (y, x))
                if (constr != None):
                    row += charRepConstr(constr)
                else:
                    row += "."
        print row + str(x)
        index += 1
    print colIndexes

    #print food totals
    p1Food = state.inventories[0].foodCount
    p2Food = state.inventories[1].foodCount
    print " food: " + str(p1Food) + "/" + str(p2Food)

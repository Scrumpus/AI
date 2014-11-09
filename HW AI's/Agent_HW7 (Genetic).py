import sys
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
import AIPlayerUtils

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

    #
    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   creates fitness list and gene list for the player
    #
    #Variables:
    # fitnessList - a list of the fitness of each gene in geneList
    # geneList - a list of lists will store the current population of genes
    # geneIndex - an index of which gene in the population is next to be evaluated
    # gameCount - keeps track of which game we are on
    # generation - the generation of the current population of genes
    # hasPlaced - variable to decide whether the gene has been placed or not
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Babymaker")
        #initalize all the variables to be empty/zero
        self.fitnessList = []
        self.geneList = []
        self.geneIndex = 0
        self.gameCount = 0
        self.generation = 0
        self.hasPlaced = 0
        f = open('C:\AI\HW7\EvidenceFile.txt', 'w')
        sys.stdout = f
        

    #
    #setLists
    #Description:
    # initialize the population of genes with random values and reset the fitness list to default values
    #
    #Parameters:
    # currentState - takes in the current state of the board

    def setLists(self, currentState):
        #create a gene of all the player's constructions
        numToPlace = 11
        numGenes = 12

        #set both the fitnessList and geneList to be empty
        self.geneList = [None]*numGenes
        self.fitnessList = [0]*numGenes

        #place all 11 constructions randomly on the player's side of the board
        for currGen in range(0, numGenes):
            gene = [None]*numToPlace
            for i in range(0, (numToPlace)):
                while gene[i] == None:
                    x = random.randint(0,9)
                    y = random.randint(0,3)
                    if (x, y) not in gene:
                        gene[i] = (x, y)

            #double check to make sure no spot in gene is None
            for spot in range(0, len(gene)):
            #if None type is found, create a spot for it
                if gene[spot] is None:
                    x = random.randint(0,9)
                    y = random.randint(0,3)
                    if (x, y) not in gene:
                        gene[spot] = (x, y)

            self.geneList[currGen] = gene
                
    #
    #generateChildren
    #Description:
    # take two parent genes and generate two child genes that result from the pairing
    #
    #Parameters:
    # parent1 - the first parent gene
    # parent2 - the second parent gene
    #
    #Return: two new children from mating the parent genes
    # child1 - first child gene created
    # child2 - second child gene created
    #
    def generateChildren(self, parent1, parent2):

        #initialize the two children genes to be empty
        child1 = [None]*11
        child2 = [None]*11

        #random chance of mutation
        randMutate = random.randint(0,19)

        #slice the parents at randomSpot
        randomSpot = random.randint(4, 8)
        child1[0:randomSpot] = parent1[0:randomSpot]
        child1[randomSpot:] = parent2[randomSpot:]
        child2[0:randomSpot] = parent2[0:randomSpot]
        child2[randomSpot:] = parent1[randomSpot:]

        #if mutation occurs, mutate one of the children at a random spot
        if randMutate == 7:
            randChild = random.randint(0, 1)
            randIndex = random.randint(0, 10)

            if randChild == 0:

                child1 = self.mutate(child1, randIndex)
            else:

                child2 = self.mutate(child2, randIndex)

        #check for no duplicate coordinates
        child1 = self.noDuplicates(child1)
        child2 = self.noDuplicates(child2)

        #double check to make sure no spot in child is None
        for spot in range(0, len(child1)):
            #if None type is found, create a spot for it
            if child1[spot] is None:
                while child1[spot] is None:
                    x = random.randint(0,9)
                    y = random.randint(0,3)
                    if (x, y) not in child1:
                        child1[spot] = (x, y)

        for spot in range(0, len(child2)):
        #if None type is found, create a spot for it
            if child2[spot] is None:
                while child2[spot] is None:
                    x = random.randint(0,9)
                    y = random.randint(0,3)
                    if (x, y) not in child2:
                        child2[spot] = (x, y)

        return child1, child2

    #
    #noDuplicates
    #Description: checks to see if the gene has any duplicate spots
    # if spot is found, a mutation will occur to fix the problem
    #
    #Parameters:
    # gene- a gene to check
    #
    #return:
    #  gene - returns the same gene, or modified gene if duplicate found
    #
    def noDuplicates(self, gene):
        # searches through the gene to search for duplicates
        for x in range(0, len(gene)):
            #if duplicates are found, the gene is mutated to fix the problem
            if gene.count(gene[x]) > 1:
                gene = self.mutate(gene, x)
        return gene

    #
    #mutate
    #Description: mutates the gene at a specified index, with a random new position
    #
    #Parameters:
    # gene - gene to be mutated
    # index - the position of the gene to be mutated
    #
    #Return:
    # gene - the mutated gene
    #
    def mutate(self, gene, index):
        mutated = 0
        #continues to attempt to mutate until a new spot is created
        while mutated == 0:
            x = random.randint(0,9)
            y = random.randint(0,3)
            #sets the new gene at the new index
            if (x, y) not in gene:
                gene[index] = (x, y)
                return gene
        
        
    #
    #nextGeneration
    #Description:
    #   Generates the next generation of genes from the old one
    #
    #
    def nextGeneration(self):
        #create sorted fitness list, from least to greatest
        sortFitnessList = self.fitnessList
        sortFitnessList.sort()
        #creates a parentList of four genes
        parentList = [None]*4

        #choose the top 4 genes to repopulate
        startIdx = 0
        for i in range(8,12):
            for j in range(startIdx, 12):
                #find the gene in the sorted list matching in the unsorted
                if self.fitnessList[j] >= sortFitnessList[i]:
                    parentList[i-8] = self.geneList[j]
                    #start next iteration at the next spot after the chosen gene
                    if j != 11:
                        startIdx = j+1
                    break
                
        #print "this is the parent list" + str(parentList)
        #print "this is the gene list " + str(self.geneList)
        #reset gene list that stores the new population of genes
        self.geneList = [None]*12

        #generate children from each permutation of the parent genes
        #there are twelve total new genes created
        tempChildren = self.generateChildren(parentList[0], parentList[1])
        self.geneList[0] = tempChildren[0]
        self.geneList[1] = tempChildren[1]

        
        tempChildren = self.generateChildren(parentList[0], parentList[2])
        self.geneList[2] = tempChildren[0]
        self.geneList[3] = tempChildren[1]

        
        tempChildren = self.generateChildren(parentList[0], parentList[3])
        self.geneList[4] = tempChildren[0]
        self.geneList[5] = tempChildren[1]


        tempChildren = self.generateChildren(parentList[1], parentList[2])
        self.geneList[6] = tempChildren[0]
        self.geneList[7] = tempChildren[1]


        tempChildren = self.generateChildren(parentList[1], parentList[3])
        self.geneList[8] = tempChildren[0]
        self.geneList[9] = tempChildren[1]


        tempChildren = self.generateChildren(parentList[2], parentList[3])
        self.geneList[10] = tempChildren[0]
        self.geneList[11] = tempChildren[1]

        
        #increment the generation
        #reset the fitnessList
        self.fitnessList = [0]*12
        self.generation += 1
        
  ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        #increment the game count
        self.gameCount += 1
        #increase current gene fitness if player won
        if hasWon == True:
            self.fitnessList[self.geneIndex] += 1
        else:
            self.fitnessList[self.geneIndex] -= 1
        #go to next gene after 50 games
        if self.gameCount == 50:
            self.geneIndex += 1
            self.gameCount = 0
        #create next generation after evaluating all of current gene population
        if self.geneIndex == 12:
            self.geneIndex = 0
            self.nextGeneration()

        
    
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
        #list of moves that the player will make
        moves = []
        #creates a geneList of randomly selected positions for constructions
        if self.hasPlaced == 0:
            self.setLists(currentState)
            self.hasPlaced = 1
        
        #get the currentGene from the list
        currGene = self.geneList[self.geneIndex]

        #if it is set up phase 1, get the moves from the currentGene
        if currentState.phase == SETUP_PHASE_1:
            moves = currGene[0:11]
            #print the moves for the first game
            return moves
        #randomly select stuff on the enemy's side
        elif currentState.phase == SETUP_PHASE_2:
            #print the state layout for the start of each gene
            if self.gameCount == 0:
                print str(AIPlayerUtils.asciiPrintState(currentState))
            numToPlace = 2
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
            return [(0,0)]
    
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
        #Get my inventory
        myInv = None
        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                myInv = inv
                break
        #If my inventory is still none, then I don't have one.
        if myInv == None:
            return Move(END, None, None)
        #Try to build an ant
        if myInv.foodCount >= UNIT_STATS[SOLDIER][COST]:  #is there enough food?
            #Detect whether the anthill has nothing on top of it
            hill = myInv.getAnthill()
            if currentState.board[hill.coords[0]][hill.coords[1]].ant == None:
                #build a random ant
                toPlace = random.randint(WORKER, R_SOLDIER)
                return Move(BUILD, [hill.coords], random.randint(WORKER, R_SOLDIER))
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
                else:
                    #Choose a random direction
                    randDir = random.randint(0, len(validDirections) - 1)
                    #Apply it
                    nextCoord = addCoords(coordList[-1], validDirections[randDir])
                    coordList.append(nextCoord)
                    #Add its cost to the total move cost
                    totalCost += currentState.board[nextCoord[0]][nextCoord[1]].getMoveCost()
            #Return the chosen move
            return Move(MOVE_ANT, coordList, None)
        #If I can't to anything, end turn
        return Move(END, None, None)
    
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



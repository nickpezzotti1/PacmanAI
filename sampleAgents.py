# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util



class CornerSeekingAgent(Agent):

    def __init__(self):
         self.map = None
         # 0 is unexplored
         # 1 is wall
         # 2 is food
         # 3 is visited

         self.corners = None

    def getAction(self, state):
        # init map
        if self.map is None:
            self._initialize(state)

        # update knowledge of map
        self._update_map(state)

        my_position = api.whereAmI(state)

        if self.corners[0] == my_position:
            del self.corners[0]

        destination = (11, 1)
        print("visiting", destination)
        move_direction = self._goTo(state, my_position, destination)

        return api.makeMove(move_direction, None)

    #A-star pathfinding
    def _goTo(self, state, start, end):
        legal_moves = api.legalActions(state)

        start = tuple(start)
        end = tuple(end)
        print("start A*")
        path = aStar(self.map, start, end)
        print("path", path)

        return self._get_direction(start, path[1])

    def _get_direction(self, start, next):
        print("moving from", start, " to ", next)
        if (start[1] < next[1]):
            return Directions.NORTH
        if (start[1] > next[1]):
            return Directions.SOUTH
        if (start[0] < next[0]):
            return Directions.EAST
        if (start[0] > next[0]):
            return Directions.WEST

    def _initialize(self, state):
        self.corners = api.corners(state)
        max_row = 0
        max_col = 0

        for coordinate in self.corners:
            max_row = max(coordinate[0], max_row)
            max_col = max(coordinate[1], max_col)

        self.map = [[0 for col in range(max_row + 1)] for col in range(max_col + 1)]
        corners = api.corners(state)
        print("start")
        for i in range(len(corners)):
            if corners[i] == (0, 0):
                corners[i] = (1, 1)

            elif corners[i] == (len(self.map[0]) - 1, len(self.map) - 1):
                corners[i] = (len(self.map[0]) - 2, len(self.map) - 2)

            elif corners[i] == (0, len(self.map) - 1):
                corners[i] = (1, len(self.map) - 2)

            elif corners[i] == (len(self.map[0]) - 1, 0):
                corners[i] = (len(self.map[0]) - 2, 1)
        self.corners = corners
        self._print_map(state)
        print("Corners:", self.corners, api.corners(state))

    def _update_map(self, state):
        for wall in api.walls(state):
            self.map[wall[1]][wall[0]] = 1

        for food in api.food(state):
            self.map[food[1]][food[0]] = 2

        myPos = api.whereAmI(state)
        self.map[myPos[1]][myPos[0]] = 3

        self._print_map(state)

    def _print_map(self, state):
        myPos =  api.whereAmI(state)

        print("---------------MAP---------------")
        for i in reversed(range(len(self.map))):
            for j in range(len(self.map[i])):
                if myPos[1] == i and myPos[0] == j:
                    print "P",
                elif self.map[i][j] == 1:
                    print "|",
                elif self.map[i][j] == 2:
                    print "*",
                elif self.map[i][j] == 3:
                    print " ",
                else:
                    print "?",
            print ""




class HungryAgent(Agent):

    def getAction(self, state):
        myPosition = api.whereAmI(state)
        closestFood = self._findClosestFood(myPosition, api.food(state))
        legal = api.legalActions(state)

        moveToMake = self._getDirectionToMove(myPosition, closestFood, legal)
        return api.makeMove(moveToMake, legal)

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        if Directions.WEST in legal:
            return api.makeMove(Directions.WEST, legal)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

    def _findClosestFood(self, myPos, foodPositions):
        return sorted(foodPositions, key=lambda pos: abs(pos[0]-myPos[0]) + abs(pos[1]-myPos[1]))[0]

    def _getDirectionToMove(self, myPos, foodPos, legalMoves):
        if (myPos[0] - foodPos[0] < 0 and Directions.WEST in legalMoves):
            return Directions.WEST
        if (myPos[0] - foodPos[0] > 0 and Directions.EAST in legalMoves):
            return Directions.EAST
        if (myPos[1] - foodPos[1] > 0 and Directions.SOUTH in legalMoves):
            return Directions.SOUTH
        if (myPos[1] - foodPos[1] < 0 and Directions.NORTH in legalMoves):
            return Directions.NORTH


class GoWestAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        if Directions.WEST in legal:
            return api.makeMove(Directions.WEST, legal)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # Where are the ghosts?
        print "Ghost positions:"
        theGhosts = api.ghosts(state)
        for i in range(len(theGhosts)):
            print theGhosts[i]

        # How far away are the ghosts?
        print "Distance to ghosts:"
        for i in range(len(theGhosts)):
            print util.manhattanDistance(pacman,theGhosts[i])

        # Where are the capsules?
        print "Capsule locations:"
        print api.capsules(state)

        # Where is the food?
        print "Food locations: "
        print api.food(state)

        # Where are the walls?
        print "Wall locations: "
        print api.walls(state)

        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.
        return api.makeMove(Directions.STOP, legal)


class Node:
    def __init__(self,value,point):
        self.value = value
        self.point = point
        self.parent = None
        self.H = 0
        self.G = 0
    def move_cost(self,other):
        return 0 if self.value == '.' else 1

def children(point,grid):
    x,y = point.point
    links = [grid[d[0]][d[1]] for d in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y)]]
    return [link for link in links if link.value != 1]
def manhattan(point,point2):
    return abs(point.point[0] - point2.point[0]) + abs(point.point[1]-point2.point[0])
def aStar(grid, start, goal):
    #The open and closed sets
    openset = set()
    closedset = set()
    #Current point is the starting point
    current = start
    #Add the starting point to the open set
    openset.add(current)
    #While the open set is not empty
    while openset:
        #Find the item in the open set with the lowest G + H score
        current = min(openset, key=lambda o:o.G + o.H)
        #If it is the item we want, retrace the path and return it
        if current == goal:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
        #Remove the item from the open set
        openset.remove(current)
        #Add it to the closed set
        closedset.add(current)
        #Loop through the node's children/siblings
        for node in children(current,grid):
            #If it is already in the closed set, skip it
            if node in closedset:
                continue
            #Otherwise if it is already in the open set
            if node in openset:
                #Check if we beat the G score
                new_g = current.G + current.move_cost(node)
                if node.G > new_g:
                    #If so, update the node to have a new parent
                    node.G = new_g
                    node.parent = current
            else:
                #If it isn't in the open set, calculate the G and H score for the node
                node.G = current.G + current.move_cost(node)
                node.H = manhattan(node, goal)
                #Set the parent to our current item
                node.parent = current
                #Add it to the set
                openset.add(node)
    #Throw an exception if there is no path
    raise ValueError('No Path Found')

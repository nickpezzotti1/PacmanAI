# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

import sys
GHOST_REWARD = -1
FOOD_REWARD = 0.2
CAPSULE_REWARD = 0.3
EMPTY_CELL_REWARD = -0.04
WALL_REWARD = 0


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

MazeEntity = enum("GHOST", "FOOD", "CAPSULE", "EMPTY_CELL", "WALL", "PACMAN")


class Maze:

    def __init__(self, state):
        self.map = None
        self.utilities = None

        self.update(state)

    def update(self, state):
        ''' Update the rewards on the map . Called after every move '''
        self.map = self._initialize(state)
        self._fill(state)
        self.utilities = None
        self._value_iteration(state)

    def _initialize(self, state):
        ''' Generate an empty 2D-matrix representing the array '''

        corners = api.corners(state)

        max_row = 0
        max_col = 0
        for coordinate in corners:
            max_row = max(coordinate[0], max_row)
            max_col = max(coordinate[1], max_col)

        return [[MazeEntity.EMPTY_CELL for col in range(max_row + 1)] for col in range(max_col + 1)]

    def _fill(self, state):
        ''' Place the maze entities in the maze '''

        # Place walls
        for wall in api.walls(state):
            self.map[wall[1]][wall[0]] = MazeEntity.WALL

        # Place foods
        for food in api.food(state):
            self.map[food[1]][food[0]] = MazeEntity.FOOD

        # Place capsules
        for capsule in api.capsules(state):
            self.map[capsule[1]][capsule[0]] = MazeEntity.CAPSULE

        # Place ghosts
        for ghost in api.ghosts(state):
            self.map[int(ghost[1])][int(ghost[0])] = MazeEntity.GHOST

        # Place pacman player
        myPos = api.whereAmI(state)
        self.map[myPos[1]][myPos[0]] = MazeEntity.PACMAN

    def get_reward(self, row, col, state):
        if (self.map[row][col] == MazeEntity.WALL):
            return "na"
        elif (self.map[row][col] == MazeEntity.FOOD):
            return FOOD_REWARD + self._manhattan_distance_to_closest_ghost(state, row, col)/100
        elif (self.map[row][col] == MazeEntity.CAPSULE):
            return CAPSULE_REWARD + self._manhattan_distance_to_closest_ghost(state, row, col)/100
        elif (self.map[row][col] == MazeEntity.GHOST):
            return GHOST_REWARD
        elif (self.map[row][col] == MazeEntity.PACMAN or self.map[row][col] == MazeEntity.EMPTY_CELL):
            return EMPTY_CELL_REWARD #+ self._manhattan_distance_to_closest_ghost(state, row, col)/100

        raise Exception("Oops! Something went wrong")

    def print_map(self, print_mode = 0):
        '''
        print a string representation of the map to the terminal
        print_mode:
            0 - human_readable
            1 - utilities
        '''
        print("---------------------------------------------MAP---------------------------------------------")
        for i in reversed(range(len(self.map))):
            for j in range(len(self.map[i])):
                if (print_mode == 0):
                    if self.map[i][j] == MazeEntity.PACMAN:
                        print "P\t",
                    elif self.map[i][j] == MazeEntity.WALL:
                        print "|\t",
                    elif self.map[i][j] == MazeEntity.FOOD:
                        print "*\t",
                    elif self.map[i][j] == MazeEntity.CAPSULE:
                        print "o\t",
                    elif self.map[i][j] == MazeEntity.GHOST:
                        print "@\t",
                    else:
                        print (str(round(self.utilities[i][j], 2)) if self.utilities else "?")  + "\t",
                else:
                    if self.map[i][j] == MazeEntity.WALL:
                        print "|\t",
                    else:
                        print (str(round(self.utilities[i][j], 2)) if self.utilities else "?") + "\t",

            print ""

    def _value_iteration(self, state):
        U =  [[0 for i in range(len(self.map[0]))] for j in range(len(self.map))]
        for row in range(len(U)):
            for col in range(len(U[row])):
                #print U[row][col], "TO",
                U[row][col] = self.get_reward(row, col, state)

        U_1 = [row[:] for row in U]

        for i in range(100):
            U = [row[:] for row in U_1]

            for row in range(len(self.map)):
                for col in range(len(self.map[row])):
                    if self.map[row][col] == MazeEntity.EMPTY_CELL or self.map[row][col] == MazeEntity.PACMAN:
                        #print(self.get_reward(row, col))
                        U_1[row][col] = self.get_reward(row, col, state) + 1 * max(self.getEU(U, row, col).values())
        #self._apply_ghost_sheet(U_1)
        self.utilities = U_1
        #self.print_map(1)
        #self.print_map(0)

    def _apply_ghost_sheet(U):
        for row in range(len(U)):
            for col in range(len(U[row])):
                if self.get_reward(row, col, state) == GHOST_REWARD:
                    U[row][col] = self.get_reward(row, col, state)

    def getEU(self, utilities, row, col):
        deterministic_utilities = {
            "Stop": utilities[row][col],
            "North": utilities[row + 1][col] if self.map[row + 1][col] != MazeEntity.WALL else utilities[row][col],
            "East": utilities[row][col + 1] if self.map[row][col + 1] != MazeEntity.WALL else utilities[row][col],
            "South": utilities[row - 1][col] if self.map[row - 1][col] != MazeEntity.WALL else utilities[row][col],
            "West": utilities[row][col - 1] if self.map[row][col - 1] != MazeEntity.WALL else utilities[row][col],
        }

        expected_utilities = {
            "Stop": deterministic_utilities["Stop"],
            "North": 0.8*deterministic_utilities["North"]+0.1*deterministic_utilities["East"]+0.1*deterministic_utilities["West"],
            "East": 0.8*deterministic_utilities["East"]+0.1*deterministic_utilities["North"]+0.1*deterministic_utilities["South"],
            "South": 0.8*deterministic_utilities["South"]+0.1*deterministic_utilities["East"]+0.1*deterministic_utilities["West"],
            "West": 0.8*deterministic_utilities["West"]+0.1*deterministic_utilities["North"]+0.1*deterministic_utilities["South"],
        }

        return expected_utilities

    def _manhattan_distance_to_closest_ghost(self, state, row, col):
    	theGhosts = api.ghosts(state)

    	distances = []
    	for i in range(len(theGhosts)):
    	    distances.append(util.manhattanDistance([row, col],theGhosts[i]))

    	return min(distances)


class MDPAgent(Agent):
    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        # CREATE A MAP THAT STORES THE UTILITY OF EACH CELL
        self.map = Maze(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        self.map.update(state) # performs value iteration

        # Get the actions we can try
        legal_moves = api.legalActions(state)
        move = self._determine_best_action(state, legal_moves)
        # Random choice between the legal options.
        #print("Chosen Direction:", move)
        return api.makeMove(move, legal_moves)

    def _determine_best_action(self, state, legal_moves):
        moves = self.map.getEU(self.map.utilities, api.whereAmI(state)[1], api.whereAmI(state)[0])

        return self.arg_max({k: v for k, v in moves.iteritems() if k in legal_moves}
)

    def arg_max(self, dict):
        return max(dict, key=dict.get)

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
GHOST_REWARD = -200
FOOD_REWARD = 10
CAPSULE_REWARD = 10
EMPTY_CELL_REWARD = -1
WALL_REWARD = 0
NO_MOVE_REWARD = -1


class MapRepresentation():

    def __init__(self, state):
        self.update_map(state)

    def update_map(self, state):
        ''' Update the rewards on the map . Called after every move '''
        self.map = self._get_empty_map(state)

        self.pac_man_pos =  api.whereAmI(state)
        self._update_rewards(state)
        self._value_iteration(state)

    def _get_empty_map(self, state):
        ''' Generate an empty 2D-matrix representing the array '''

        corners = api.corners(state)

        max_row = 0
        max_col = 0
        for coordinate in corners:
            max_row = max(coordinate[0], max_row)
            max_col = max(coordinate[1], max_col)

        return [[EMPTY_CELL_REWARD for col in range(max_row + 1)] for col in range(max_col + 1)]

    def _update_rewards(self, state):
        ''' Update the board with current rewards '''

        for wall in api.walls(state):
            self.map[wall[1]][wall[0]] = WALL_REWARD

        for food in api.food(state):
            self.map[food[1]][food[0]] = FOOD_REWARD

        for capsule in api.capsules(state):
            self.map[capsule[1]][capsule[0]] = CAPSULE_REWARD

        for ghost in api.ghosts(state):
            self.map[int(ghost[1])][int(ghost[0])] = GHOST_REWARD

        myPos = api.whereAmI(state)
        self.map[myPos[1]][myPos[0]] = NO_MOVE_REWARD

    def get_reward(self, row, col):
        return self.map[row][col]

    def get_utility(self, row, col):
        return self.utilities[row][col]

    def is_wall(self, row, col):
        return self.map[row][col] == WALL_REWARD

    def print_map(self, print_mode = 0):
        '''
        print a string representation of the map to the terminal
        print_mode:
            0 - human_readable
            1 - rewards
            2 - utilities

        '''
        print("---------------MAP---------------")
        for i in reversed(range(len(self.map))):
            for j in range(len(self.map[i])):
                if (print_mode == 1):
                    if self.pac_man_pos[1] == i and self.pac_man_pos[0] == j:
                        print "P\t",
                    elif self.map[i][j] == WALL_REWARD:
                        print "|\t",
                    else:
                        print str(self.map[i][j]) + "\t",
                elif (print_mode == 0):
                    if self.pac_man_pos[1] == i and self.pac_man_pos[0] == j:
                        print "P\t",
                    elif self.map[i][j] == WALL_REWARD:
                        print "|\t",
                    elif self.map[i][j] == FOOD_REWARD:
                        print "*\t",
                    elif self.map[i][j] == CAPSULE_REWARD:
                        print "o\t",
                    elif self.map[i][j] == GHOST_REWARD:
                        print "@\t",
                    else:
                        print str(round(self.utilities[i][j], 2)) + "\t",

                else:
                    if self.pac_man_pos[1] == i and self.pac_man_pos[0] == j:
                        print "P\t",
                    elif self.is_wall(i, j):
                        print "|\t",
                    else:
                        print str(self.utilities[i][j]) + "\t",

            print ""

    def _value_iteration(self, state, discount_factor = 0.5):
        self.print_map(1)
        U = [row[:] for row in self.map]
        U_1 = [row[:] for row in U]

        for i in range(10):
            U = [row[:] for row in U_1]

            for row in range(len(self.map)):
                for col in range(len(self.map[0])):
                    #print(row, col, self.map[row][col])
                    if self.map[row][col] == EMPTY_CELL_REWARD:
                        U_1[row][col] = self.map[row][col] + 0.5 * max(self.getEU(U, row, col).values())

        print("Finished value iteration \n\n\n")
        self.utilities = U_1
        self.print_map(0)

    def getEU(self, utilities, row, col):
        deterministic_utilities = {
            "Stop": utilities[row][col],
            "North": utilities[row + 1][col] if self.map[row + 1][col] != WALL_REWARD else utilities[row][col],
            "East": utilities[row][col + 1] if self.map[row][col + 1] != WALL_REWARD else utilities[row][col],
            "South": utilities[row - 1][col] if self.map[row - 1][col] != WALL_REWARD else utilities[row][col],
            "West": utilities[row][col - 1] if self.map[row][col - 1] != WALL_REWARD else utilities[row][col],
        }

        expected_utilities = {
            "Stop": deterministic_utilities["Stop"],
            "North": 0.8*deterministic_utilities["North"]+0.1*deterministic_utilities["East"]+0.1*deterministic_utilities["West"],
            "East": 0.8*deterministic_utilities["East"]+0.1*deterministic_utilities["North"]+0.1*deterministic_utilities["South"],
            "South": 0.8*deterministic_utilities["South"]+0.1*deterministic_utilities["East"]+0.1*deterministic_utilities["West"],
            "West": 0.8*deterministic_utilities["West"]+0.1*deterministic_utilities["North"]+0.1*deterministic_utilities["South"],
        }

        return expected_utilities


class MDPAgent(Agent):
    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        # CREATE A MAP THAT STORES THE UTILITY OF EACH CELL
        self.map = MapRepresentation(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        self.map.update_map(state) # performs value iteration

        # Get the actions we can try
        legal_moves = api.legalActions(state)
        print(legal_moves)
        move = self._determine_best_action(state, legal_moves)
        # Random choice between the legal options.
        print("Moving", move)
        return api.makeMove(move, legal_moves)

    def _determine_best_action(self, state, legal_moves):
        moves = self.map.getEU(self.map.utilities, api.whereAmI(state)[1], api.whereAmI(state)[0])
        print("moves", moves)

        return self.arg_max({k: v for k, v in moves.iteritems() if k in legal_moves}
)

    def arg_max(self, dict):
        return max(dict, key=dict.get)

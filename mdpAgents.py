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
GHOST_REWARD = -200 #-sys.maxint - 1
FOOD_REWARD = 10
CAPSULE_REWARD = 15
EMPTY_CELL_REWARD = -1
WALL_REWARD = 0
NO_MOVE_REWARD = -2


class MDPAgent(Agent):
    map = None

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        # CREATE A MAP THAT STORES THE UTILITY OF EACH CELL
        print "Setting up map"
        self._update_map(state)
        self._print_map(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):
        print "Updating internal representation of map"
        self._update_map(state)

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal_moves = api.legalActions(state)
        move = self._determine_best_action(state, legal_moves)
        # Random choice between the legal options.
        return api.makeMove(move, legal_moves)

    def _determine_best_action(self, state, legal_moves):
        calculate_utility = lambda state : lambda move : self._get_move_utility(state, move)
        heuristic_of_moves = map(calculate_utility(state), legal_moves)
        print(heuristic_of_moves)


        best_move_index = 0
        for i in range(len(heuristic_of_moves)):
            if heuristic_of_moves[best_move_index] < heuristic_of_moves[i]:
                best_move_index = i

        return legal_moves[best_move_index]

    #TODO put non determinism in
    def _get_move_utility(self, state, direction):
        myPos =  api.whereAmI(state)
        if direction == "Stop":
            return self.map[myPos[1]][myPos[0]]
        elif direction == "North":
            return self.map[myPos[1] + 1][myPos[0]]
        elif direction == "East":
            return self.map[myPos[1]][myPos[0] + 1]
        elif direction == "South":
            return self.map[myPos[1] - 1][myPos[0]]
        elif direction == "West":
            return self.map[myPos[1]][myPos[0] - 1]


    def _reset_map(self, state):
        corners = api.corners(state)
        max_row = 0
        max_col = 0

        for coordinate in corners:
            max_row = max(coordinate[0], max_row)
            max_col = max(coordinate[1], max_col)

        self.map = [[EMPTY_CELL_REWARD for col in range(max_row + 1)] for col in range(max_col + 1)]

    def _update_map(self, state):
        self._reset_map(state)
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

        self._print_map(state)


    def _print_map(self, state, print_heuristics=True):
        myPos =  api.whereAmI(state)
        print("---------------MAP---------------")
        for i in reversed(range(len(self.map))):
            for j in range(len(self.map[i])):
                if (print_heuristics):
                    if myPos[1] == i and myPos[0] == j:
                        print "P\t",
                    elif self.map[i][j] == WALL_REWARD:
                        print "|\t",
                    else:
                        print str(self.map[i][j]) + "\t",
                else:
                    if myPos[1] == i and myPos[0] == j:
                        print "P",
                    elif self.map[i][j] == WALL_REWARD:
                        print "|",
                    elif self.map[i][j] == FOOD_REWARD:
                        print "*",
                    elif self.map[i][j] == CAPSULE_REWARD:
                        print "o",
                    elif self.map[i][j] == GHOST_REWARD:
                        print "@",
                    else:
                        print " ",

            print ""

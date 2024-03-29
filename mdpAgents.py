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

# The agent here is was written by Nicholas Pezzotti, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import math

""" These are the parameters that our agent use """
GHOST_REWARD = -1
FOOD_REWARD = 0.2
CAPSULE_REWARD = FOOD_REWARD
EMPTY_CELL_REWARD = -0.03
MIN_DISTANCE_FROM_GHOST = 0 # this will be set proportional to the map size

DEFAULT_GAMMA_VALUE = 0.85
DEFAULT_DELTA_VALUE = 0.00001



class MDPAgent(Agent):
    """
    A Pacman agent that works on a MDP. It is designed for a non-deterministic,
    fully-observable, dynamic environment.

    ...

    Methods
    -------
    getAction(state) : str
        Given a state, accounting for non-deterministic actions it computes the
        action that returns the maximum expected utility and returns it.
    """

    def getAction(self, state):
        """
        Given a state, accounting for non-deterministic actions it computes the
        action that returns the maximum expected utility and returns it.

        Amongst the legal moves, after having performed value iterations, returns
        the best move.
        """

        # Get the possible actions
        legal_moves = api.legalActions(state)
        move = self._determine_best_action(state, legal_moves)

        #print("Chosen Direction:", move)
        return api.makeMove(move, legal_moves)

    def _determine_best_action(self, state, legal_moves):
        """
        This function handles the logic for querying the map the expected utility of each
        action and returns the best one.
        """

        maze = Maze(state)
        moves = maze.getEU(api.whereAmI(state)[1], api.whereAmI(state)[0])
        #print("moves", str(moves))

        return self._arg_max({k: v for k, v in moves.iteritems() if k in legal_moves})

    def _arg_max(self, dict):
        """
        A simple implementation of argmax. Given a dictionary returns the
        key which is mapped to the maximum value.
        """

        return max(dict, key=dict.get)


def enum(*sequential, **named):
    """Template to allow enums in Python2 without using imports"""

    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

MazeEntity = enum("GHOST", "FOOD", "CAPSULE", "EMPTY_CELL", "WALL", "PACMAN")

class Maze:
    """
    A class used to represent a model of the maze the agent is navigating

    ...

    Attributes
    ----------
    map : [[MazeEntity]]
        a 2D array that stores what MazeEntity is stored in which cell
    utilities : [[float]]
        a 2D array that represents the the utility of each cell on the board

    Methods
    -------
    getEU(row, col, utilities=None) : {direction: str -> expectedUtility: float}
        Returns a dictionary that maps the direction of movement from the
        location (row, col) and its expectedUtility

        To get the expected utility of a cell rather than resulting from a
        movement access the field self.utilities directly

    print_map(print_mode = 0)
        Prints the map to the standard output

        print a string representation of the map to the terminal
        print_mode:
            0 - human_readable
            1 - utilities

    """

    def __init__(self, state):
        """
        Initializes the 2D array representing the maze, places the entities in
        the matrix and performs value iteration on the matrix
        Parameters
        ----------
        state
            The current state of the board
        """

        self.map = self._initialize(state)
        self._fill(state)
        self.distances = self._precompute_distances(state)
        global MIN_DISTANCE_FROM_GHOST
        MIN_DISTANCE_FROM_GHOST = int(math.log(3 * max(len(self.map), len(self.map[0])))/math.log(3)) + 1
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

        # Place ghosts (This is done after the food and capsules as we don't
        # care if there is food under a ghost, we will avoid it)
        for ghost in api.ghosts(state):
            self.map[int(ghost[1])][int(ghost[0])] = MazeEntity.GHOST

        # Place pacman player
        myPos = api.whereAmI(state)
        self.map[myPos[1]][myPos[0]] = MazeEntity.PACMAN

    def _get_reward(self, row, col, state):
        """Reward function

            Given a row and col, it returns the reward of that cell.
            The values are the ones of the constants defined at the top of the file,
            with the exception of food, capsules and pacman's position which is
            significantly reduced if he in a predifined distance from any of the
            ghosts.
        """

        if (self.map[row][col] == MazeEntity.WALL):
            return "na"
        elif (self.map[row][col] == MazeEntity.FOOD):
            return ((GHOST_REWARD / self._manhattan_distance_to_closest_ghost(state, row, col)) if self._manhattan_distance_to_closest_ghost(state, row, col) < MIN_DISTANCE_FROM_GHOST else FOOD_REWARD)
        elif (self.map[row][col] == MazeEntity.CAPSULE):
            return ((GHOST_REWARD / self._manhattan_distance_to_closest_ghost(state, row, col)) if self._manhattan_distance_to_closest_ghost(state, row, col) < MIN_DISTANCE_FROM_GHOST else CAPSULE_REWARD)
        elif (self.map[row][col] == MazeEntity.GHOST):
            return GHOST_REWARD
        elif (self.map[row][col] == MazeEntity.PACMAN or self.map[row][col] == MazeEntity.EMPTY_CELL):
            return ((GHOST_REWARD / self._manhattan_distance_to_closest_ghost(state, row, col)) if self._manhattan_distance_to_closest_ghost(state, row, col) < MIN_DISTANCE_FROM_GHOST else EMPTY_CELL_REWARD)

        raise Exception("Oops! Something went wrong")

    def _value_iteration(self, state, delta=DEFAULT_DELTA_VALUE, gamma=DEFAULT_GAMMA_VALUE):
        """ Performs value iteration with Bellman Equation on the maze and stores it in self.utilities.

            Parameters
            ----------
            delta
                The minimum maximum change from one iteration to the next. The
                larger it is, the quicker it will converge but the less accurate
                it is.
            gamma
                The amount the previous iteration's utility is discounted. The
                larger the more farsighted our agent will be.
        """

        U =  [[self._get_reward(row, col, state) for col in range(len(self.map[0]))] for row in range(len(self.map))]
        U_1 = [row[:] for row in U] # copy

        while True:
            max_delta = 0
            U = [row[:] for row in U_1]

            for row in range(len(self.map)):
                for col in range(len(self.map[row])):
                    if self.map[row][col] == MazeEntity.EMPTY_CELL or self.map[row][col] == MazeEntity.PACMAN or self.map[row][col] == MazeEntity.FOOD or self.map[row][col] == MazeEntity.CAPSULE:
                        # BELLMAN EQUATION
                        U_1[row][col] = self._get_reward(row, col, state) + gamma * max(self.getEU(row, col, U).values())
                        max_delta = max(abs(U_1[row][col]  - U[row][col]), max_delta)

            # stop iterating if the smallest delta is larger than our delta value
            if (delta >= max_delta):
                break;

        self.utilities = U_1

    def getEU(self, row, col, utilities=None):
        """Returns a dictionary that maps the direction of movement from the location (row, col) and its expectedUtility.

            To get the expected utility of a cell rather than resulting from a
            movement access the field self.utilities directly.
        """

        utilities = self.utilities if utilities == None else utilities

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
        """Finds the closest distance and finds the manhattan distance to it."""

    	return self.distances[row][col]

    def _precompute_distances(self, state):
        """ Precomputes the distance of each cell to that of the closest ghost """
        theGhosts = api.ghosts(state)

        distances = [[float("inf") for col in range(len(self.map[0]))] for row in range(len(self.map))]

        theGhosts = api.ghosts(state)
        for ghost in theGhosts:
            self._flood_fill(distances, int(ghost[1]), int(ghost[0]), 0)

        return distances

    def _flood_fill(self, distances, row, col, val):
        """ The variation of the floodfill algorithm. This computes the distance to the closest ghost, stopping at a given threshold k """

        if row < 0 or row >= len(self.map) or col < 0 or col >= len(self.map[row]) or (distances[row][col] != -1 and val >= distances[row][col]) or self.map[row][col] == MazeEntity.WALL or val > MIN_DISTANCE_FROM_GHOST:
            return

        distances[row][col] = val

        val = val + 1
        self._flood_fill(distances, row, col + 1, val)
        self._flood_fill(distances, row, col - 1, val)
        self._flood_fill(distances, row + 1, col, val)
        self._flood_fill(distances, row - 1, col, val)


    def print_map(self, print_mode = 0):
        """
        pretty print a string representation of the map to the terminal
        print_mode:
            0 - human_readable
            1 - utilities
        """""

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

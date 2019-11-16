"""
Visualize Genetic Algorithm to find a maximum point in a function.
Visit my tutorial website for more: https://morvanzhou.github.io/tutorials/
# """
# import numpy as np
# import matplotlib.pyplot as plt
#
# DNA_SIZE = 10            # DNA length
# POP_SIZE = 100           # population size
# CROSS_RATE = 0.8         # mating probability (DNA crossover)
# MUTATION_RATE = 0.003    # mutation probability
# N_GENERATIONS = 200
# X_BOUND = [0, 5]         # x upper and lower bounds
#
#
# def F(x): return np.sin(10*x)*x + np.cos(2*x)*x     # to find the maximum of this function
#
#
# # find non-zero fitness for selection
# def get_fitness(pred): return pred + 1e-3 - np.min(pred)
#
#
# # convert binary DNA to decimal and normalize it to a range(0, 5)
# def translateDNA(pop): return pop.dot(2 ** np.arange(DNA_SIZE)[::-1]) / float(2**DNA_SIZE-1) * X_BOUND[1]
#
#
# def select(pop, fitness):    # nature selection wrt pop's fitness
#     idx = np.random.choice(np.arange(POP_SIZE), size=POP_SIZE, replace=True,
#                            p=fitness/fitness.sum())
#     return pop[idx]
#
#
# def crossover(parent, pop):     # mating process (genes crossover)
#     if np.random.rand() < CROSS_RATE:
#         i_ = np.random.randint(0, POP_SIZE, size=1)                             # select another individual from pop
#         cross_points = np.random.randint(0, 2, size=DNA_SIZE).astype(np.bool)   # choose crossover points
#         parent[cross_points] = pop[i_, cross_points]                            # mating and produce one child
#     return parent
#
#
# def mutate(child):
#     for point in range(DNA_SIZE):
#         if np.random.rand() < MUTATION_RATE:
#             child[point] = 1 if child[point] == 0 else 0
#     return child
#
#
# pop = np.random.randint(2, size=(POP_SIZE, DNA_SIZE))   # initialize the pop DNA
#
# plt.ion()       # something about plotting
# x = np.linspace(*X_BOUND, 200)
# plt.plot(x, F(x))
#
# for _ in range(N_GENERATIONS):
#     F_values = F(translateDNA(pop))    # compute function value by extracting DNA
#
#     # something about plotting
#     if 'sca' in globals(): sca.remove()
#     sca = plt.scatter(translateDNA(pop), F_values, s=200, lw=0, c='red', alpha=0.5); plt.pause(0.05)
#
#     # GA part (evolution)
#     fitness = get_fitness(F_values)
#     print("Most fitted DNA: ", pop[np.argmax(fitness), :])
#     pop = select(pop, fitness)
#     pop_copy = pop.copy()
#     for parent in pop:
#         child = crossover(parent, pop_copy)
#         child = mutate(child)
#         parent[:] = child       # parent is replaced by its child
#
# plt.ioff(); plt.show()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
import random
import os

EPOCHS = 20
INITIAL_POPULATION_SIZE = 10

def eval_fitness(genotype):
    res1 = int(os.popen('python pacman.py --pacman MDPAgent --layout smallClassic -q -a \"food_reward=%s,empty_reward=%s,min_dist=%s,gamma=%s\" -n 10'%(genotype[0], genotype[1], genotype[3], genotype[2])).read())
    res2 = int(os.popen('python pacman.py --pacman MDPAgent --layout mediumClassic -q -a \"food_reward=%s,empty_reward=%s,min_dist=%s,gamma=%s\" -n 2'%(genotype[0], genotype[1], genotype[3], genotype[2])).read())
    return res1 + res2*5

def initialise(n):
    initial_population = []
    for i in range(n):
        food_reward = round(random.uniform(0, 0.7), 2)
        empty_cell = round(random.uniform(-0.5, 0), 2)
        gamma = round(random.uniform(0.1, 0.99), 2)
        min_distance = random.randint(1,3)

        initial_population.append((food_reward, empty_cell, gamma, min_distance))

    return initial_population

def weighted_random_choice(choices):
    max = sum(choices.values())
    pick = random.uniform(0, max)
    current = 0
    for key, value in choices.items():
        current += value
        if current > pick:
            return key

def crossover(p1, p2):
    return (p1[0], p1[1], p2[2], p2[3])

def mutate(genome):
    r = random.uniform(0, 1)
    if r < 0.1:
        r = random.uniform(0, 1)
        if r < 0.5:
            r -= 0.1
        else:
            r +=  0.1

    r = random.uniform(0, 1)
    if r < 0.1:
        r = random.uniform(0, 1)
        if r < 0.5:
            r -= 0.1
        else:
            r +=  0.1

    r = random.uniform(0, 1)
    if r < 0.1:
        r = random.uniform(0, 1)
        if r < 0.5:
            r -= 0.1
        else:
            r +=  0.1

    r = random.uniform(0, 1)
    if r < 0.01:
        r = random.uniform(0, 1)
        if r < 0.5:
            r -= 1
        else:
            r += 1

def reproduce(chromosomes, n):
    res = []
    for i in range(n + 1):
        p1 = weighted_random_choice(chromosomes)
        p2 = weighted_random_choice(chromosomes)

        c = crossover(p1, p2)
        c = mutate(c)

        res.append(c)
    return res


population = initialise(INITIAL_POPULATION_SIZE)
print "Initialising popoulation to size", len(population)

for i in range(EPOCHS):
    chromosomes = {genotype : eval_fitness(genotype) for genotype in population}
    print "chromosomes", chromosomes
    print "pool score:", sum(chromosomes.values())
    population = reproduce(chromosomes, len(population))
    print "Updating population to", population
    print " "

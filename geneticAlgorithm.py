import random
import os

EPOCHS = 20
INITIAL_POPULATION_SIZE = 50

def eval_fitness(genotype):
    res1 = int(os.popen('python pacman.py --pacman MDPAgent --layout smallGrid -q -a \"food_reward=%s,empty_reward=%s,min_dist=%s,gamma=%s\" -n 5'%(genotype[0], genotype[1], genotype[3], genotype[2])).read())
    res2 = int(os.popen('python pacman.py --pacman MDPAgent --layout mediumClassic -q -a \"food_reward=%s,empty_reward=%s,min_dist=%s,gamma=%s\" -n 2'%(genotype[0], genotype[1], genotype[3], genotype[2])).read())
    return res1*2 + res2*5

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
    genome = list(genome)
    r = random.uniform(0, 1)
    if r < 0.1:
        r = random.uniform(0, 1)
        if r < 0.5:
            genome[0] -= 0.1
        else:
            genome[0] +=  0.1

    r = random.uniform(0, 1)
    if r < 0.1:
        r = random.uniform(0, 1)
        if r < 0.5:
            genome[1] -= 0.1
        else:
            genome[1] += 0.1

    r = random.uniform(0, 1)
    if r < 0.1:
        r = random.uniform(0, 1)
        if r < 0.5:
            genome[2] -= 0.1
        else:
            genome[2] +=  0.1

    r = random.uniform(0, 1)
    if r < 0.01:
        r = random.uniform(0, 1)
        if r < 0.5:
            genome[3] -= 1
        else:
            genome[3] += 1

    return tuple(genome)


def reproduce(chromosomes, n):
    res = []
    for i in range(n):
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
    print " "

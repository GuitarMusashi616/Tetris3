import pygame
from time import sleep
import math
import numpy
import random
import neat
import os
import visualize
from constants import TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT, SHAPES, S_WIDTH, S_HEIGHT
from grid import Grid
from option import Option
from piece import Piece

pygame.font.init()

def draw_grid(surface, row, col):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + PLAY_WIDTH, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + PLAY_HEIGHT))  # vertical lines


def draw_window(surface, grid):
    surface.fill((0,0,0))
    # Tetris Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255,255,255))

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j * 30, TOP_LEFT_Y + i * 30, 30, 30), 0)

    # draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)
    # pygame.display.update()

def train(config_file, generations):
    # Load configuration.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, generations)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

    input('Press any key to begin demonstration')
    demonstrate(winner, config)
    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    # for xi, xo in zip(xor_inputs, xor_outputs):
    #     output = winner_net.activate(xi)
    #     print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))
    #
    node_names = {-1: 'TOTAL_HOLES', -2: 'COMPLETE_LINES', -3: 'AGGREGATE_HEIGHT', -4: 'BUMPINESS', 0: 'SCORE'}
    node_names2 = {
        -1: 'CH_1',
        -2: 'CH_2',
        -3: 'CH_3',
        -4: 'CH_4',
        -5: 'CH_5',
        -6: 'CH_6',
        -7: 'CH_7',
        -8: 'CH_8',
        -9: 'CH_9',
        -10: 'CH_10',
        -11: 'HD_1,2',
        -12: 'HD_2,3',
        -13: 'HD_3,4',
        -14: 'HD_4,5',
        -15: 'HD_5,6',
        -16: 'HD_6,7',
        -17: 'HD_7,8',
        -18: 'HD_8,9',
        -19: 'HD_9,10',
        -20: 'MAX_HEIGHT',
        -21: 'TOTAL_HOLES',
        -22: 'HOLE_1',
        -23: 'HOLE_2',
        -24: 'HOLE_3',
        -25: 'HOLE_4',
        -26: 'HOLE_5',
        -27: 'HOLE_6',
        -28: 'HOLE_7',
        -29: 'HOLE_8',
        -30: 'HOLE_9',
        -31: 'HOLE_10',
        0: 'SCORE',
    }
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    # print("BEST OF EACH 5 GENERATIONS")
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    # p.add_reporter(neat.StdOutReporter(True))
    # p.run(eval_genomes, 1)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-9')
    # p.add_reporter(neat.StdOutReporter(True))
    # p.run(eval_genomes, 1)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-14')
    # p.add_reporter(neat.StdOutReporter(True))
    # p.run(eval_genomes, 1)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-19')
    # p.add_reporter(neat.StdOutReporter(True))
    # p.run(eval_genomes, 1)

def eval_genomes(genomes, config):
    # global STATE
    for _, genome in genomes:
        # random.setstate(STATE)  # same order of tetromino shapes
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        main_training(genome, net, display=True)

def demonstrate(genome, config):
    # genome.fitness = 0
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    main_testing(genome, net)


def get_outputs(net, inputs):
    outputs = []
    for i in range(len(inputs)):
        outputs.append(net.activate(inputs[i]))
    return outputs


def main_training(genome, net, display=False):
    run = True
    grid = Grid()
    pieces = []
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
        pieces.insert(0, Piece(0, 0, random.choice(SHAPES)))
        inputs, spawn = grid.get_final_states(pieces[0])
        outputs = get_outputs(net, inputs)
        if len(outputs) <= 0:
            break
        # assign the nets choice and execute
        ind = outputs.index(max(outputs))
        pieces[0].x, pieces[0].y, pieces[0].rotation = spawn[ind]
        pieces[0].drop(grid)
        grid.draw(pieces[0])
        genome.fitness += grid.clear_lines()
        genome.fitness += 10
        if display:
            # pygame.time.wait(20)
            draw_window(WIN, grid.grid)
            pygame.display.update()
            pass


def main_testing(genome, net):
    run = True
    grid = Grid()
    pieces = []
    decision_time = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

        if decision_time:
            pieces.insert(0, Piece(0, 0, random.choice(SHAPES)))
            inputs, spawn = grid.get_final_states(pieces[0])
            outputs = get_outputs(net, inputs)
            if len(outputs) <= 0:
                break
            # assign the nets choice and execute
            ind = outputs.index(max(outputs))
            pieces[0].x, pieces[0].y, pieces[0].rotation = spawn[ind]
            decision_time = False

        collided = pieces[0].down(grid)
        grid.draw(pieces[0])
        draw_window(WIN, grid.grid)
        pygame.display.update()
        pygame.time.wait(20)
        if collided:
            genome.fitness += grid.clear_lines()
            genome.fitness += 10
            decision_time = True
        else:
            grid.erase(pieces[0])

def load_ai(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    champs = []
    print("BEST OF EACH 5 GENERATIONS")
    ai_file = 'tetrisAI'
    # p = neat.Checkpointer.restore_checkpoint(os.path.join(ai_file, 'neat-checkpoint-4'))
    # p.add_reporter(neat.StdOutReporter(True))
    # champs.append(p.run(eval_genomes, 1))

    # p = neat.Checkpointer.restore_checkpoint(os.path.join(ai_file, 'neat-checkpoint-9'))
    # p.add_reporter(neat.StdOutReporter(True))
    # champs.append(p.run(eval_genomes, 1))
    #
    # p = neat.Checkpointer.restore_checkpoint(os.path.join(ai_file, 'neat-checkpoint-14'))
    # p.add_reporter(neat.StdOutReporter(True))
    # champs.append(p.run(eval_genomes, 1))
    #
    # p = neat.Checkpointer.restore_checkpoint(os.path.join(ai_file, 'neat-checkpoint-19'))
    # p.add_reporter(neat.StdOutReporter(True))
    # champs.append(p.run(eval_genomes, 1))

    input('Press any key to continue')

    for c in champs:
        demonstrate(c, config)


def player_like2(piece, grid):
    x = 5
    y = 0
    rotation = 0
    moves = []

    while x != piece.x or rotation != piece.rotation:
        if rotation < piece.rotation:
            rotation += 1
            y += 1
            moves += [Option.CW_ROTATE, Option.DOWN]
            continue
        elif rotation > piece.rotation:
            rotation -= 1
            y += 1
            moves += [Option.CCW_ROTATE, Option.DOWN]
            continue
        if x < piece.x:
            x += 1
            y += 1
            moves += [Option.RIGHT, Option.DOWN]
            continue
        elif x > piece.x:
            x -= 1
            y += 1
            moves += [Option.LEFT, Option.DOWN]
            continue
    return moves


def main_testing2():
    run = True
    grid = Grid()
    pieces = []
    decision_time = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

        if decision_time:
            pieces.insert(0, Piece(0, 0, random.choice(SHAPES)))
            inputs, spawn = grid.get_final_states(pieces[0])
            outputs = [sum(input) for input in inputs]
            if len(outputs) <= 0:
                break
            # assign the nets choice and execute
            ind = outputs.index(min(outputs))
            pieces[0].x, pieces[0].y, pieces[0].rotation = spawn[ind]
            moves = player_like2(pieces[0], grid)
            pieces[0].x = 5
            pieces[0].y = 0
            pieces[0].rotation = 0
            decision_time = False

        collided = False
        if moves:
            move = moves.pop(0)
            collided = pieces[0].do_option(move, grid)
        else:
            collided = pieces[0].down(grid)

        grid.draw(pieces[0])
        draw_window(WIN, grid.grid)
        pygame.display.update()
        pygame.time.wait(20)
        if collided:
            grid.clear_lines()
            decision_time = True
        else:
            grid.erase(pieces[0])
    # BFS

def get_moves(piece, grid):
    piece2 = Piece(0, 0, piece.shapes)
    tree = {}
    queue = piece2.get_options(grid)
    # BFS
    while queue:
        o = queue.pop(0)
        piece2.do_option(o, grid)
        piece2.get_options(grid)
        # options = piece2.get_options(grid)


def test():
    main_testing2()


WIN = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
pygame.display.set_caption('Tetris')
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward.txt')
train(config_path, 5)
# load_ai(config_path)
# test()

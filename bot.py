import random

import game_message
from game_message import *
import numpy as np


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self.wall_positions = []
        self.teamZone = []

    def get_next_move(self, game_message: TeamGameState):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        if game_message.tick == 1:
            for line in range(len(game_message.map.tiles)):
                for column in range(len(game_message.map.tiles[line])):
                    if game_message.map.tiles[line][column] == TileType.WALL:
                        self.wall_positions.append((line, column))

            for line in range(len(game_message.map.tiles)):
                for column in range(len(game_message.map.tiles[line])):
                    if game_message.currentTeamId == game_message.teamZoneGrid[line][column]:
                        self.teamZone.append((line, column))

        grid = np.zeros((game_message.map.width, game_message.map.height))
        grid_size = (game_message.map.width, game_message.map.height)

        for wall in self.wall_positions:
            grid[wall] = -1

        for item in game_message.items:
            if item.type == "blitzium_core":
                grid[(item.position.x, item.position.y)] = 5
            elif item.type == "blitzium_ingot":
                grid[(item.position.x, item.position.y)] = 3
            elif item.type == "blitzium_nugget":
                grid[(item.position.x, item.position.y)] = 1
            elif item.type == "radiant_core":
                grid[(item.position.x, item.position.y)] = -5
            elif item.type == "radiant_slag":
                grid[(item.position.x, item.position.y)] = -2

        actions.extend(self.ramasseCaca(game_message, grid))

        #print(grid)
        # You can clearly do better than the random actions above! Have fun!
        return actions

    def ramasseCaca(self, game_message, grid):
        liste = []
        caca = (-5.0, -2.0)

        """for row in grid:
            for space in row:
                print(space)
                if space == -5:
                    if space in self.teamZone:

                        liste.append(MoveToAction(characterId = game_message.character.id, position = space))
                        liste.append(GrabAction(characterId = game_message.character.id))"""

        list_caca = list(zip(*np.where(grid <= -2)))
        list_to_clean = []
        for caca_pos in list_caca:

            if caca_pos in self.teamZone:
                list_to_clean.append(caca_pos)

        numeric_values = [(tuple(map(lambda x: x.item(), pair[0])), pair[1].item()) for pair in list_to_get]

        for caca in list_to_clean:
            for character in game_message.yourCharacters:
                liste.append(MoveToAction(characterId = character.id, position = caca))
                liste.append(GrabAction(characterId = character.id))


        return liste


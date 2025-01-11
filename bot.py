import heapq
import math
import random

import game_message
from game_message import *
import numpy as np
from game_message import *

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self.wall_positions = []
        self.teamZone = []
        self.enemy_positions = []
        self.enemyZone = []

    def get_next_move(self, game_message: TeamGameState):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []
        characters_with_actions = set()  # Track which characters have assigned actions

        if game_message.tick == 1:
            # Initialize map information on the first tick
            for line in range(len(game_message.map.tiles)):
                for column in range(len(game_message.map.tiles[line])):
                    if game_message.map.tiles[line][column] == TileType.WALL:
                        self.wall_positions.append((line, column))

            for line in range(len(game_message.map.tiles)):
                for column in range(len(game_message.map.tiles[line])):
                    if game_message.currentTeamId == game_message.teamZoneGrid[line][column]:
                        self.teamZone.append((line, column))

        # Initialize grid and set up enemy positions
            enemies = game_message.otherCharacters
            for line in range(len(game_message.map.tiles)):
                for column in range(len(game_message.map.tiles[line])):
                    if enemies[0].teamId == game_message.teamZoneGrid[line][column]:
                        self.enemyZone.append((line, column))



        grid = np.zeros((game_message.map.width, game_message.map.height))
        grid_size = (game_message.map.width, game_message.map.height)

        for wall in self.wall_positions:
            grid[wall] = -1

        for character in game_message.otherCharacters:
            self.enemy_positions.append((character.position.x, character.position.y))

        #print(self.enemy_positions)
        for enemy in self.enemy_positions:
            grid[enemy] = -10  # Mark enemies as obstacles

        # Set grid values based on item types
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

        blitzium_items = []
        for item in game_message.items:
            if item.type == "blitzium_core":
                blitzium_items.append((item.position.x, item.position.y))
            elif item.type == "blitzium_ingot":
                blitzium_items.append((item.position.x, item.position.y))
            elif item.type == "blitzium_nugget":
                blitzium_items.append((item.position.x, item.position.y))

        #A* pathfinding with enemy avoidance

        def a_star_search(start, goal, grid, grid_size):
            open_set = []
            heapq.heappush(open_set, (0, start))

            # Dictionaries for tracking paths
            came_from = {}
            g_score = {start: 0}
            f_score = {start: heuristic(start, goal)}

            while open_set:
                # Get the node with the lowest f_score
                _, current = heapq.heappop(open_set)

                # If we reach the goal, reconstruct the path
                if current == goal:
                    return reconstruct_path(came_from, current)

                x, y = current
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor = (x + dx, y + dy)
                    if 0 <= neighbor[0] < grid_size[0] and 0 <= neighbor[1] < grid_size[1]:
                        if grid[neighbor[0]][neighbor[1]] == -1:
                            continue  # Skip walls and enemies

                        tentative_g_score = g_score[current] + 1
                        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))

            return None  # No valid path found

        # Heuristic function for A* (Manhattan distance)
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # Reconstruct the path from the A* search
        def reconstruct_path(came_from, current):
            total_path = [current]
            while current in came_from:
                current = came_from[current]
                total_path.append(current)
            total_path.reverse()
            return total_path

        # Collecting blitzium and avoiding enemies
        nb_char_gather = len(game_message.yourCharacters)

        list_blitzium = list(zip(*np.where(grid >= 1)))
        list_to_get = []
        for blitzium_pos in list_blitzium:
            if blitzium_pos not in self.teamZone:
                list_to_get.append((blitzium_pos, grid[blitzium_pos]))

        list_caca = list(zip(*np.where(grid <= -2)))

        list_to_clean = []
        for caca_pos in list_caca:
            if caca_pos in self.teamZone:
                list_to_clean.append(caca_pos)

        numeric_caca = [(pair[0].item(), pair[1].item()) for pair in list_to_clean]

        numeric_values = [(tuple(map(lambda x: x.item(), pair[0])), pair[1].item()) for pair in list_to_get]

        for character in game_message.yourCharacters:
            somme = 0
            if character.id in characters_with_actions:
                continue  # Skip this character if it already has an action
            for item in character.carriedItems:
                somme += item.value

            if len(numeric_caca) > 0 or somme < 0:
                for character in game_message.yourCharacters:
                    position = (character.position.x, character.position.y)
                    if len(character.carriedItems) == 1:
                        if position in self.enemyZone and grid[position] == 0:
                            for char in game_message.yourCharacters:
                                if character.id == char.id:
                                    continue
                                if char.position == character.position:
                                    actions.append(random.choice([
                                        MoveLeftAction(characterId=character.id),
                                        MoveUpAction(characterId=character.id),
                                        MoveRightAction(characterId=character.id),
                                        MoveDownAction(characterId=character.id)
                                        ]
                                    ))
                                    characters_with_actions.add(character.id)
                                else:
                                    actions.append(DropAction(characterId=character.id))
                                    characters_with_actions.add(character.id)

                        else:
                            for case in self.enemyZone:
                                if grid[case] == 0:
                                    path = a_star_search(position, case, grid, grid_size)
                                    if path and len(path) > 1:
                                        next_step = path[1]  # Move to the next position in the path
                                        actions.append(
                                            MoveToAction(characterId=character.id,
                                                         position=Position(next_step[0], next_step[1])))
                                        characters_with_actions.add(character.id)  # Mark the character as having an action
                                        break
                                    # actions.append(
                                    #     MoveToAction(characterId=character.id, position=Position(case[0], case[1])))
                                    # characters_with_actions.add(character.id)
                    elif grid[character.position.x, character.position.y] <= -2 and position in self.teamZone:
                        actions.append(GrabAction(characterId=character.id))
                        characters_with_actions.add(character.id)
                    else:
                        if numeric_caca:
                            for case in numeric_caca:
                                path = a_star_search(position, case, grid, grid_size)
                                if path and len(path) > 1:
                                    next_step = path[1]  # Move to the next position in the path
                                    actions.append(
                                        MoveToAction(characterId=character.id,
                                                     position=Position(next_step[0], next_step[1])))
                                    characters_with_actions.add(character.id)  # Mark the character as having an action
                                    break
                            # actions.append(MoveToAction(characterId=character.id,
                            #                           position=Position(numeric_caca[0][0], numeric_caca[0][1])))
                            # characters_with_actions.add(character.id)
            else:

                position = (character.position.x, character.position.y)

                if len(character.carriedItems) == 1:
                    # Carrying an item, need to go back to base
                    if position in self.teamZone and grid[position] == 0:
                        actions.append(DropAction(characterId=character.id))
                        characters_with_actions.add(character.id)  # Mark the character as having an action
                    else:
                        for case in self.teamZone:
                            if grid[case] == 0:
                                path = a_star_search(position, case, grid, grid_size)
                                if path and len(path) > 1:
                                    next_step = path[1]  # Move to the next position in the path
                                    actions.append(
                                        MoveToAction(characterId=character.id,
                                                     position=Position(next_step[0], next_step[1])))
                                    characters_with_actions.add(character.id)  # Mark the character as having an action
                                    break
                                # actions.append(MoveToAction(characterId=character.id, position=Position(case[0], case[1])))
                                # characters_with_actions.add(character.id)  # Mark the character as having an action
                                # break

                if grid[character.position.x, character.position.y] > 0 and position not in self.teamZone:
                    actions.append(GrabAction(characterId=character.id))
                    characters_with_actions.add(character.id)  # Mark the character as having an action
                else:
                    if numeric_values:

                        closest_position = numeric_values[0]
                        for value in numeric_values:
                            close = math.sqrt(closest_position[0][0]**2 + closest_position[0][1]**2)
                            new = math.sqrt(value[0][0]**2 + value[0][1]**2)

                            if new < close:
                                closest_position = value

                        destination = closest_position[0]

                        path = a_star_search(position, destination, grid, grid_size)
                        if path and len(path) > 1:
                            next_step = path[1]  # Move to the next position in the path
                            actions.append(
                                MoveToAction(characterId=character.id, position=Position(next_step[0], next_step[1])))
                            characters_with_actions.add(character.id)  # Mark the character as having an action

        print(actions)
        return actions

    def ramasseCaca(self, game_message, grid):
        liste = []


        #print(grid)
        list_caca = list(zip(*np.where(grid <= -2)))

        list_to_clean = []
        for caca_pos in list_caca:
            #print(caca_pos) #caca_pos: list64
            if caca_pos in self.teamZone:
                list_to_clean.append(caca_pos)

        numeric_values = [(pair[0].item(), pair[1].item()) for pair in list_to_clean]

        #Aller au caca
        # for character in game_message.yourCharacters:
            # liste.append(MoveToAction(characterId = character.id, position=Position(numeric_values[0][0], numeric_values[0][1])))

        #AJOUTER UN MESSAGE DERREUR S'IL NY A PAS D'OBJET À PICKUP
        print(self.enemyZone)
        for character in game_message.yourCharacters:
            position = (character.position.x, character.position.y)
            if len(character.carriedItems) == 1:
                if position in self.enemyZone and grid[position] == 0:
                    liste.append(DropAction(characterId=character.id))
                else:
                    for case in self.enemyZone:
                        if grid[case] == 0:
                            liste.append(MoveToAction(characterId=character.id, position=Position(case[0], case[1])))

            if grid[character.position.x, character.position.y] <= -2 and position in self.teamZone:
                liste.append(GrabAction(characterId=character.id))
            else:
                if numeric_values:
                    liste.append(MoveToAction(characterId=character.id,
                                              position=Position(numeric_values[0][0], numeric_values[0][1])))
                    # destination = numeric_values[0][0]
                    # path = a_star_search(position, destination, grid, grid_size)
                    # if path and len(path) > 1:
                    #     next_step = path[1]  # Move to the next position in the path
                    #     actions.append(
                    #         MoveToAction(characterId=character.id, position=Position(next_step[0], next_step[1])))

        #
        # for character in game_message.yourCharacters:
        #
        #     position_char = (character.position.x, character.position.y)
        #     if len(character.carriedItems) == 0 and grid[position_char] >= 0:
        #         liste.append(MoveToAction(characterId=character.id,
        #                                   position=Position(numeric_values[0][0], numeric_values[0][1])))
        #     elif position_char in self.teamZone and grid[position_char] <= -2:
        #         liste.append(GrabAction(characterId = character.id))
        #
        #     print(self.enemyZone[0])
        #     if character.numberOfCarriedItems == 1 and grid[position_char] == 0:
        #        liste.append(MoveToAction(characterId = character.id, position = self.enemyZone[0]))
            # if len(character.carriedItems) == 1 and grid[position_char] >= 0:
            #     liste.append(MoveToAction(characterId = character.id, position = self.enemyZone[1]))

        #Sortir le caca de la zone

        return liste


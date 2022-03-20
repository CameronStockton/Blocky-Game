"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    lst = []
    num_used = []
    num1 = random.randint(0, 1)
    while len(lst) < num_goals:
        num2 = random.randint(0, len(COLOUR_LIST)-1)
        #This ensures the number is not used again
        while num2 in num_used:
            num2 = random.randint(0, len(COLOUR_LIST)-1)
        num_used.append(num2)
        if num1 == 0:
            lst.append(PerimeterGoal(COLOUR_LIST[num2]))
        else:
            lst.append(BlobGoal(COLOUR_LIST[num2]))
            
    return lst

def _make_list_blocks(block: Block) \
    -> List[Tuple[int, int], Tuple[int, int, int]]:
    """ Returns a list of positions and colours for this 
    block and each child in the block in unit cells """
    if not block.colour is None and block.level == block.max_depth:
        return [[block.position, block.colour]]
    elif not block.colour is None:
        units = 2**(block.max_depth - block.level)
        init_pos = list(block.position)
        L = []
        unit_size = round(block.size/units)
        i = 0
        while i < units:
            j = 0
            while j < units:
                new_pos_x = init_pos[0] + i*unit_size
                new_pos_y = init_pos[1] + j*unit_size
                new_pos = (new_pos_x, new_pos_y)
                L.append([new_pos, block.colour])
                j += 1
            i += 1
        return L
    else:
        J = []
        for child in block.children:
            J.extend(_make_list_blocks(child))
        return J

def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    lst = _make_list_blocks(block)
    sorted_lst = sorted(lst, key=lambda lst: lst[0][0])
    L = []
    units = 2**(block.max_depth)
    l = 0
    while l < units:
        L.append([])
        l += 1
    i = 0
    while i < units:
        j = 0
        while j < units:
            a = sorted_lst.pop(0)
            L[i].append(a[1])
            j += 1
        i += 1
    return L


'''for i in range(units):
                I = []
                for j in range(units):
                    I.append(block.colour)
                L.append(I)
            return L'''

class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """ A child class of Goal where filling the perimeter is the objective """
    def score(self, board: Block) -> int:
        """ Find score based on parameter of PerimeterGoal """
        #Important to note that the perimeter only consists of the first
        #column and row and the last column and row
        copy = board.create_copy()
        copy_flat = _flatten(copy)
        max_ = len(copy_flat[0])
        j = 0
        score = 0
        #Count first column
        while j < max_:
            if copy_flat[0][j] == self.colour:
                score += 1
                j += 1
            else:
                j += 1
                
        j = 0
        #Count last column
        while j < max_:
            if copy_flat[max_-1][j] == self.colour:
                score += 1
                j += 1
            else:
                j += 1
                
        i = 0
        #Count first row
        while i < max_:
            if copy_flat[i][0] == self.colour:
                score += 1
                i += 1
            else:
                i += 1
                
        i = 0
        #Count last row
        while i < max_:
            if copy_flat[i][max_-1] == self.colour:
                score += 1
                i += 1
            else:
                i += 1
        
        return score

    def description(self) -> str:
        """ Describe what the objective is """
        col_name = colour_name(self.colour)
        return 'Fill the perimeter with ' + col_name


class BlobGoal(Goal):
    """ A child class of Goal where getting the largest amount of touching 
    unit colours """
    def score(self, board: Block) -> int:
        """ Find score based on parameter of BlobGoal """
        copy = board.create_copy()
        copy_flat = _flatten(copy)
        visited = []
        i = 0
        while i < len(copy_flat):
            col = []
            j = 0
            while j < len(copy_flat[i]):
                col.append(-1)
                j += 1
            visited.append(col)
            i += 1
        pos = []
        x = 0
        while x < len(copy_flat):
            y = 0
            while y < len(copy_flat[x]):
                if copy_flat[x][y] == self.colour:
                    pos.append((x, y))
                y += 1
            x += 1
        score = 0
        for p in pos:
            new_score = self._undiscovered_blob_size(p, copy_flat, visited)
            if new_score > score:
                score = new_score

        return score

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        #Pos is given as position in flattened board
        #If board[pos[0]][pos[1]] not colour return 0
        #if pos not in board return 0 (check sizes)
        x = pos[0]
        y = pos[1]
        #Now go through board
        if not x in range(0, len(board)) and not y in range(0, len(board)):
            return 0
        elif visited[x][y] != -1:
            return 0
        elif board[x][y] != self.colour:
            visited[x][y] = 0
            return 0
        else:
            #we know that this pos will be the colour and will be unvisited
            score = 1
            visited[x][y] = 1
            if x > 0:
                score += self._undiscovered_blob_size((x-1, y), board, visited)
            if x < len(board[x])-1:
                score += self._undiscovered_blob_size((x+1, y), board, visited)
            if y > 0:
                score += self._undiscovered_blob_size((x, y-1), board, visited)
            if y < len(board[y])-1:
                score += self._undiscovered_blob_size((x, y+1), board, visited)
            return score




    def description(self) -> str:
        """ Describe what the objective is """
        col_name = colour_name(self.colour)
        return 'Make the biggest blob with ' + col_name


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })

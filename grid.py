import math

from color import Color as color

class Grid:
    HEIGHT = 20
    WIDTH = 10

    def __init__(self):
        self.grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
        self.score = 0

    def __repr__(self):
        """visual of the tetris game state"""
        s = ""
        for row in self.grid:
            for rgb in row:
                if rgb == (0, 0, 0):
                    s += '.'
                elif rgb == (0, 255, 0):
                    s += color.GREEN + '0' + color.END
                elif rgb == (0, 0, 255):
                    s += color.BLUE + '0' + color.END
                elif rgb == (255, 255, 0):
                    s += color.YELLOW + '0' + color.END
                elif rgb == (0, 255, 255):
                    s += color.CYAN + '0' + color.END
                elif rgb == (128, 0, 128):
                    s += color.PURPLE + '0' + color.END
                elif rgb == (255, 165, 0):
                    s += color.DARKCYAN + '0' + color.END
                else:
                    s += color.RED + '0' + color.END
            s += '\n'
        return s

    @staticmethod
    def normalize(lst):
        return [float(i) / max(lst) for i in lst]

    def draw(self, piece, erase=False):
        """draws a piece to the grid"""
        for i, row in enumerate(piece.get_shape()):
            for j, block in enumerate(row):
                if block == '0':
                    j_off = piece.get_offset('left')
                    i_off = piece.get_offset('up')
                    if not erase:
                        self.grid[i - i_off + piece.y][j - j_off + piece.x] = piece.color
                    else:
                        self.grid[i - i_off + piece.y][j - j_off + piece.x] = (0, 0, 0)

    def erase(self, piece):
        """erases a piece from the grid"""
        self.draw(piece, erase=True)

    def collides(self, piece):
        """returns true if the piece collides with another piece or is out of bounds"""
        for i, row in enumerate(piece.get_shape()):
            for j, block in enumerate(row):
                if block == '0':
                    x = j - piece.get_offset('left') + piece.x
                    y = i - piece.get_offset('up') + piece.y

                    if x < 0 or y < 0:
                        return True
                    try:
                        if self.grid[y][x] != (0, 0, 0):
                            return True
                    except:
                        return True
        return False

    def __clear_row(self):
        """used by clear lines"""
        for row in self.grid:
            if (0, 0, 0) not in row:
                self.grid.remove(row)
                self.grid.insert(0, [(0, 0, 0) for _ in range(Grid.WIDTH)])
                return True
        return

    def clear_lines(self):
        """clears the full lines"""
        lines = 0
        for _ in range(4):
            if self.__clear_row():
                lines += 1
            else:
                return 1000 * lines * lines  # 1000 * lines * lines
        return 1000 * lines * lines


    def _get_column_heights(self):
        column_heights = []

        for column_num in range(Grid.WIDTH):
            column_height = 0
            height_found = False
            for row_num in range(Grid.HEIGHT):
                if self.grid[row_num][column_num] != (0, 0, 0) and not height_found:
                    column_height = Grid.HEIGHT - row_num
                    height_found = True
            column_heights.append(column_height)

        return column_heights

    def _get_height_differences(self, column_heights):
        height_differences = []

        for i in range(len(column_heights) - 1):
            height_differences.append(column_heights[i + 1] - column_heights[i])

        return height_differences

    def _get_holes(self):
        holes = []

        for column_num in range(Grid.WIDTH):
            column_holes = 0
            height_found = False
            for row_num in range(Grid.HEIGHT):
                if self.grid[row_num][column_num] != (0, 0, 0) and not height_found:
                    height_found = True
                if self.grid[row_num][column_num] == (0, 0, 0) and height_found:
                    column_holes += 1
            holes.append(column_holes)

        return holes

    def _get_complete_lines(self):
        complete_lines = 0
        for row in self.grid:
            if (0, 0, 0) in row:
                pass
            else:
                complete_lines += 1
        return complete_lines

    def get_inputs2(self):
        column_heights = self._get_column_heights()
        height_differences = self._get_height_differences(column_heights)
        holes = self._get_holes()

        max_height = [max(column_heights)]
        total_holes = [sum(holes)]
        return self.normalize(column_heights + height_differences + max_height + total_holes + holes)

    def get_inputs(self):
        total_holes = sum(self._get_holes())
        aggregate_height = sum(self._get_column_heights())
        bumpiness = 0
        for i in self._get_height_differences(self._get_column_heights()):
            bumpiness += math.fabs(i)
        complete_lines = self._get_complete_lines()
        return self.normalize([total_holes, complete_lines, aggregate_height, bumpiness])

    def get_final_states(self, piece):
        # old_grid = self.grid.copy()
        final_states_inputs = []
        final_states_spawn = []
        for r in range(len(piece.shapes)):
            piece.rotation = r
            for x in range(Grid.WIDTH - piece.get_length() + 1):
                piece.x = x
                piece.y = 0
                # self.grid = old_grid.copy()
                while not self.collides(piece):
                    piece.y += 1
                piece.y -= 1
                # self.clear_lines()
                if not (piece.y < 0): # and not (piece.y < 4 and piece.x >= 5-piece.y-1 and piece.x <= 5+piece.y+1):
                    self.draw(piece)
                    final_states_spawn.append((x, 0, r))
                    final_states_inputs.append(self.get_inputs())
                    self.erase(piece)
                # clear_output(wait=True)
                # print(grid)
                # print(grid.get_inputs())
                # sleep(0.2)
        # self.grid = old_grid.copy()
        return (final_states_inputs, final_states_spawn)

    def game_over(self):
        for rgb in self.grid[2]:
            if rgb != (0, 0, 0):
                return True
        return False
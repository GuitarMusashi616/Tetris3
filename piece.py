from constants import OFFSET_LEFT, OFFSET_RIGHT, OFFSET_UP, OFFSET_DOWN, SHAPES, SHAPE_COLORS
from option import Option


class Piece:
    def __init__(self, x, y, shapes):
        self.shapes = shapes
        self.rotation = 0
        self.x = x
        self.y = y
        self.color = SHAPE_COLORS[SHAPES.index(shapes)]

    def __repr__(self):
        s = ""
        for row in self.shapes[self.rotation]:
            for block in row:
                s += block
            s += '\n'
        return s

    def get_shape(self):
        return self.shapes[self.rotation]

    def get_offset(self, direction):
        if direction == 'left':
            return OFFSET_LEFT[SHAPES.index(self.shapes)][self.rotation]
        elif direction == 'right':
            return OFFSET_RIGHT[SHAPES.index(self.shapes)][self.rotation]
        elif direction == 'up':
            return OFFSET_UP[SHAPES.index(self.shapes)][self.rotation]
        elif direction == 'down':
            return OFFSET_DOWN[SHAPES.index(self.shapes)][self.rotation]
        else:
            raise Exception("direction must be 'left', 'right', 'up', or 'down'")

    def drop(self, grid):
        while not grid.collides(self):
            self.y += 1
        self.y -= 1

    def down(self, grid):
        self.y += 1
        if grid.collides(self):
            self.y -= 1
            return True
        return False

    def left(self, grid):
        self.x -= 1
        if grid.collides(self):
            self.x += 1
            return True
        return False

    def right(self, grid):
        self.x += 1
        if grid.collides(self):
            self.x -= 1
            return True
        return False

    def cw(self, grid):
        self.rotation += 1
        if grid.collides(self):
            self.rotation -= 1
            return True
        return False

    def ccw(self, grid):
        self.rotation -= 1
        if grid.collides(self):
            self.rotation += 1
            return True
        return False

    def get_length(self):
        return 5 - self.get_offset('left') - self.get_offset('right')

    def get_width(self):
        return 5 - self.get_offset('up') - self.get_offset('down')

    def get_options(self, grid):
        options = []
        # check CW_ROTATE
        self.rotation += 1
        if not grid.collides(self):
            options.append(Option.CW_ROTATE)
        self.rotation -= 1
        # check CCW_ROTATE
        self.rotation -= 1
        if not grid.collides(self):
            options.append(Option.CCW_ROTATE)
        self.rotation += 1
        # check LEFT
        self.x -= 1
        if not grid.collides(self):
            options.append(Option.LEFT)
        self.x += 1
        # check RIGHT
        self.x += 1
        if not grid.collides(self):
            options.append(Option.RIGHT)
        self.x -= 1
        # check DOWN
        self.y += 1
        if not grid.collides(self):
            options.append(Option.DOWN)
        self.y -= 1
        # check DROP
        if not grid.collides(self):
            options.append(Option.DROP)
        return options

    def do_option(self, option, grid):
        if option == Option.CW_ROTATE:
            return self.cw(grid)
        elif option == Option.CCW_ROTATE:
            return self.ccw(grid)
        elif option == Option.LEFT:
            return self.left(grid)
        elif option == Option.RIGHT:
            return self.right(grid)
        elif option == Option.DOWN:
            return self.down(grid)
        elif option == Option.DROP:
            self.drop(grid)
            return True

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @x.setter
    def x(self, x):
        # self.__x = numpy.clip(x,0,Grid.WIDTH-self.length)
        self.__x = x

    @y.setter
    def y(self, y):
        # self.__y = numpy.clip(y,0,Grid.HEIGHT-self.width
        self.__y = y

    @property
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self, r):
        self.__rotation = r % len(self.shapes)
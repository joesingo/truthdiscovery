class Entity:
    """
    Class to represent an abstract entity that can be drawn
    """
    def __init__(self, x=None, y=None, colour=None):
        self.x = x
        self.y = y
        self.colour = colour


class Rectangle(Entity):
    def __init__(self, width=None, height=None, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height


class Circle(Entity):
    def __init__(self, radius=None, label=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.label = label


class Line(Entity):
    def __init__(self, end_x=None, end_y=None, width=None, dashed=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.end_x = end_x
        self.end_y = end_y
        self.width = width
        self.dashed = dashed


class Label(Entity):
    def __init__(self, text=None, size=None, overflow_background=None,
                 **kwargs):
        """
        :param text:   text to draw
        :param size:   size (backend specific units)
        :param overflow_background: if the label is associated with another
                                    entity and exceeds its bounds, draw the
                                    label in a box with this background
        """
        # Note: coordinates of label are the coordinates of the *centre*
        super().__init__(**kwargs)
        self.text = text
        self.size = size
        self.overflow_background = overflow_background

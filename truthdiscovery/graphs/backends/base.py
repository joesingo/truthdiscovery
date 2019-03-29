class BaseBackend:
    """
    Class to represent a method of drawing a list of :any:`Entity` objects to
    a file
    """
    def draw_entities(self, entities, outfile, width, height):
        """
        :param entities: an iterable of :any:`Entity` objects
        :param outfile:  file object to write to
        :param width:    width of image in px
        :param height:   height of image in px
        """
        raise NotImplementedError("Must be implemented in child classes")

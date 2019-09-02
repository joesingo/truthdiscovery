import math

import cairo

from truthdiscovery.graphs.backends.base import BaseBackend
from truthdiscovery.graphs.entities import Rectangle, Circle, Line


class PngBackend(BaseBackend):
    """
    Draw an image as a PNG using Cairo
    """
    def draw_entities(self, entities, outfile, width, height):
        # Initialise Cairo
        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, width, height
        )
        ctx = cairo.Context(surface)

        for ent in entities:
            ctx.set_source_rgba(*ent.colour)
            if isinstance(ent, Rectangle):
                ctx.rectangle(ent.x, ent.y, ent.width, ent.height)
                ctx.fill()

            if isinstance(ent, Circle):
                ctx.arc(ent.x, ent.y, ent.radius, 0, 2 * math.pi)
                ctx.fill()
                if ent.label is not None:
                    self.draw_label(ctx, ent.label, 2 * ent.radius, width)

            elif isinstance(ent, Line):
                if ent.dashed:
                    ctx.set_dash([10])  # TODO: configure dash size somehow
                else:
                    ctx.set_dash([])
                ctx.set_line_width(ent.width)
                ctx.move_to(ent.x, ent.y)
                ctx.line_to(ent.end_x, ent.end_y)
                ctx.stroke()

        surface.write_to_png(outfile)

    def draw_label(self, ctx, label, max_width, image_width):
        ctx.set_font_size(label.size)
        ext = ctx.text_extents(label.text)
        # Make sure long source or var names do not run off the screen
        label_lhs = min(image_width - ext.width, label.x - ext.width / 2)
        label_lhs = max(0, label_lhs)

        # If label exceeds the node, draw a background-coloured box where text
        # will go, so that the label does not clash with background/node border
        if ext.width > max_width:
            r, g, b = label.overflow_background
            ctx.set_source_rgba(*label.overflow_background)
            # Try and have label an 'opposite' colour for label to avoid
            # clashing
            label.colour = (1 - r, 1 - g, 1 - b)

            padding = 5  # allow some space between box border and text
            ctx.rectangle(
                label_lhs - padding,
                label.y - ext.height / 2 - padding,
                ext.width + 2 * padding,
                ext.height + 2 * padding
            )
            ctx.fill()

        ctx.set_source_rgba(*label.colour)
        ctx.move_to(label_lhs, label.y - ext.y_bearing / 2)
        ctx.show_text(label.text)

/*
 * Object to handle drawing a graph to a canvas from a JSON description
 */
function GraphDrawer() {
    this.canvas = null;
    this.ctx = null;
};

/*
 * Retrieve the <canvas> element and create a context
 */
GraphDrawer.prototype.grab_canvas = function() {
    if (this.canvas === null) {
        this.canvas = document.getElementById("graph-canvas");
        this.ctx = this.canvas.getContext("2d");
    }
};

/*
 * Draw the given JSON graph to the canvas
 */
GraphDrawer.prototype.draw_graph = function(obj) {
    this.canvas.width = obj.width;
    this.canvas.height = obj.height;
    this.ctx.textBaseline = "middle";

    for (var i=0; i<obj.entities.length; i++) {
        var ent = obj.entities[i];
        var this_colour = this.get_colour_string(ent.colour);

        switch (ent.type) {
            case "circle":
                this.ctx.fillStyle = this_colour
                this.ctx.beginPath();
                this.ctx.arc(ent.x, ent.y, ent.radius, 0, 2 * Math.PI);
                this.ctx.fill();

                if (ent.label !== null) {
                    this.draw_label(ent.label, 2 * ent.radius, obj.width);
                }
                break;

            case "rectangle":
                this.ctx.fillStyle = this_colour
                this.ctx.fillRect(ent.x, ent.y, ent.width, ent.height);
                break;

            case "line":
                this.ctx.strokeStyle = this_colour
                this.ctx.lineWidth = ent.width;
                this.ctx.beginPath();
                this.ctx.moveTo(ent.x, ent.y);
                this.ctx.lineTo(ent.end_x, ent.end_y);
                this.ctx.stroke();
                break;
        }
    }
};

/*
 * Draw a label for a node.
 *
 * The code is essentially the same as the Python code in png_backend.py
 */
GraphDrawer.prototype.draw_label = function(label, max_width, canvas_width) {
    this.ctx.font = "normal " + label.size + "px Arial";
    var text_metrics = this.ctx.measureText(label.text);
    var label_lhs = Math.min(
        canvas_width - text_metrics.width,
        label.x - text_metrics.width / 2
    );
    label_lhs = Math.max(0, label_lhs);

    var label_c = label.colour;
    if (text_metrics.width > max_width) {
        var r = label.overflow_background[0];
        var g = label.overflow_background[1];
        var b = label.overflow_background[2];
        label_c = [1 - r, 1 - g, 1 - b];

        this.ctx.fillStyle = this.get_colour_string(label.overflow_background);
        var padding = 5
        this.ctx.fillRect(
            label_lhs - padding,
            label.y - label.size / 2 - padding,
            text_metrics.width + 2 * padding,
            label.size + 2 * padding
        );
    }

    this.ctx.fillStyle = this.get_colour_string(label_c);
    this.ctx.fillText(label.text, label_lhs, label.y);
};

/*
 * Return a string 'rgb(r, g, b)' from an array of RGB values in [0, 1]
 */
GraphDrawer.prototype.get_colour_string = function(colour_array) {
    var r = colour_array[0] * 255;
    var g = colour_array[1] * 255;
    var b = colour_array[2] * 255;
    return "rgb(" + r + ", " + g + ", " + b + ")";
};

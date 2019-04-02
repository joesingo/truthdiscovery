function Animator(onstop) {
    this.drawer = new GraphDrawer();
    this.frames = null;
    this.current_frame = null;
};

Animator.prototype.load = function(obj) {
    this.drawer.grab_canvas("animation-canvas");
    this.frames = obj.frames;
    // Draw first frame
    this.current_frame = 0;
    this.redraw();
};

Animator.prototype.redraw = function() {
    if (this.frames === null) {
        return;
    }
    var frame_obj = this.frames[this.current_frame];
    this.drawer.draw_graph(this.frames[this.current_frame]);
}

Animator.prototype.previousFrame = function() {
    this.setFrame(this.current_frame - 1);
}

Animator.prototype.nextFrame = function() {
    this.setFrame(this.current_frame + 1);
}

Animator.prototype.setFrame = function(new_frame) {
    if (this.frames === null) {
        return;
    }
    this.current_frame = Math.max(0, Math.min(new_frame, this.frames.length - 1));
    this.redraw();
}

import sys
import platform


def bind_mousewheel_to_children(parent_widget, scrollable_frame):
    """Recursively bind mouse wheel events to all children of a parent widget,
    so that scrolling over child widgets still scrolls the CTkScrollableFrame.

    This is needed because CTkScrollableFrame only binds <MouseWheel> on its
    internal canvas, not on child widgets. On macOS, child widgets like CTkButton
    or CTkLabel consume the event and it never reaches the canvas.
    """
    canvas = scrollable_frame._parent_canvas

    for child in parent_widget.winfo_children():
        child.bind("<MouseWheel>", lambda e, c=canvas: _forward_mousewheel(e, c), add="+")
        if sys.platform.startswith("linux"):
            child.bind("<Button-4>", lambda e, c=canvas: c.yview_scroll(-3, "units"), add="+")
            child.bind("<Button-5>", lambda e, c=canvas: c.yview_scroll(3, "units"), add="+")
        bind_mousewheel_to_children(child, scrollable_frame)


def _forward_mousewheel(event, canvas):
    """Forward mouse wheel event to canvas."""
    # macOS trackpad gives delta ~±1-2, macOS mouse gives ±120, Windows gives ±120
    if abs(event.delta) >= 120:
        canvas.yview_scroll(int(-1 * event.delta / 120), "units")
    else:
        canvas.yview_scroll(int(-1 * event.delta), "units")

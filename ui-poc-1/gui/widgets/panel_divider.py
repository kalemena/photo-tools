import customtkinter as ctk


class PanelDivider(ctk.CTkFrame):
    """A draggable vertical divider between two panels in a grid layout.

    Place this in its own grid column between the left and right panels.
    Drag it to resize adjacent columns.
    """

    def __init__(self, master, left_col, right_col, divider_width=6):
        super().__init__(master, width=divider_width, cursor="sb_h_double_arrow")
        self.left_col = left_col
        self.right_col = right_col

        self.configure(fg_color=("gray65", "gray40"))

        self._start_x = 0
        self._left_weight = 1
        self._right_weight = 1

        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._end_drag)

    def _start_drag(self, event):
        self._start_x = event.x_root
        self._left_weight = self.master.grid_columnconfigure(self.left_col)["weight"]
        self._right_weight = self.master.grid_columnconfigure(self.right_col)["weight"]

    def _on_drag(self, event):
        delta = event.x_root - self._start_x
        if delta == 0:
            return

        total = max(1, self._left_weight + self._right_weight)

        # Estimate: 1 weight unit ~ (window_width / total_weight) pixels
        # Convert pixel delta to weight delta
        win_w = max(1, self.master.winfo_width())
        weight_delta = delta * total / win_w

        new_left = max(1, self._left_weight + weight_delta)
        new_right = max(1, self._right_weight - weight_delta)

        # Re-normalise to preserve original total
        scale = total / (new_left + new_right)
        new_left *= scale
        new_right *= scale

        self.master.grid_columnconfigure(self.left_col, weight=int(round(new_left)))
        self.master.grid_columnconfigure(self.right_col, weight=int(round(new_right)))

    def _end_drag(self, event):
        pass

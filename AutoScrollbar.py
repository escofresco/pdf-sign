import tkinter as tk

class AutoScrollbar(tk.Scrollbar):
    """
    Subclass tkinter.Scrollbar to hide itself when scrollbar is unnecessary.
    """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise(tk.TclError, "cannot use pack with this widget")
    def place(self, **kw):
        raise(tk.TclError, "cannot use place with this widget")

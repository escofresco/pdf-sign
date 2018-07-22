from AutoScrollbar import AutoScrollbar
from DrawCanvas import DrawCanvas
from PIL import Image, ImageTk, ImageDraw
from os import path, listdir
from tkinter import filedialog, font
import tkinter as tk
from utils import pdf_to_imgs

class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        canvas = DrawCanvas(parent=self.master)
        ## Track left and right control keys
        self.control_key_is_pressed = False # Manage "control" key down as a flag
        self.bind_all("<KeyPress-Control_L>", self.set_control_key_is_pressed)
        self.bind_all("<KeyRelease-Control_L>", self.set_control_key_is_pressed)
        self.bind_all("<KeyPress-Control_R>", self.set_control_key_is_pressed)
        self.bind_all("<KeyRelease-Control_R>", self.set_control_key_is_pressed)
        ### Respond to control-s -> save
        self.bind_all("<Key-s>", self.is_saveshortcut)
        ### Response to control-o -> open
        self.bind_all("<Key-o>", self.is_openshortcut)
        ### Reponse to control-z -> undo
        self.bind_all("<Key-z>", self.is_undoshortcut)

        self.__setup() # Handle standard setup
        #self.canvas = DrawCanvas(parent=self.master)

    def __setup(self):
        self.scale = self.screen_scale()
        self.master.tk.call('tk', 'scaling', self.scale)
        self.master.title("PDF Sign")
        self.custom_font = font.Font(family="Times", size=18)
        self.master.config(width=1800, height=2300) # 400 x 400
        self.__make_menu()
        self.__show_draw()
        #self.__make_canvas()

    def __make_menu(self):
        menu = tk.Menu(self, font=self.custom_font)

        ## Create "File" section of menu with
        file_cascade = tk.Menu(menu, tearoff=0, font=self.custom_font) # Dashed line is disabled
        file_cascade.add_command(label="Open", command=self.open) # Handle open behavior
        file_cascade.add_command(label="Save", command=self.save) # Handle save behavior
        file_cascade.add_separator() # Separator after "Open"
        file_cascade.add_command(label="Exit", command=self.master.quit) # Handle exit behavior
        menu.add_cascade(label="File", menu=file_cascade) # Add file to Menu

        ## Create "Edit" section
        edit_cascade = tk.Menu(menu, tearoff=0, font=self.custom_font) # Dashed line is disabled
        edit_cascade.add_command(label="Sign", command=self.draw) # Handle sign
        edit_cascade.add_separator() # Separator after "Undo"
        edit_cascade.add_command(label="Undo", command=self.undo) # Handle undo
        menu.add_cascade(label="Edit", menu=edit_cascade)

        ## Create "View" section
        view_cascade = tk.Menu(menu, tearoff=0, font=self.custom_font)
        view_cascade.add_command(label="Zoom In", command=self.zoom_in) # Handle zoom in
        view_cascade.add_command(label="Zoom Out", command=self.zoom_out) # Handle zoom out
        menu.add_cascade(label="View", menu=view_cascade)

        self.master.config(menu=menu) # Add menu to window

    def __show_draw(self):
        pass
        # self.canvas.mainloop()
        # self.mainloop()

    def __make_canvas(self):
        pass

    def is_saveshortcut(self, event):
        if self.control_key_is_pressed:
            # ctrl-s has been selected
            self.save() # Invoke save function

    def is_openshortcut(self, event):
        if self.control_key_is_pressed:
            # ctrl-o has been selected
            self.open() # Invoke open function

    def is_undoshortcut(self, event):
        if self.control_key_is_pressed:
            # ctrl-z has been selected
            self.undo() # Invoke undo function


    def set_control_key_is_pressed(self, event):
        if str(event.type) is "KeyPress":
            self.control_key_is_pressed = True
        elif str(event.type) is "KeyRelease":
            self.control_key_is_pressed = False

    def resize(self, event):
        size = (event.width, event.height)
        print(size)

    def screen_scale(self) -> float:
        """
        Returns scale of the screen the current window is on (width / height).
        """
        return self.master.winfo_screenwidth() / self.master.winfo_screenheight()

    def open(self):
        """
        Use file dialogue to navigate user to a pdf.
        """
        canvas.open()
        # Open dialogue to find pdf
        file = filedialog.askopenfilename(
            title="Select pdf",
            filetypes=[("PDF File", "*.pdf")],
            initialdir=path.dirname(__file__)
        )
        # Add pdf (as a sett of images) to window
        self.load_pdf(pdf_to_imgs(file))

    def save(self):
        file = filedialog.asksaveasfile(mode='w', defaultextension=".pdf")
        if file is None:
            # Dialog has been closed with "Cancel"
            return # Don't save
        try:
            self.canvas.save()
        except NameError:
            print("No canvas exists")

    def draw(self):
        """
        Manage draw behavior
        """
        print(float(self.master.tk.call('tk', 'scaling')))
        self.__show_draw()

    def undo(self):
        pass

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

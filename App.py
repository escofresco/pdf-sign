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

        #self.load_pdf(pdf_to_imgs("./sample.pdf"))

        self.__setup() # Handle standard setup

    def __setup(self):
        self.scale = self.screen_scale()
        self.master.tk.call('tk', 'scaling', self.scale)
        self.master.title("PDF Sign")
        self.custom_font = font.Font(family="Times", size=18)
        self.master.config(width=400, height=400) # 400 x 400
        self.__make_menu()
        self.__show_draw()
        #self.__make_canvas()

    def __make_menu(self):
        menu = tk.Menu(self, font=self.custom_font)

        ## Create "file" section of menu with
        file_cascade = tk.Menu(menu, tearoff=0, font=self.custom_font) # Dashed line is disabled
        file_cascade.add_command(label="Open", command=self.open) # Handle open behavior
        file_cascade.add_separator() # Separator after "Open"
        file_cascade.add_command(label="Exit", command=self.master.quit) # Handle exit behavior
        menu.add_cascade(label="File", menu=file_cascade) # Add file to Menu

        ## Create "sign" section
        menu.add_command(label="Sign", command=self.draw) # Handle sign behavior

        self.master.config(menu=menu) # Add menu to window

    def __show_draw(self):
        self.canvas = DrawCanvas(parent=self.master)
        self.canvas.mainloop()
        self.mainloop()

    def __make_canvas(self):


        self.imgA = Image.open("/home/jonasz/Developer/projects/pdf_sign/a.png")
        photoA = ImageTk.PhotoImage(self.imgA)

        scroll = AutoScrollbar(self.master)
        scroll.grid(row=0, column=1, sticky=tk.N+tk.S)
        canvas = tk.Canvas(self.master, yscrollcommand=scroll.set, bg='green')
        canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        scroll.config(command=canvas.yview)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        frame = tk.Frame(canvas, bg='blue')
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        rows = 5
        for i in range(1,rows):
            label = tk.Label(frame, image=photoA)
            label.image = photoA
            label.grid(row=i, column=0, sticky=tk.E+tk.W)


        canvas.create_window(0, 0, anchor=tk.NW, window=frame)

        frame.update_idletasks()

        canvas.config(scrollregion=canvas.bbox("all"))

        self.master.bind("<Configure>", self.resize)
        self.master.mainloop()

    def resize(self, event):
        size = (event.width, event.height)
        print(size)

    def screen_scale(self)->float:
        """
        Returns scale of the screen the current window is on (width / height).
        """
        return self.master.winfo_screenwidth() / self.master.winfo_screenheight()

    def open(self):
        """
        Use file dialogue to navigate user to a pdf.
        """
        # Open dialogue to find pdf
        file = filedialog.askopenfilename(
            title="Select pdf",
            filetypes=[("PDF File", "*.pdf")],
            initialdir=path.dirname(__file__)
        )
        # Add pdf (as a set of images) to window
        self.load_pdf(pdf_to_imgs(file))

    def draw(self):
        """
        Manage draw behavior
        """
        print(float(self.master.tk.call('tk', 'scaling')))
        self.__show_draw()

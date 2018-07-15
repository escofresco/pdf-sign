from AutoScrollbar import AutoScrollbar
from PIL import Image, ImageTk, ImageDraw
from platform import system
import tkinter as tk
from utils import pdf_images, pdf_to_imgs

class DrawCanvas(tk.Canvas):
    def __init__(self, image_dir=None, parent=None):
        self.system = system() # Store OS (Linux, Windows, Java)
        self.parent = parent
        self.pdf_images = {} # Track images on the canvas

        ## Horizontal scrollbar subclass AutoScrollbar
        self.horizontal_autoscroll = AutoScrollbar(self.parent, orient=tk.HORIZONTAL, width=16*2)
        self.horizontal_autoscroll['command'] = self.xview
        self.horizontal_autoscroll.grid(column=0, row=1, sticky=(tk.W,tk.E))

        ## Vertical scrollbar subclass AutoScrollbar
        self.vertical_autoscroll = AutoScrollbar(self.parent, orient=tk.VERTICAL, width=16*2)
        self.vertical_autoscroll['command'] = self.yview
        self.vertical_autoscroll.grid(column=1, row=0, sticky=(tk.N,tk.S))

        super().__init__(self.parent,
            scrollregion=(0, 0, 0, 0),
                yscrollcommand=self.vertical_autoscroll.set,
                xscrollcommand=self.horizontal_autoscroll.set)


        ## Add images of pdf pages to this canvas
        image_dir = pdf_to_imgs("duality.pdf")
        self.load_pdf_images(image_dir.name)

        line_img = Image.new("RGB", (1000, 1000), "#FFFFFF")
        img_draw = ImageDraw.Draw(line_img)

        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self.lastx, self.lasty = 0, 0

        self.bind("<Button-1>", self.xy)
        self.bind("<B1-Motion>", self.addLine)
        self.bind("<B1-ButtonRelease>", self.doneStroke)

        ## Handle mousewheel behavior
        if self.system == 'Linux':
            self.bind_all("<Button-4>", self._on_mousewheel)
            self.bind_all("<Button-5>", self._on_mousewheel)
        else:
            self.bind_all("<MouseWheel>", self._on_mousewheel)

        # Red box
        id = self.create_rectangle((10, 10, 30, 30), fill="red", tags=('palette', 'palettered'))
        self.tag_bind(id, "<Button-1>", lambda x: self.setColor("red"))

        # Blue box
        id = self.create_rectangle((10, 35, 30, 55), fill="blue", tags=('palette', 'paletteblue'))
        self.tag_bind(id, "<Button-1>", lambda x: self.setColor("blue"))

        # Black box
        id = self.create_rectangle((10, 60, 30, 80), fill="black", tags=('palette', 'paletteblack', 'paletteSelected'))
        self.tag_bind(id, "<Button-1>", lambda x: self.setColor("black"))

        id = self.create_rectangle((10, 85, 30, 105), fill="yellow", tags=('palette', 'paletteSelected'))
        self.tag_bind(id, "<Button-1>", self.clear)

        self.setColor('black') # Default color is black
        self.itemconfigure('palette', width=5)
        self.mainloop()

    def _on_mousewheel(self, event):
        """
        Respond to mechanical scroll events.
        """
        if self.system == 'Linux':
            # Handle linux specific behavior
            if event.num == 4:
                # Handle scroll up
                self.yview_scroll(-1, "units")
            elif event.num == 5:
                # Handle scroll down
                self.yview_scroll(1, "units")
        else:
            self.yview_scroll(-1*(event.delta/120), "units")

    def xy(self, event):
        self.lastx, self.lasty = self.canvasx(event.x), self.canvasy(event.y)

    def setColor(self, newcolor):
        self.color = newcolor
        self.dtag('all', 'paletteSelected')
        self.itemconfigure('palette', outline='white')
        self.addtag('paletteSelected', 'withtag', 'palette%s' % self.color)
        self.itemconfigure('paletteSelected', outline='#999999')

    def addLine(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        self.create_line((self.lastx, self.lasty, x, y), fill=self.color, width=5, tags='currentline')
        self.lastx, self.lasty = x, y

        img_draw.line([(self.lastx, self.lasty), (x, y)], fill=self.color, width=5)

    def doneStroke(self, event):
        self.itemconfigure('currentline', width=1)

    def clear(self, event):
        line_img.save("asdf.jpg")
        for tag in self.find_all():
            if tag > 4:
                self.delete(tag)

    def load_pdf_images(self, image_dir):
        """
        Render images on canvas from the given directory. (Images must be .ppm)

        :param String image_dir: Direcotory source of images.
        """
        images = pdf_images(image_dir)
        img_dim = [0, 0] # (width, height) of the collection of images
        for i, img in enumerate(images):
            # FIXME: Display images without keeping them in memory; could cause program failure
            self.pdf_images[i] = img # Keep images in memory
            if img.width() > img_dim[0]:
                img_dim[0] = img.width()
            img_dim[1] += img.height()
            self.create_image(0, img.height()*i, anchor=tk.NW, image=self.pdf_images[i])
        else:
            # Update canvas scrollregion to cover the full collection of images
            # in x and y directions
            self.config(scrollregion=(0, 0, img_dim[0], img_dim[1]))

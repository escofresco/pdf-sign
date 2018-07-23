from AutoScrollbar import AutoScrollbar
from PIL import Image, ImageTk, ImageDraw
from platform import system
import tkinter as tk
from utils import pdf_images, pdf_to_imgs, save_images_as_pdf

class DrawCanvas(tk.Canvas):
    def __init__(self, image_dir=None, parent=None):
        self.system = system() # Store OS (Linux, Windows, Java)
        self.parent = parent
        self.pdf_images = {} # Track images on the canvas

        # List of lists of tuples containing line coordinates ->
        # [[(x0, y0, x1, y1), ..., (x(n-1), y(n-1), xn, yn)], ...]
        self.lines = []
        self.current_stroke = [] # The current stroke; gets appended to self.lines when complete
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

        # Track the current stroke as a series of lines
        self.current_stroke.append((self.lastx, self.lasty, x, y)) # Track the current stroke
        self.lastx, self.lasty = x, y

        #self._draw_img.line([(self.lastx, self.lasty), (x, y)], fill=self.color, width=5)

    def doneStroke(self, event):
        self.itemconfigure('currentline', width=1)
        self.lines.append(self.current_stroke) # Stroke is complete; add to list of lines
        self.stroke = []

    def clear(self, event):
        # self.draw_img.save("asdf.jpg")
        # for tag in self.find_all():
        #     if tag > 4:
        #         self.delete(tag)
        self.save()

    def add_strokes_to_image(self, page_height):
        edited_pages = {}
        for stroke in self.lines:
            for line in stroke:
                page_num = self.coordinate_to_page((line[0], line[1]), page_height)
                page_dim = (self.pdf_images[page_num][1].width(), int(page_height))

                ## Check if this page has been edited already
                if page_num not in edited_pages:
                    # Create new entry in edited_pages
                    print(self.pdf_images[page_num][0])
                    temp_img = Image.open(self.pdf_images[page_num][0]) # create PIL Image from pdf image path
                    edited_pages[page_num] = {
                        'image': temp_img,
                        'image_draw': ImageDraw.Draw(temp_img) # Create PIL ImageDraw from PIL Image
                    }

                # Draw the line in this stroke
                # TODO: Handle line coordinates that go outside the page
                edited_pages[page_num]['image_draw'].line([(line[0], line[1]), (line[2], line[3])], fill='black', width=5)
        else:
            # Top-level loop is complete; Save every page.
            img_list = []
            for page_num, (img_path, _) in self.pdf_images.items():
                if page_num in edited_pages:
                    # Append the image that has been drawn on.
                    img_list.append(edited_pages[page_num]['image'])
                else:
                    # Append the un-edited image, which must be converted from
                    # TKinter PhotoImage to PIL Image
                    img_list.append(Image.open(self.pdf_images[page_num][0]))
            save_images_as_pdf(img_list, "test.pdf")

    def coordinate_to_page(self, coord, page_height):
        """
        :param tuple coord: (x, y)
        :returns int: The page number this coordinate is on. floor(y / page_count)
        """
        return int(coord[1] // page_height)

    def save(self):
        page_count = max(self.pdf_images.keys()) + 1 # The largest number + 1
        page_height = self.draw_img.height / page_count # Height of each page
        page_width = self.draw_img.width
        self.add_strokes_to_image(page_height)
        # for page in range(page_count):
        #     cur_y = page * page_height
        #     box = (0, cur_y, page_width, cur_y + page_height) # Size of current page
        #     temp = self.draw_img.crop(box) # Crop to current page size
        #     #asdf = self.pdf_images[page] #Image.open(self.pdf_images[page])
        #     #temp = asdf.paste(temp, (0,0)) # Paste temp onto current pdf page
        #     temp = self.pdf_images[page].paste(temp, (25,250))
        #     temp.save(str(page) + ".png")

    def load_pdf_images(self, image_dir):
        """
        Render images on canvas from the given directory. (Images must be .ppm)

        :param String image_dir: Directory source of images.
        """
        images = pdf_images(image_dir)
        img_dim = [0, 0] # (width, height) of the collection of images
        for i, (img_path, photo_img) in enumerate(images):
            # FIXME: Display images without keeping them in memory; could cause program failure
            self.pdf_images[i] = (img_path, photo_img) # Keep images in memory since tkinter doesn't do this automatically
            if photo_img.width() > img_dim[0]:
                img_dim[0] = photo_img.width()
            img_dim[1] += photo_img.height()
            self.create_image(0, photo_img.height()*i, anchor=tk.NW, image=self.pdf_images[i][1])
        else:
            # Update canvas scrollregion to cover the full collection of images
            # in x and y directions
            self.config(scrollregion=(0, 0, img_dim[0], img_dim[1]))

            # Create an image the size of the full collection of images to account
            # for any point where the user may want to draw
            self.draw_img = Image.new('RGBA', (img_dim[0], img_dim[1]), (250, 10, 0, 0))
            self._draw_img = ImageDraw.Draw(self.draw_img)

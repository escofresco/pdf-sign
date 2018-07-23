from os import listdir
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import re
from tempfile import TemporaryDirectory
import tkinter as tk

def pdf_to_imgs(src_pdf, first_page=None, last_page=None, res=300) -> TemporaryDirectory:
    """
    Converts a PDF page to Pillow Image

    :param PyPDF2.PdfFileReader src_pdf: PDF object.
    :param int first_page: Page number of first page in range.
    :param int last_page: Page number of last page in range
    :param int res: Resolution of returned image
                    in DPI.
    :returns str: The path to directory containing pdf images
    """
    dir = TemporaryDirectory()
    convert_from_path(src_pdf, dpi=res, output_folder=dir.name, fmt='ppm')
    return dir

def pdf_images(dir) -> tk.PhotoImage:
    """
    Convert images in a given directory to tk.PhotoImage objects using generator.

    :param String dir: The directory containing images
    :yields tuple: ("<img_path>", <PhotoImage>)
    """
    images = []
    files = listdir(dir)
    for img_name in sorted(files):
        if is_image(img_name):
            img_path = dir + '/' + img_name
            yield (img_path, ImageTk.PhotoImage(file=img_path))

def is_image(img_name)->bool:
    """
    Is the given string an image.
    """
    if re.search(r"\.(gif|jpg|jpeg|tiff|png|ppm)$", img_name) is not None:
        return True
    return False

def save_images_as_pdf(imgs, name):
    """
    Save a list of images as a PDF; each item in list gets one page.

    :param list imgs: PIL Images
    :param str name: File name of PDF.
    """
    assert name.endswith('.pdf') is True

    imgs[0].save(name, append_images=imgs[1:], save_all=True)

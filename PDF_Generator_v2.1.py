import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar, Radiobutton
from reportlab.lib import colors
import threading
from reportlab.lib.pagesizes import letter
from tkinter import Radiobutton, filedialog, messagebox
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import webbrowser
from tkinter import ttk
import base64
from image import logo_png
from io import BytesIO
import os
import ctypes
import sys
import win32event
import win32api
import winerror
from functools import partial
import tempfile

MAX_PAGES = 100000
MAX_PDFS = 100000

# Check if another instance is already running
mutex = win32event.CreateMutex(None, 1, "UniqueAppMutexName")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    tk.Tk().withdraw()
    messagebox.showerror("Error", "Another instance of the application is already running.")
    sys.exit(1)

def add_padding_to_pdf(filepath, target_size_kb):
    target_size_bytes = target_size_kb * 1024
    current_size = os.path.getsize(filepath)
    padding_needed = target_size_bytes - current_size
    if padding_needed > 0:
        with open(filepath, "ab") as f:
            f.write(b"\0" * padding_needed)


def open_link(event):
    webbrowser.open("https://sourceforge.net/u/aniketc007/profile")

def generate_pdfs():
    folder_path = entries[0].get()
    num_pages = entries[1].get()
    num_pdfs = entries[2].get()
    custom_text = entries[3].get()
    watermark_path = entries[4].get()

    desired_size_kb = entries[5].get() if len(entries) > 5 else ""

    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to save PDFs.")
        return
    
    # Default values for num_pages and num_pdfs
    if not num_pages:
        num_pages = 1
    if not num_pdfs:
        num_pdfs = 1

    try:
        num_pages = int(num_pages)
        num_pdfs = int(num_pdfs)
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
        return

    if num_pages <= 0 or num_pdfs <= 0:
        messagebox.showerror("Error", "Please enter numbers greater than 0.")
        return
    
    if num_pages > MAX_PAGES or num_pdfs > MAX_PDFS:
        messagebox.showerror("Error", f"Maximum number of pages/PDFs is {MAX_PAGES}.")
        return

    progress_bar["value"] = 0
    progress_bar["maximum"] = num_pdfs

    overlay.lift()
    progress_bar.lift()
    version_label.lift()

    def generate_pdf_thread():
        for i in range(num_pdfs):
            filename = f"{folder_path}/PDF_{i+1}.pdf"
            try:
                c = canvas.Canvas(filename, pagesize=letter)

                # Define page dimensions
                page_width, page_height = letter

                # Adding watermark to all pages if a watermark is provided
                if watermark_path and watermark_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img = Image.open(watermark_path)

                    # Apply color mode based on user selection
                    if color_mode_var.get() == "bw":
                        img = img.convert("L")  # Convert to grayscale for black and white
                    else:
                        img = img.convert("RGBA")  # Keep original color with alpha channel

                    img_width, img_height = img.size

                    # Adjust size of watermark image
                    max_size = 550  # Maximum dimension for watermark
                    if max(img_width, img_height) > max_size:
                        if img_width > img_height:
                            new_width = max_size
                            new_height = int(img_height * (max_size / img_width))
                        else:
                            new_height = max_size
                            new_width = int(img_width * (max_size / img_height))
                        img = img.resize((new_width, new_height), Image.LANCZOS)  # Use LANCZOS for resizing
                    else:
                        new_width, new_height = img_width, img_height

                    # Set transparency
                    img.putalpha(51)  # 20% transparency (255 * 0.2 = 51)

                    # Save resized watermark image to a temporary file
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                        temp_watermark_path = temp_file.name
                        img.save(temp_watermark_path)

                    # Loop through each page and draw watermark and text
                    for _ in range(num_pages):
                        # Draw watermark
                        x_offset = (page_width - new_width) / 2
                        y_offset = (page_height - new_height) / 2
                        c.drawImage(temp_watermark_path, x_offset, y_offset, width=new_width, height=new_height, mask='auto')

                        # Draw custom text if provided
                        if custom_text:
                            if placement_var.get() == 2:  # Custom placement
                                try:
                                    x = int(x_entry.get())
                                    y = int(y_entry.get())
                                except ValueError:
                                    messagebox.showerror("Error", "Please enter valid numbers for X and Y.")
                                    return
                            else:
                                x, y = 497, 125  # Default placement

                            c.drawString(x, y, custom_text)
                        c.showPage()

                    # Remove the temporary watermark file
                    os.remove(temp_watermark_path)

                elif watermark_path:
                    messagebox.showerror("Error", "Unsupported watermark file format.")
                    return
                else:
                    # No watermark provided, generate PDF without watermark
                    for _ in range(num_pages):
                        if custom_text:
                            if placement_var.get() == 2:  # Custom placement
                                try:
                                    x = int(x_entry.get())
                                    y = int(y_entry.get())
                                except ValueError:
                                    messagebox.showerror("Error", "Please enter valid numbers for X and Y.")
                                    return
                            else:
                                x, y = 497, 125  # Default placement

                            c.drawString(x, y, custom_text)
                        c.showPage()

                c.save()

                # Add padding if size specified
                if desired_size_kb:
                    try:
                        size_kb = int(desired_size_kb)
                        if size_kb > 0:
                            add_padding_to_pdf(filename, size_kb)
                    except ValueError:
                        pass  # optionally notify user
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                return
            progress_bar["value"] = i + 1

        messagebox.showinfo("Success", f"{num_pdfs} PDFs generated successfully!")
        
        progress_bar["value"] = 0  # Reset progress bar
        overlay.lower()

    threading.Thread(target=generate_pdf_thread).start()

def browse_folder():
    folder_path = filedialog.askdirectory()
    entries[0].delete(0, tk.END)
    entries[0].insert(0, folder_path)

def browse_watermark():
    filetypes = [("Image files", "*.png;*.jpg;*.jpeg")]
    watermark_path = filedialog.askopenfilename(filetypes=filetypes)
    entries[4].delete(0, tk.END)
    entries[4].insert(0, watermark_path)

def toggle_custom_placement():
    if placement_var.get() == 2:
        x_entry.config(state=tk.NORMAL)
        y_entry.config(state=tk.NORMAL)
    else:
        x_entry.delete(0, tk.END)
        y_entry.delete(0, tk.END)
        x_entry.config(state=tk.DISABLED)
        y_entry.config(state=tk.DISABLED)


# Decode the base64 string to bytes
logo_bytes = base64.b64decode(logo_png)

# Create a BytesIO object to wrap the decoded bytes
logo_buffer = BytesIO(logo_bytes)

# Open the image using PIL
logo_image = Image.open(logo_buffer)

if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

root = tk.Tk()
root.title("PDF Generator")
root.configure(bg='black')
root.geometry("668x300")

# Set minimum and maximum size
root.minsize(668, 300)
root.maxsize(668, 300)

# # Resize the image if necessary
logo_image = logo_image.resize((32, 32), Image.LANCZOS)

# # Convert the image to a Tkinter PhotoImage object
logo_photo = ImageTk.PhotoImage(logo_image)

# # Set the logo image as the icon
root.iconphoto(True, logo_photo)


labels = [
    "Select folder to save PDFs :",
    "Enter number of pages per PDF (Max 100000) :",
    "Enter number of PDFs to generate (Max 100000) :",
    "Enter custom text to include in PDF :",
    "Select watermark file (PNG/JPG) :"
]

entries = []
for i, label_text in enumerate(labels):
    label = tk.Label(root, text=label_text, bg='black', fg='white', font=("Helvetica", 10, "bold"))
    label.place(x=10, y=30*i+10)
    entry = tk.Entry(root, width=30)
    entry.place(x=330, y=30*i+10)
    entries.append(entry)


# Create a custom style for the progressbar
style = ttk.Style()
style.theme_use('default')
style.configure("custom.Horizontal.TProgressbar", thickness=1, background='#7FFF00', troughcolor='#000000', bordercolor='#000000', darkcolor='#000000', lightcolor='#000000')

placement_var = tk.IntVar()
placement_var.set(1)  # Default placement

color_mode_var = tk.StringVar()
color_mode_var.set("bw")  # Default color mode is black and white

bw_radio = tk.Radiobutton(root, text="Black & White", variable=color_mode_var, value="bw", cursor="hand2", font=("Helvetica", 10, "bold"))
bw_radio.place(x=250, y=200)

color_radio = tk.Radiobutton(root, text="Color", variable=color_mode_var, value="color", cursor="hand2", font=("Helvetica", 10, "bold"))
color_radio.place(x=150, y=200)

default_radio = Radiobutton(root, text="Default", variable=placement_var, value=1, command=toggle_custom_placement, cursor="hand2",font=("Helvetica", 10, "bold"))
default_radio.place(x=130, y=160)

custom_radio = Radiobutton(root, text="Custom", variable=placement_var, value=2, command=toggle_custom_placement, cursor="hand2",font=("Helvetica", 10, "bold"))
custom_radio.place(x=240, y=160)

x_label = tk.Label(root, text="X :", bg='black', fg='white',font=("Helvetica", 10, "bold"))
x_label.place(x=330, y=160)

x_entry = tk.Entry(root, width=10, state=tk.DISABLED)
x_entry.place(x=360, y=160)

y_label = tk.Label(root, text="Y :", bg='black', fg='white',font=("Helvetica", 10, "bold"))
y_label.place(x=460, y=160)

y_entry = tk.Entry(root, width=10, state=tk.DISABLED)
y_entry.place(x=490, y=160)

or_label = tk.Label(root, text="OR", bg='black', fg='white', font=("Helvetica", 10, "bold"))
or_label.place(x=210, y=160)

or_label = tk.Label(root, text="OR", bg='black', fg='white', font=("Helvetica", 10, "bold"))
or_label.place(x=220, y=200)

and_label = tk.Label(root, text="&", bg='black', fg='white', font=("Helvetica", 10, "bold"))
and_label.place(x=430, y=160)

text_alignment_label = tk.Label(root, text="Text Alignment :", bg='black', fg='white', font=("Helvetica", 10, "bold"))
text_alignment_label.place(x=10, y=160)

Watermark_Type_label = tk.Label(root, text="Watermark Type :", bg='black', fg='white', font=("Helvetica", 10, "bold"))
Watermark_Type_label.place(x=10, y=200)

watermark_button = tk.Button(root, text="Browse Watermark", bg="#CD9B1D", command=browse_watermark, cursor="hand2",font=("Helvetica", 10, "bold"))
watermark_button.place(x=530, y=125)

# Add this in your GUI creation section, somewhere appropriate, e.g. below other entries
size_label = tk.Label(root, text="Enter desired PDF size in KB (e.g. 1024 for 1MB):", bg='black', fg='white', font=("Helvetica", 10, "bold"))
size_label.place(x=10, y=240)

size_entry = tk.Entry(root, width=30)
size_entry.place(x=330, y=240)

entries.append(size_entry)


button_browse = tk.Button(root, text="Select Folder", bg="#CD9B1D", command=browse_folder, cursor="hand2", font=("Helvetica", 10, "bold"))
button_browse.place(x=530, y=8) # Adjust the coordinates as needed

button_generate = tk.Button(root, text="Generate PDFs", bg="#00C957", command=generate_pdfs, cursor="hand2", font=("Helvetica", 10, "bold"))
button_generate.place(x=550, y=200) # Adjust the coordinates as needed


overlay = tk.Frame(root, bg='black')
overlay.place(x=0, y=0, relwidth=1, relheight=1)
overlay.lower()


progress_bar = ttk.Progressbar(root, length=660, mode='determinate', style="custom.Horizontal.TProgressbar")
progress_bar.place(x=5, y=270)

# Create a function to open the link
def open_link(event):
    webbrowser.open("https://github.com/Aniketc068")

version_label = tk.Label(root, text="Version 2.1", fg="white", bg="black", font=("Helvetica", 10, "bold"), cursor="hand2")
version_label.place(x=580, y=275)

# Bind the label to open the link when clicked
version_label.bind("<Button-1>", open_link)

root.mainloop()

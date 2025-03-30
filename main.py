import tkinter as tk
from tkinter import ttk,messagebox,filedialog

from PIL import  ImageTk

import qrcode
from qrcode.image.pil import PilImage


import io
from urllib.parse import urlparse


# -------------- QR Code Function ------------

class ImageQRCode:

    def __init__(self) -> None:

        self.__fill_colour = "black"
        self.__back_colour = "white"
        self.__version = 2
        self.__error_correction=qrcode.constants.ERROR_CORRECT_H
        self.__box_size=2
        self.__border=2
    
    def set_data(self,data:str) -> None :
        self.__qr = qrcode.QRCode(
            version=self.__version,
            error_correction=self.__error_correction,
            box_size=self.__box_size,
            border=self.__border,

        )

        self.__qr.add_data(data=data)
        self.__qr.make(fit=True)


    def generate(self):

        img = self.__qr.make_image(
            fill_color=self.__fill_colour,
            back_color=self.__back_colour
            )

        return img

# ---------------- Variable 
img_qrcode = ImageQRCode()
buffer_image: io.BytesIO | None = None
qr_img_tk = None
# ------------------ function --------------------- 
def generate_qr():

    global buffer_image
    global qr_img_tk

    tab_ui_data = {
        "Text" : data_text_ui,
        "WiFi" : data_wifi_ui,
        "URL" : data_url_ui

    }

    data = tab_ui_data[current_active_tab()]()

    if data:
        img_qrcode.set_data(data)
        image:PilImage 

        image = img_qrcode.generate()
        

        buffer_image = io.BytesIO()

        image.save(buffer_image, format="PNG")
        buffer_image.seek(0)

        file_size = len(buffer_image.getvalue())  # Size in bytes
        img_px = f"{image.pixel_size}"
        
        # Convert the PIL image to a format that Tkinter's Canvas can use
        qr_img_tk = ImageTk.PhotoImage(resize_image(image))
        

        # Update the label to display the QR code image
        qrcode_imagelabel.config(image=qr_img_tk, text="")  # Clear the "No QR Code" text

        update_img_info_ui(img_px,file_size)
    else:
        # Remove the existing image from the label
        qrcode_imagelabel.config(image="",text="No QR Code")  # Clear the image
        
        update_img_info_ui()

def current_active_tab() -> str:
    current_tab_index = entry_type_tabs.index(entry_type_tabs.select())
    tab_name  = entry_type_tabs.tab(current_tab_index, "text")

    return tab_name

def update_img_info_ui(image_px=None, image_file_size=None):

    if image_px:

        image_px = f"{image_px} px X {image_px} px"
    else:
        image_px = "-"

    if image_file_size:

        image_file_size = bytes_to_human_readable(image_file_size)
    else:
        image_file_size = "-"


    ## update image size (px)
    img_px_field.config(state="normal")
    img_px_field.delete(0,tk.END)
    img_px_field.insert(0,image_px)
    img_px_field.config(state="disabled")

    ## update image data size
    img_size_field.config(state="normal")
    img_size_field.delete(0,tk.END)
    img_size_field.insert(0,image_file_size)
    img_size_field.config(state="disabled")

def resize_image(image: PilImage):
    

    heigh = qrcode_imagelabel.winfo_height()
    width = qrcode_imagelabel.winfo_width()
    min_dimension = min(width,heigh) -1

    image = image.resize((min_dimension, min_dimension))
    
    return image
    
def save_qr():
    """Saves the QR code image to a file."""

    if not buffer_image:
        messagebox.showwarning("Save Error", "No QR code to save. Please generate one first !")
        return

    # Open a file dialog to select the save location
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        # Write buffer content to the file
        with open(file_path, "wb") as f:
            f.write(buffer_image.getvalue())
        messagebox.showinfo("Save Successful", f"QR code saved.\nLocation: {file_path}")
    
def bytes_to_human_readable(size_in_bytes):
    """Convert bytes to a human-readable format (e.g., KB, MB, GB)."""
    # Define size units
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    
    size = size_in_bytes
    unit_index = 0
    
    # Keep dividing by 1024 until the size is small enough
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    # Return the size rounded to 2 decimal places along with the appropriate unit
    return f"{size:.2f} {units[unit_index]}"

# ----------------- functions - UI --------------------
def data_text_ui() -> str:
    data = text_field.get("1.0","end-1c")
    return data

def data_wifi_ui() ->str | None :

    sslid:str = network_name_field.get()
    pawrd:str = password_field.get()
    network_hidden:bool = checkbox_isHidden.get()
    network_security = security_value.get()

    if network_security == "WPA/WPA2":
        v = "WPA"
    elif network_security == "None":
        v = ""
    else:
        v = network_security

    if v and (not sslid or not pawrd ):
        return None


    data = f"WIFI:S:{sslid};H:{str(network_hidden).lower()};T:{v};P:{pawrd};;"

    return data

def data_url_ui() -> str | None:

    url = url_field.get()

    p = urlparse(url)

    if url and not bool(p.scheme and p.netloc):
        messagebox.showerror("URL entry Error","The entered URL is not valied !")
        return None
    elif not url :
        return None

    return url



# -------------------- UI -------------------------

# ====== Window 
window = tk.Tk()
window.title("QR Code Generator")
window.config(padx=2,pady=2)
window.geometry("800x400")
window.wm_minsize(width=800,height=400)


## === Left Side
# Configure rows and columns to expand with the window size
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)

# Input Frame
input_frame = tk.Frame(window,padx=5,pady=5, relief="groove", borderwidth=1)
input_frame.grid(row=0,column=0,sticky="nsew")
input_frame.grid_columnconfigure(0,weight=1)
input_frame.grid_rowconfigure(0,weight=1)

# Input Frame > Entry Type Tabs
entry_type_tabs = ttk.Notebook(input_frame)
entry_type_tabs.grid(row=1,column=0,sticky="nsew")

# Input Frame > Tabs > Text Frame
text_tab = tk.Frame(entry_type_tabs,padx=5,pady=5)
text_tab.grid_columnconfigure(0,weight=1)
text_tab.grid_rowconfigure(0,weight=1)

# Input Frame > Tabs > WiFi Frame
wifi_tab = tk.Frame(entry_type_tabs,padx=20,pady=15)
wifi_tab.grid_columnconfigure(1,weight=1)
# wifi_tab.grid_rowconfigure(0,weight=1)

# Input Frame > Tabs > URL Frame
url_tab = tk.Frame(entry_type_tabs)
url_tab.grid_columnconfigure(1,weight=1)
# url_tab.grid_rowconfigure(0,weight=1)


# Input Frame >  Set Entry Type Tabs
entry_type_tabs.add(text_tab,text="Text")
entry_type_tabs.add(wifi_tab,text="WiFi")
entry_type_tabs.add(url_tab,text="URL")
entry_type_tabs.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

# Input Frame > Tabs > Text Frame > Text Field
text_field = tk.Text(text_tab,width=20)
text_field.grid(row=0, column=0, padx=2, pady=2,sticky="nsew")

# Input Frame > Tabs > Text Frame > WiFi Field
# Network Name
tk.Label(wifi_tab,text="Network Name (SSID):").grid(row=0, column=0, padx=2, pady=2, sticky="nsw")

network_name_field = tk.Entry(wifi_tab)
network_name_field.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

# Password
tk.Label(wifi_tab,text="Password:").grid(row=1, column=0, padx=2, pady=2, sticky="nsw")
password_field = tk.Entry(wifi_tab,show="*")
password_field.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")

# Hidden 
tk.Label(wifi_tab,text="Network :").grid(row=2, column=0, padx=2, pady=2, sticky="nsw")
checkbox_isHidden = tk.BooleanVar(wifi_tab,value=False)

hidden_checkbtn = tk.Checkbutton(
wifi_tab,
text="Hidden",
variable=checkbox_isHidden,
onvalue=True, offvalue=False
)
hidden_checkbtn.grid(row=2, column=1, padx=2, pady=2, sticky="nsw")

# Radio Button . choose Options

securtiy_frame = tk.LabelFrame(wifi_tab,text="Encryption")
securtiy_frame.grid(row=3, column=0,columnspan=2, padx=2, pady=2, sticky="nsew")

security_value = tk.StringVar(securtiy_frame,value="WPA/WPA2")

for i,option in enumerate(("WPA/WPA2","WEP","None")):
    tk.Radiobutton(
        securtiy_frame,
        text=option,
        variable=security_value,
        value=option
        ).grid(row=0, column=i,sticky="w", padx=2)

# Input Frame > Tabs > Text Frame > URL Field
tk.Label(url_tab,text="URL:").grid(row=0, column=0, padx=2, pady=2, sticky="nsw")
url_field = tk.Entry(url_tab)
url_field.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

# Input Frame > Generate Btn
generate_btn = tk.Button(input_frame, text="Generate QR Code",command=generate_qr)
generate_btn.grid(row=2, column=0, pady=5,padx=5,sticky="nsew")

## === Right Side
# Configure rows and columns to expand with the window size
window.grid_columnconfigure(1, weight=5)

# QRCode result Frame
qrcodeResult_frame = tk.Frame(window,padx=5,pady=5,relief="groove", borderwidth=1)
qrcodeResult_frame.grid(row=0,column=1,sticky="nsew")
qrcodeResult_frame.grid_columnconfigure(0,weight=1)
qrcodeResult_frame.grid_rowconfigure(1,weight=1)

# QRCode result Frame > Text Field
qrcode_label = tk.Label(qrcodeResult_frame, text="QR Code")
qrcode_label.grid(row=0, column=0,columnspan=3, padx=5, pady=5,sticky="new")

qrcode_imagelabel = tk.Label(
    qrcodeResult_frame,
    text="No QR Code Image",
    fg="black",bg="gray"
    )
qrcode_imagelabel.grid(row=1, column=0,columnspan=3,sticky="nsew")

# QRCode result Frame > Image info
img_info_frame = tk.Frame(qrcodeResult_frame)
img_info_frame.grid(row=2, column=0,columnspan=3,sticky="nsew")
img_info_frame.grid_columnconfigure(1,weight=2)
img_info_frame.grid_columnconfigure(2,weight=1)
img_info_frame.grid_rowconfigure([0,1],weight=1)

#-image resolution/pixel 
img_px_label = tk.Label(img_info_frame, text="Pixel:")
img_px_label.grid(row=0,column=0,sticky="nsw")
img_px_field = tk.Entry(img_info_frame,relief="flat")
img_px_field.insert(0,"-")
img_px_field.grid(row=0,column=1,sticky="nsw")
img_px_field.config(state="disabled")

#-image file size 

img_size_label = tk.Label(img_info_frame, text="Size:")
img_size_label.grid(row=1,column=0,sticky="nsw")
img_size_field = tk.Entry(img_info_frame,relief="flat")
img_size_field.insert(0,"-")
img_size_field.grid(row=1,column=1,sticky="nsw")
img_size_field.config(state="disabled")


# image Save to file

image_save_btn = tk.Button(img_info_frame,text="Save",command=save_qr)
image_save_btn.grid(row=0,column=2,rowspan=2,sticky="ew")

window.mainloop()
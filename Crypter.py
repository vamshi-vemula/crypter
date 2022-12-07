from pathlib import Path
from base64 import urlsafe_b64encode
from hashlib import md5
from cv2 import imread,imwrite
from cryptography.fernet import Fernet
from tkinter import Tk, Label, Canvas, Entry, Text, Button, PhotoImage, Frame, filedialog, messagebox, scrolledtext
from PIL import ImageTk, Image
from os import path
# Code for including assets path location
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
# Code to switch frames
def show_frame(frame):
    frame.tkraise()
# Code for choosing image
def choose_image(mode="image"):
    global file
    if mode == "image":
        file= filedialog.askopenfile(filetypes = ([('png', '*.png'),('jpeg', '*.jpeg'),('jpg', '*.jpg'),('All Files', '*.*')]))
        if not file:
            messagebox.showerror("Error","Please select an Image")
        else:
            update_image(file.name)
# Encrypting & Decrypting Text using Fernet
def encrypt_decrypt(string,password,mode='enc'):
    _hash = md5(password.encode()).hexdigest() 
    cipher_key = urlsafe_b64encode(_hash.encode()) 
    cipher = Fernet(cipher_key)
    if mode == 'enc':
        return cipher.encrypt(string.encode()).decode()
    else:
        return cipher.decrypt(string.encode()).decode()
# Encrypt message inside Image
def enc_img():
        data=se_entry_1.get("1.0","end")
        passw=se_entry_2.get()
        if file and data!="" and passw!="":
            encode(file.name,data,passw)
        else:
            messagebox.showerror("Error","Enter Text and Password")
def str2bin(string):
	return ''.join((bin(ord(i))[2:]).zfill(8) for i in string)
def encode(input_filepath,text,password):
    data = encrypt_decrypt(text,password,'enc')
    data_length = bin(len(data))[2:].zfill(32) 
    bin_data = iter(data_length + str2bin(data))
    img = imread(input_filepath,1)
    height,width = img.shape[0],img.shape[1]
    encoding_capacity = height*width*3
    total_bits = 32+len(data)*8
    completed = False
    modified_bits = 0
    #Run 2 nested for loops to traverse all the pixels of the whole image in left to right, top to bottom
    for i in range(height):
        for j in range(width):
            pixel = img[i,j] #get the current pixel that is being traversed
            for k in range(3): #get next 3 bits from the binary data that is to be encoded in image
                try:
                    x = next(bin_data)
                except StopIteration: #if there is no data to encode, mark the encoding process as completed
                    completed = True
                    break
                if x == '0' and pixel[k]%2==1: #if the bit to be encoded is '0' and the current LSB is '1'
                    pixel[k] -= 1 #change LSB from 1 to 0
                    modified_bits += 1 #increment the modified bits count
                elif x=='1' and pixel[k]%2==0: #if the bit to be encoded is '1' and the current LSB is '0'
                    pixel[k] += 1 #change LSB from 0 to 1
                    modified_bits += 1 #increment the modified bits count
            if completed:
                break
        if completed:
            break
    written = imwrite("secret_image.png",img) #create a new image with the modified pixels
    if written:
        messagebox.showinfo("Success","The output is saved in program location")
    else:
        messagebox.showerror("Error","Can't make a file")
    
    se_canvas.itemconfig(se_image_1,image=se_image_image_1)
    sd_canvas.itemconfig(sd_image_1,image=sd_image_image_1)

# Decrypt message inside Image
def dec_img():
        passw=sd_entry_2.get()
        if file and passw!="":
            decode(file.name,passw)
        else:
            messagebox.showerror("Error","Enter the Password")
def bin2str(string):
	return ''.join(chr(int(string[i:i+8],2)) for i in range(len(string))[::8])
def decode(input_filepath,password):
    result,extracted_bits,completed,number_of_bits = '',0,False,None
    img = imread(input_filepath)
    height,width = img.shape[0],img.shape[1] #get the dimensions of the image
    #Run 2 nested for loops to traverse all the pixels of the whole image in left to right, top to bottom
    for i in range(height):
        for j in range(width):
            for k in img[i,j]: #for values in pixel RGB tuple
                result += str(k%2) #extract the LSB of RGB values of each pixel
                extracted_bits += 1

                if extracted_bits == 32 and number_of_bits == None: #If the first 32 bits are extracted, it is our data size. Now extract the original data
                    number_of_bits = int(result,2)*8 #number of bits to extract from the image
                    result = ''
                    extracted_bits = 0
                elif extracted_bits == number_of_bits: #if all required bits are extracted, mark the process as completed
                    completed = True
                    break
            if completed:
                break
        if completed:
            break
    try:
        decrypted_data= encrypt_decrypt(bin2str(result),password,'dec')
        sd_canvas.itemconfig(sd_image_1,image=sd_image_image_1)
        se_canvas.itemconfig(se_image_1,image=se_image_image_1)
        sd_entry_1.delete(1.0,"end")
        sd_entry_1.insert(1.0, decrypted_data)
    except:
        messagebox.showerror("Error","Wrong Password") #if password did not match, throw error


        
# GUI Code
window = Tk()

window.geometry("900x600")
window.title("Crypter Tool")
window.configure(bg = "#2F2C2C")
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)
# 7 Frames for different screens
frame_sh = Frame(window)
frame_se = Frame(window)
frame_sd = Frame(window)
for frame in (frame_sh, frame_se, frame_sd):
    frame.grid(row=0,column=0,sticky='nsew')
# Update Image
def update_image(filename):
    myimg = Image.open(filename, 'r')
    myimage = myimg.resize((369,337))
    img = ImageTk.PhotoImage(myimage)
    se_canvas.itemconfig(se_image_1,image=img)
    se_canvas.imgref = img
    sd_canvas.itemconfig(sd_image_1,image=img)
    sd_canvas.imgref = img
# ------------            Steg Home Frame sh      -------------------
sh_canvas = Canvas(frame_sh,bg = "#2F2C2C",height = 600,width = 900,bd = 0,highlightthickness = 0,relief = "ridge")
sh_canvas.place(x = 0, y = 0)

sh_image_image_1 = PhotoImage(file=relative_to_assets("logo.png"))
sh_image_1 = sh_canvas.create_image(241.0,318.0,image=sh_image_image_1)

sh_canvas.create_text(330.0,37.0,anchor="nw",text="Crypter Tool",fill="#00BFA6",font=("Inter", 26 * -1))

sh_button_image_1 = PhotoImage(file=relative_to_assets("sh_button_1.png"))
sh_button_1 = Button(master=sh_canvas,image=sh_button_image_1,borderwidth=0,highlightthickness=0,command=lambda: show_frame(frame_se),relief="flat")
sh_button_1.place(x=512.0,y=205.0,width=305.0,height=82.0)


sh_button_image_2 = PhotoImage(file=relative_to_assets("sh_button_2.png"))
sh_button_2 = Button(master=sh_canvas,image=sh_button_image_2,borderwidth=0,highlightthickness=0,command=lambda: show_frame(frame_sd),relief="flat")
sh_button_2.place(x=512.0,y=358.0,width=305.0,height=76.0)

sh_canvas.create_text(150.0,520.0,anchor="nw",text="Python GUI Tool for Steganography with Password Encryption",fill="#FFFFFF",font=("Inter", 17 * -1))

# ------------            Steg Encrypt Frame se      -------------------
se_canvas = Canvas(frame_se,bg = "#2F2C2C",height = 600,width = 900,bd = 0,highlightthickness = 0,relief = "ridge")
se_canvas.place(x = 0, y = 0)

se_image_image_1 = PhotoImage(file=relative_to_assets("logo.png"))
se_image_1 = se_canvas.create_image(244.0,319.0,image=se_image_image_1)

se_canvas.create_text(215.0,46.0,anchor="nw",text="Select any Image to hide your secret message inside that Image",fill="#FFFFFF",font=("Inter", 16 * -1))

se_entry_image_1 = PhotoImage(file=relative_to_assets("entry_large.png"))
se_entry_bg_1 = se_canvas.create_image(667.0,308.0,image=se_entry_image_1)
se_entry_1 = scrolledtext.ScrolledText(master=se_canvas,bd=0,bg="#888585",highlightthickness=0)
se_entry_1.place(x=529.0,y=258.0,width=276.0,height=98.0)

se_entry_image_2 = PhotoImage(file=relative_to_assets("entry_small.png"))
se_entry_bg_2 = se_canvas.create_image(667.0,414.5,image=se_entry_image_2)
se_entry_2 = Entry(master=se_canvas,bd=0,bg="#888585",highlightthickness=0)
se_entry_2.place(x=529.0,y=398.0,width=276.0,height=31.0)

se_canvas.create_text(526.0,228.0,anchor="nw",text="Enter Secret Message",fill="#FFFFFF",font=("Inter", 13 * -1))

se_canvas.create_text(526.0,368.0,anchor="nw",text="Enter Password",fill="#FFFFFF",font=("Inter", 13 * -1))

se_back_button_image = PhotoImage(file=relative_to_assets("back.png"))
se_back_button = Button(master=se_canvas,image=se_back_button_image,borderwidth=0,highlightthickness=0,command=lambda: show_frame(frame_sh),relief="flat")
se_back_button.place(x=36.0,y=30.0,width=131.0,height=52.0)

se_button_image_1 = PhotoImage(file=relative_to_assets("se_button_1.png"))
se_button_1 = Button(master=se_canvas,image=se_button_image_1,borderwidth=0,highlightthickness=0,command=lambda: choose_image(),relief="flat")
se_button_1.place(x=510.0,y=137.0,width=305.0,height=67.0)

se_button_image_2 = PhotoImage(file=relative_to_assets("se_button_2.png"))
se_button_2 = Button(master=se_canvas,image=se_button_image_2,borderwidth=0,highlightthickness=0,command=lambda: enc_img(),relief="flat")
se_button_2.place(x=514.0,y=455.0,width=305.0,height=67.0)

# ------------            Steg Decrypt Frame sd      -------------------
sd_canvas = Canvas(frame_sd,bg = "#2F2C2C",height = 600,width = 900,bd = 0,highlightthickness = 0,relief = "ridge")
sd_canvas.place(x = 0, y = 0)

sd_image_image_1 = PhotoImage(file=relative_to_assets("logo.png"))
sd_image_1 = sd_canvas.create_image(254.0,313.0,image=sd_image_image_1)

sd_canvas.create_text(225.0,44.0,anchor="nw",text="Select any Image to see Hidden message inside that Image",fill="#FFFFFF",font=("Inter", 16 * -1))

sd_entry_image_1 = PhotoImage(file=relative_to_assets("entry_large.png"))
sd_entry_bg_1 = sd_canvas.create_image(663.0,460.0,image=sd_entry_image_1)
sd_entry_1 = scrolledtext.ScrolledText(master=sd_canvas,bd=0,bg="#888585",highlightthickness=0)
sd_entry_1.place(x=525.0,y=410.0,width=276.0,height=98.0)

sd_entry_image_2 = PhotoImage(file=relative_to_assets("entry_small.png"))
sd_entry_bg_2 = sd_canvas.create_image(662.0,265.5,image=sd_entry_image_2)
sd_entry_2 = Entry(master=sd_canvas,bd=0,bg="#888585",highlightthickness=0)
sd_entry_2.place(x=524.0,y=249.0,width=276.0,height=31.0)

sd_canvas.create_text(517.0,386.0,anchor="nw",text="Secret Message is :-",fill="#FFFFFF",font=("Inter", 13 * -1))

sd_canvas.create_text(517.0,217.0,anchor="nw",text="Enter Password",fill="#FFFFFF",font=("Inter", 13 * -1))


sd_back_button_image = PhotoImage(file=relative_to_assets("back.png"))
sd_back_button = Button(master=sd_canvas,image=sd_back_button_image,borderwidth=0,highlightthickness=0,command=lambda: show_frame(frame_sh),relief="flat")
sd_back_button.place(x=36.0,y=30.0,width=131.0,height=52.0)

sd_button_image_1 = PhotoImage(file=relative_to_assets("sd_button_1.png"))
sd_button_1 = Button(master=sd_canvas,image=sd_button_image_1,borderwidth=0,highlightthickness=0,command=lambda: choose_image(),relief="flat")
sd_button_1.place(x=509.0,y=145.0,width=306.0,height=59.0)

sd_button_image_2 = PhotoImage(file=relative_to_assets("sd_button_2.png"))
sd_button_2 = Button(master=sd_canvas,image=sd_button_image_2,borderwidth=0,highlightthickness=0,command=lambda: dec_img(),relief="flat")
sd_button_2.place(x=509.0,y=308.0,width=306.0,height=60.0)


# End of Frames
show_frame(frame_sh)
window.resizable(False, False)
window.mainloop()
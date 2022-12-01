from tkinter import *
from PIL import Image, ImageTk
from tkinter.filedialog import askdirectory
import os 
import cv2
import glob 
from facecode import *
from pathlib import Path
import shutil

def import_folder():
    global total_width
    global total_height
    global image_list

    total_width = 0
    total_height = 0

    global directory
    directory = askdirectory(mustexist = True)
    
    if(os.path.isdir(directory)):
        files = glob.glob(directory + "/*")
        files.sort(key = os.path.getmtime)
        image_list = []
        listbox.delete(0, END)
        for path in files:
            if(path.endswith(".jpg") or path.endswith(".png")):
                img = cv2.imread(path)
                width, height, _ = img.shape
                total_width += width
                total_height += height
                image_list.append(img)
                listbox.insert(END, path[len(directory) + 1:])

def preview():
    try:
        FPS = int(fps_entry.get())
    except:
        FPS = round(len(image_list) / int(time_entry.get()))

    mean_width = int(total_width / len(image_list))
    mean_height = int(total_height / len(image_list))

    new_image_list = [image_list[index] for index in stack]
    if(facecode_option == 1):
        for i in range(len(new_image_list)):
            new_image_list[i] = facecode(new_image_list[i])

    download_path = str(Path.home()) + "\Downloads"
    
    filename = "output.mp4"
    output = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc("M", "J", "4", "2"), fps = FPS, frameSize = (mean_height, mean_width))
    for image in new_image_list:
        output.write(image)
    
    output.release()
    # os.startfile("output.mp4")
    play(filename)
    if(os.path.isfile(download_path + f"\{filename}")):
        os.remove(download_path + f"\{filename}")
    
    shutil.move(os.getcwd() + f"\{filename}", download_path)

def play(filename):
    cv2.destroyAllWindows()
    cap = cv2.VideoCapture(filename)
    cv2.namedWindow("Preview")

    while(cv2.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.imshow("Preview", frame)

        key = cv2.waitKey(30)
        if key == 32:
            break

    cap.release()
    cv2.destroyAllWindows()

def show(event):
    global image
    
    if(len(listbox.curselection()) == 0):
        image_display.config(image = '', height = 0, width = 0)
    else:
        if(len(listbox.curselection()) > len(stack)):
            stack.append([i for i in list(listbox.curselection()) if i not in stack][0])
        elif(len(listbox.curselection()) < len(stack)):
            stack.remove([i for i in stack if i not in list(listbox.curselection())][0])

        image_pil = Image.fromarray(cv2.cvtColor(image_list[stack[-1]], cv2.COLOR_BGR2RGB))
        height, width = image_pil.size
        image = ImageTk.PhotoImage(image_pil)
        image_display.config(image = image, height = height, width = width)

def clear_fps_entry(event):
    if(not fps_entry.get().isdecimal()):
        fps_entry.delete(0, "end")

def clear_time_entry(event):
    if(not time_entry.get().isdecimal()):
        time_entry.delete(0, "end")

def select_all():
    global stack
    if(select_option.get() == 1):
        listbox.select_set(0, END)
        stack = [i for i in range(len(image_list))]
    elif(select_option.get() == 0):
        listbox.selection_clear(0, END)
        stack = []

# All of Tkinter GUI objects 
root = Tk()
root.state("zoomed")
root.title("Timelapse")
win_width = root.winfo_screenwidth()
win_height = root.winfo_screenheight()

# Spotify dark mode color scheme
background = "#121212"
menu_bar = "#404040"
text_color = "#FFFFFF"

ico = Image.open("timelapse.png")
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.configure(bg = background)

top_frame = Frame(root, bg = background)
top_frame.pack(pady = 5)

import_button = Button(top_frame, text = "Import", command = import_folder, bg = menu_bar, fg = text_color)
import_button.pack(side = "left")

select_option = IntVar()
select_checkbox = Checkbutton(top_frame, variable = select_option, command = select_all, onvalue = 1, offvalue = 0, text = "All images?", bg = menu_bar, fg = text_color, selectcolor = menu_bar, activebackground = menu_bar, activeforeground = text_color)
select_checkbox.pack(side = "left", padx = 5)

facecode_option = IntVar()
facecode_checkbox = Checkbutton(top_frame, variable = facecode_option, onvalue = 1, offvalue = 0, text = "Use Facecode?", bg = menu_bar, fg = text_color, selectcolor = menu_bar, activebackground = menu_bar, activeforeground = text_color)
facecode_checkbox.pack(side = "left", padx = 5)

fps_entry = Entry(top_frame, width = 5)
fps_entry.insert(0, "FPS")
fps_entry.pack(side = "left", padx = 5)
fps_entry.bind("<FocusIn>", clear_fps_entry)

time_entry = Entry(top_frame, width = 10)
time_entry.insert(0, "In Seconds")
time_entry.pack(side = "left", padx = 5)
time_entry.bind("<FocusIn>", clear_time_entry)

preview_button = Button(top_frame, text = "Preview", command = preview, bg = menu_bar, fg = text_color)
preview_button.pack(side = "left", padx = 5)

bottom_frame = Frame(root, bg = background, height = 0.5 * win_height)
bottom_frame.pack(padx = 5)

image_display = Label(bottom_frame, bg = background, height = 0, width = 0)
image_display.pack(side = "left", padx = 10)

stack = []
listbox = Listbox(bottom_frame, bg = menu_bar, fg = text_color, selectmode = "multiple", height = 20, width = 20)
listbox.pack(side = "left", fill = "both")
listbox.bind("<<ListboxSelect>>", show)

scrollbar = Scrollbar(bottom_frame)
scrollbar.pack(side = "left", fill = "both")
listbox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = listbox.yview)

text = """
    Please input a folder of images.\n
    Select the images with the listbox to the left,\n
    or select all of the images with the checkbox.\n
    To use the "Facecode" program,\n 
    click on the desired checkbox.\n
    Please enter an integer in the "FPS" box,\n
    or input the amount of seconds the video should be.\n
    You cannot have a value in both boxes.\n
    nce done, click on the "Preview" button\n
    to open the video in a new window. The video is\n
    save in your downloads.
"""
text_label = Label(bottom_frame, text = text, height = 25, width = 45, bg = menu_bar, fg = text_color)
text_label.pack(side = "left", padx = 10)

root.mainloop()
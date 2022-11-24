from tkinter import *
from PIL import Image, ImageTk
from tkinter.filedialog import askdirectory
import os 
import cv2
from tkVideoPlayer import TkinterVideo
import datetime
from math import floor
import glob 

def import_folder():
    global total_width
    global total_height
    global image_list

    total_width = 0
    total_height = 0

    directory = askdirectory(mustexist = True)
    if(os.path.isdir(directory)):
        files = glob.glob(directory + "/*")
        files.sort(key = os.path.getmtime)
        image_list = []
        for path in files:
            if(path.endswith(".jpg") or path.endswith(".png")):
                img = cv2.imread(path)
                width, height, _ = img.shape
                total_width += width
                total_height += height
                image_list.append(img)
                listbox.insert(END, path[len(directory) + 1:])

def preview():
    global FPS

    mean_width = int(total_width / len(image_list))
    mean_height = int(total_height / len(image_list))
    video_label.place_forget()

    new_image_list = [image_list[index] for index in list(listbox.curselection())]

    output = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"DIVX"), fps = FPS, frameSize = (mean_height, mean_width))
    for image in new_image_list:
        output.write(image)
    output.release()
    
    global video_player
    video_player = TkinterVideo(video_frame, scaled = True)
    video_player.load("output.avi")
    video_player.pack(expand = True, fill = "both")

    slider.config(to = 0, from_ = 0)
    timestamp.set(0)

    video_player.bind("<<Duration>>", duration)
    video_player.bind("<<SecondChanged>>", get_timestamp)

def show(event):
    global image
    
    if(len(listbox.curselection()) == 0):
        image_display.config(image = '', height = 0, width = 0)
    else:
        if(len(listbox.curselection()) > len(stack)):
            stack.append(list(set(listbox.curselection()) - set(stack))[0])
        elif(len(listbox.curselection()) < len(stack)):
            stack.remove(list(set(stack) - set(listbox.curselection()))[0])

        image_pil = Image.fromarray(cv2.cvtColor(image_list[stack[-1]], cv2.COLOR_BGR2RGB))
        height, width = image_pil.size
        image = ImageTk.PhotoImage(image_pil)
        image_display.config(image = image, height = height, width = width)
    
def play():
    if video_player.is_paused():
        video_player.play()
    else:
        video_player.pause()

def seek(value):
    video_player.seek(int(value))

def duration(event):
    duration = video_player.video_info()["duration"]
    end_time["text"] = str(datetime.timedelta(seconds = duration))
    slider["to"] = duration

def get_timestamp(event):
    timestamp.set(video_player.current_duration())

def clear1(event):
    if(not entry1.get().isdecimal()):
        entry1.delete(0, "end")

def clear2(event):
    if(not entry2.get().isdecimal()):
        entry2.delete(0, "end")

def get_FPS_1(event):
    global FPS
    try:
        FPS = int(entry1.get())
    except:
        pass

def get_FPS_2(event):
    global FPS
    try:
        FPS = floor(len(image_list) / int(entry2.get()))
    except:
        pass

def select_all():
    global stack

    listbox.select_set(0, END)
    stack = [i for i in range(len(image_list))]

root = Tk()
root.state("zoomed")
root.title("Timelapse")
win_width = root.winfo_screenwidth()
win_height = root.winfo_screenheight()

# Spotify dark mode color scheme
background = "#121212"
menu_bar = "#404040"
text = "#FFFFFF"

ico = Image.open("timelapse.png")
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.configure(bg = background)

top_frame = Frame(root, bg = background)
top_frame.pack(pady = 5)

import_button = Button(top_frame, text = "Import", command = import_folder, bg = menu_bar, fg = text)
import_button.pack(side = "left")

checkbox = Checkbutton(top_frame, command = select_all, text = "All images?", bg = menu_bar, fg = text, selectcolor = menu_bar, activebackground = menu_bar, activeforeground = text)
checkbox.pack(side = "left", padx = 5)



entry1 = Entry(top_frame, width = 5)
entry1.insert(0, "FPS")
entry1.pack(side = "left", padx = 5)
entry1.bind("<FocusIn>", clear1)
entry1.bind("<Leave>", get_FPS_1)

entry2 = Entry(top_frame, width = 10)
entry2.insert(0, "In Seconds")
entry2.pack(side = "left", padx = 5)
entry2.bind("<FocusIn>", clear2)
entry2.bind("<Leave>", get_FPS_2)

preview_button = Button(top_frame, text = "Preview", command = preview, bg = menu_bar, fg = text)
preview_button.pack(side = "left", padx = 5)

frame = Frame(root, bg = background)
frame.pack(padx = 5)

image_display = Label(frame, bg = background, height = 0, width = 0)
image_display.pack(side = "left", padx = 10)

stack = []
listbox = Listbox(frame, bg = menu_bar, fg = text, selectmode = "multiple")
listbox.pack(side = "left", fill = "both")
listbox.bind("<<ListboxSelect>>", show)

scrollbar = Scrollbar(frame)
scrollbar.pack(side = "left", fill = "both")
listbox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = listbox.yview)

video_frame = Frame(frame, height = 0.5 * win_height, width = 0.5 * win_width, bg = "#FFFFFF")
video_frame.pack_propagate(False)
video_frame.pack(side = "left", padx = 10)

video_label = Label(video_frame, text = "Preview video will be displayed here", bg = menu_bar, fg = text)
video_label.place(relwidth = 1, relheight = 1)

ico2 = Image.open("play.png")
icon_reize = ico2.resize((50, 50))
icon = ImageTk.PhotoImage(icon_reize)
play_button = Button(root, text = "Play", command = play, bg = menu_bar, fg = text, image = icon, height = 50, width = 50)
play_button.pack(pady = 5)

slider_frame = Frame(root, bg = background, width = 100)
slider_frame.pack()

start_time = Label(slider_frame, text=str(datetime.timedelta(seconds = 0)), bg = background, fg = text)
start_time.pack(side="left")

timestamp = IntVar()
slider = Scale(slider_frame, variable = timestamp, from_ = 0, to = 0, orient = "horizontal", bg = menu_bar, troughcolor = menu_bar, highlightthickness = 0, length = 0.25 * win_width, command = seek, fg = text)
slider.pack(side = "left")

end_time = Label(slider_frame, text = str(datetime.timedelta(seconds = 0)), bg = background, fg = text)
end_time.pack(side = "left")

root.mainloop()
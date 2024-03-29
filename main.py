from tkinter import *
from PIL import Image, ImageTk
from tkinter.filedialog import askdirectory
from tkVideoPlayer import TkinterVideo
import datetime
import os 
import cv2
import glob 
from facecode import *
from pathlib import Path
import shutil

def import_folder():
    global image_list
    global directory

    directory = askdirectory(mustexist = True)
    
    if(os.path.isdir(directory)):
        files = glob.glob(directory + "/*")
        image_list = []
        listbox.delete(0, END)
        for path in files:
            if(path.endswith(".jpg") or path.endswith(".png")):
                image_list.append(path)
                listbox.insert(END, path[len(directory) + 1:])
    if(len(image_list) == 0):
        error_label.config(text = "Error: No found images in the folder.")
    else:
        error_label.config(text = "")

def preview():
    if((len(fps_entry.get()) == 0 and len(time_entry.get()) == 0)):
        error_label.config(text = "Error: Must have a value for either \"FPS\" or \"Length of Video in Seconds\".")
    elif((len(fps_entry.get()) > 0 and len(time_entry.get()) > 0)):
        error_label.config(text = "Error: Cannot have a value for both \"FPS\" and \"Length of Video in Seconds\".")
    elif((len(fps_entry.get()) > 0 and int(fps_entry.get()) == 0) or (len(time_entry.get()) > 0 and int(time_entry.get()) == 0)):
        error_label.config(text = "Error: Cannot have a value for 0.")
    elif(len(stack) == 0):
        error_label.config(text = "Error: Must import a folder of images and/or select more than one image.")
    else:
        error_label.config(text = "")

        new_image_list = [image_list[index] for index in stack]
        if(facecode_option == 1):
            for i in range(len(new_image_list)):
                new_image_list[i] = facecode(new_image_list[i])

        total_width = 0
        total_height = 0

        if(len(fps_entry.get()) > 0):
            FPS = int(fps_entry.get())
        elif(len(time_entry.get()) > 0):
            FPS = round(len(new_image_list) / int(time_entry.get()))

        for path in new_image_list:
            img = cv2.imread(path)
            width, height, _ = img.shape
            total_width += width
            total_height += height

        mean_width = int(total_width / len(new_image_list))
        mean_height = int(total_height / len(new_image_list))

        video_label.place_forget()
        try:
            output = cv2.VideoWriter(filename, 
                                    cv2.VideoWriter_fourcc("m" , "p", "4", "v"), 
                                    fps = FPS, 
                                    frameSize = (mean_height ,mean_width))
            for image in new_image_list:
                output.write(cv2.imread(image))
        
            output.release()
            try:
                if duration > 0: # Checks if a video was already created
                    video_player.seek(int(len(new_image_list) / FPS)) # If the video isn't over, replacing it will cause an error
                    video_player.stop() # Supppose to stop and close the video file, but it doesn't without the previous line

                shutil.copy(os.getcwd() + f"\{filename}", str(Path.home()) + "\Downloads")    
            
                video_player.load(filename)
                video_player.seek(0)
                timestamp.set(0)

                video_player.bind("<<Duration>>", duration_event)
                video_player.bind("<<SecondChanged>>", get_timestamp)
                # os.startfile(download_path + f"\{filename}")
            except:
                error_label.config(text = "Error: The Downloads folder couldn't be accessed.")
        except:
            error_label.config(text = "Error: There was an issue at creating the video. Try increasing the number of images selected or the FPS.")

def select(event):
    global image # DON"T DELETE, it won't show the image

    if(len(listbox.curselection()) == 0):
        image_display.config(image = '', height = 0, width = 0)
    else:
        if(len(listbox.curselection()) > len(stack)):
            stack.append([i for i in list(listbox.curselection()) if i not in stack][0])
        elif(len(listbox.curselection()) < len(stack)):
            stack.remove([i for i in stack if i not in list(listbox.curselection())][0])
            
        image_pil = Image.fromarray(cv2.cvtColor(cv2.imread(image_list[stack[-1]]), cv2.COLOR_BGR2RGB))

        height, width = image_pil.size
        image = ImageTk.PhotoImage(image_pil)
        image_display.config(image = image, height = height, width = width)

def play():
    if(os.path.exists(filename)):
        error_label.config(text = "")
        if video_player.is_paused():
            video_player.play()
        else:
            video_player.pause()
    else:
        error_label.config(text = "Error: A video must be created before being able to play.")

def seek(value):
    video_player.seek(int(value))

def duration_event(event):
    global duration
    duration = int(video_player.video_info()["duration"])
    end_time["text"] = str(datetime.timedelta(seconds = duration))
    slider["to"] = duration

def get_timestamp(event):
    timestamp.set(video_player.current_duration())

def select_all():
    global stack
    if(select_option.get() == 1):
        listbox.select_set(0, END)
        stack = [i for i in range(len(image_list))]
    elif(select_option.get() == 0):
        listbox.selection_clear(0, END)
        stack = []

def validate(input):
    if(input.isdigit()):
        error_label.config(text = "")
        return True
    else:
        error_label.config(text = "Error: Input must be an integer.")
        return False
    
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

error_label = Label(root, text = "", fg = "red", bg = background)

fps_label = Label(top_frame, text = "FPS:", bg = menu_bar, fg = text_color)
fps_label.pack(side = "left")

vcmd = root.register(validate)
fps_entry = Entry(top_frame, width = 4, validate = "key", validatecommand = (vcmd, '%S'))
fps_entry.pack(side = "left", padx = 5)

time_label = Label(top_frame, text = "Length of Video in Seconds:", bg = menu_bar, fg = text_color)
time_label.pack(side = "left")

time_entry = Entry(top_frame, width = 4, validate = "key", validatecommand = (vcmd, '%S'))
time_entry.pack(side = "left", padx = 5)

duration = 0
preview_button = Button(top_frame, text = "Preview", command = preview, bg = menu_bar, fg = text_color)
preview_button.pack(side = "left", padx = 5)

error_label.pack()

bottom_frame = Frame(root, bg = background, height = 0.5 * win_height)
bottom_frame.pack(padx = 5)

image_display = Label(bottom_frame, bg = background, height = 0, width = 0)
image_display.pack(side = "left", padx = 10)

stack = []
listbox = Listbox(bottom_frame, bg = menu_bar, fg = text_color, selectmode = "multiple", height = 20, width = 20)
listbox.pack(side = "left", fill = "both")
listbox.bind("<<ListboxSelect>>", select)

scrollbar = Scrollbar(bottom_frame)
scrollbar.pack(side = "left", fill = "both")
listbox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = listbox.yview)

video_frame = Frame(bottom_frame, height = 0.5 * win_height, width = 0.5 * win_width, bg = "#FFFFFF")
video_frame.pack_propagate(False)
video_frame.pack(side = "left", padx = 10)

filename = "output.mp4"
video_player = TkinterVideo(video_frame, scaled = False)
video_player.keep_aspect(True)
video_player.pack(expand = True, fill = "both")

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
video_label = Label(video_frame, text = text, bg = menu_bar, fg = text_color)
video_label.place(relwidth = 1, relheight = 1)

ico2 = Image.open("play.png")
icon_reize = ico2.resize((50, 50))
icon = ImageTk.PhotoImage(icon_reize)
play_button = Button(root, text = "Play", command = play, bg = menu_bar, fg = text_color, image = icon, height = 50, width = 50)
play_button.pack(pady = 5)

slider_frame = Frame(root, bg = background, width = 100)
slider_frame.pack()

start_time = Label(slider_frame, text = str(datetime.timedelta(seconds = 0)), bg = background, fg = text_color)
start_time.pack(side = "left")

timestamp = IntVar()
slider = Scale(slider_frame, variable = timestamp, from_ = 0, to = 0, orient = "horizontal", bg = menu_bar, troughcolor = menu_bar, highlightthickness = 0, length = 0.5 * win_width, command = seek, fg = text_color)
slider.pack(side = "left")

end_time = Label(slider_frame, text = str(datetime.timedelta(seconds = 0)), bg = background, fg = text_color)
end_time.pack(side = "left")

root.mainloop()
from tkinter import *
import tkinter.messagebox as tmsg
from PIL import Image,ImageTk

# Starting point of mouse dragging or shapes
prev_x = 0 
prev_y = 0 
# Current x,y position of mouse cursor or end position of dragging
x = 0 
y = 0
created_element_info = [] #list of all shapes objects for saving drawing
new = [] # Each shapes of canvas
created = [] # Temporary list to hold info on every drag
shape = "Line" # Shape to draw
color = "Black" # Color of the shape
line_width = 1 # Width of the line shape
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# All the functions and logics go here
#Capture Motions on every mouse position change
def captureMotion(e=""):
    #Update Status Bar
    status.set(f"Position : x - {e.x} , y - {e.y}")
    statusbar.update()

# Update the previous position on mouse left click
def recordPosition(e=""):
    global prev_x
    global prev_y
    prev_x = e.x
    prev_y = e.y

# Update the current shape
def shapechanger(e=""):
    global shape
    shape = radiovalue.get() #selected radio value

# After Every drawing create info of drawing and add the element to new list and assign empty list to created
def generateShapesObj(e=""):
    global created, created_element_info
    new.append(created[-1])
    created = []
    created_element_info_obj = {
        "type": shape,
        "color": color,
        "prev_x": prev_x,
        "prev_y": prev_y,
        "x": x,
        "y": y
    }
    created_element_info.append(created_element_info_obj)

# Create Elements on canvas based on shape variable
def createElms():
    if shape == "Rectangle":
        a = canvas.create_rectangle(prev_x, prev_y, x, y)
    elif shape == "Oval":
        a = canvas.create_oval(prev_x, prev_y, x, y)
    elif shape == "Line":
        a = canvas.create_line(prev_x, prev_y, x, y,
                               width=line_width,
                               smooth=TRUE, splinesteps=3)
    elif shape == "Text":
        a = canvas.create_text(x, y, text=TextValueEntry.get(), font=('comicsans',FontSizeEntry.get(), 'bold'))
    elif shape == "Bitmap":
        global img
        OG_img = Image.open(BitmapValueEntry.get())
        OG_img= OG_img.resize(( max(abs(x-prev_x),10), max(abs(y-prev_y),10) ))
        img = ImageTk.PhotoImage(OG_img)
        a = canvas.create_image(x, y, anchor=NW, image=img, state=NORMAL)
    elif shape == "Paint":
        a = canvas.create_oval(x-2, y-2, x+2, y+2, fill="Black")
    elif shape == "Erase":
        a = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="White", outline="White" )
    elif shape == "Arrow":
        a = canvas.create_line(prev_x, prev_y, x, y,
                               width=line_width,
                               smooth=TRUE, splinesteps=3,arrow = LAST)
    return a

# Create shapes on mouse dragging and resize and show the shapes on the canvas
def drawShapesOnDragging(e=""):
    global x, y, element
    try:
        # Update current Position
        x = e.x
        y = e.y

        #Generate Element
        element = createElms()
        if shape != "Paint" and shape != "Erase" :
            deleteUnwanted(element) # Delete unwanted shapes
    except Exception as e:
        tmsg.showerror("Some Error Occurred!", e)

def deleteUnwanted(element):
    global created
    created.append(element) #Elements that created
    for item in created[:-1]: 
        canvas.delete(item)

# Clear the Canvas
def clearCanvas(e=""):
    global created_element_info, canvas, created, new
    canvas.delete("all")
    created_element_info = []
    created = []
    new = []


root = Tk()
root.title("Bad Handwriting Who?")

root.minsize(CANVAS_WIDTH, CANVAS_HEIGHT) #Minimum Size of the window
# All Widgets here such as canvas, buttons etc

# Canvas

canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

# Binding Events to canvas
# Structure: canvas.bind("<eventcodename>", function-name)
canvas.bind("<1>", recordPosition) #On Mouse left click
canvas.bind("<B1-Motion>", drawShapesOnDragging) #Capture Mouse left click + move (dragging)
canvas.bind("<ButtonRelease-1>", generateShapesObj) #When Mouse left click release
canvas.bind("<Motion>", captureMotion) #Mouse Motion
frame = Frame(root)
frame.pack(side=TOP)
radiovalue = StringVar()
geometry_shapes = ["Line", "Rectangle", "Oval", "Text", "Bitmap", "Paint", "Erase", "Arrow"]
radiovalue.set("Line")  # Default Select

# Manipulates Radios from the list
for shape in geometry_shapes:
    radio = Radiobutton(frame, text=shape, variable=radiovalue, font="comicsans     12 bold", value=shape, command=shapechanger).pack(side=LEFT, padx=6,pady=3)

#Buttons
Button(root, text="Clear Canvas", font="comicsans 12 bold",
       command=clearCanvas).pack(side=TOP, padx=6)

#Text Input
TextParametersFrame = Frame(master=root)
TextLableLable = Label(master=TextParametersFrame, text=' Your Text: ',
                                 font=("Courier", 12, 'bold')).pack(side='left', ipadx=0, padx=0, pady=0)

TextValueEntry = Entry(TextParametersFrame, width= 60)
TextValueEntry.pack(side=LEFT)

FontSizeLabel = Label(master=TextParametersFrame, text=' Text Size: ',
                                 font=("Courier", 12, 'bold')).pack(side='left', ipadx=0, padx=0, pady=0)
FontSizeEntry = Entry(TextParametersFrame, width= 5)
FontSizeEntry.pack(side=LEFT)

TextValueEntry.insert(0,"Type Text Here")
FontSizeEntry.insert(0,12)

TextParametersFrame.pack(fill=BOTH, side=TOP, expand=True)

#Gcode Input
BitmapInputFrame = Frame(master=root, width=100)
BitmapLable = Label(master=BitmapInputFrame, text=' Bitmap Address: ',
                                 font=("Courier", 12, 'bold')).pack(side='left', ipadx=0, padx=0, pady=0)
BitmapValueEntry = Entry(BitmapInputFrame, width= 60)
BitmapValueEntry.pack(side=LEFT)

BitmapValueEntry.insert(0,'Example Image.bmp')

BitmapInputFrame.pack(fill=BOTH, side=TOP, expand=True)

#Robot controls Buttons
RobotControlFrame = Frame(master=root, width=100)

ZeroButton = Button(RobotControlFrame,
                                   text="Zero Robot Position",
                                   command=clearCanvas,
                                   height=4,
                                   fg="black",
                                   width=20,
                                   bd=5,
                                   activebackground='green'
                                   ).pack(side=LEFT)

PrintToBoardButton = Button(RobotControlFrame,
                                   text="Print Canvas To Board",
                                   command=clearCanvas,
                                   height=4,
                                   fg="black",
                                   width=20,
                                   bd=5,
                                   activebackground='green'
                                   ).pack(side=LEFT)

RobotPositionFrame = Frame(master=RobotControlFrame, width=100)
XPosFrame = Frame(master=RobotPositionFrame, width=100)
XPosLable = Label(master=XPosFrame, text=' X-Position: ',
                                 font=("Courier", 12, 'bold')).pack(side=LEFT, ipadx=0, padx=0, pady=0)
XPosEntry = Entry(XPosFrame)
XPosEntry.pack(side=LEFT)
XPosFrame.pack(side=TOP)

YPosFrame = Frame(master=RobotPositionFrame, width=100)
YPosLabel = Label(master=YPosFrame, text=' Y-Position: ',
                                 font=("Courier", 12, 'bold')).pack(side=LEFT, ipadx=0, padx=0, pady=0)
YPosEntry = Entry(YPosFrame)
YPosEntry.pack(side=LEFT)
YPosFrame.pack(side=TOP)

MoveRobotButton = Button(RobotControlFrame,
                                   text="Go To Coords",
                                   command=clearCanvas,
                                   height=4,
                                   fg="black",
                                   width=20,
                                   bd=5,
                                   activebackground='green'
                                   ).pack(side=LEFT)

RobotPositionFrame.pack(side=LEFT)
RobotControlFrame.pack(fill=BOTH, side=TOP, expand=True)
# Status Bar
status = StringVar()
status.set("Position : x - 0 , y - 0")
statusbar = Label(root, textvariable=status, anchor="w", relief=SUNKEN)
statusbar.pack(side=BOTTOM, fill=X)
root.mainloop()
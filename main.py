from tkinter import *
import tkinter.messagebox as tmsg
from PIL import Image,ImageTk, ImageGrab, ImageOps
from Bmp_to_Gcode import *
import serial
import time

# Starting point of mouse dragging or shapes
prev_x = 0 
prev_y = 0 
# Current x,y position of mouse cursor or end position of dragging
x = 0 
y = 0
created_element_info = [] #list of all shapes objects for saving drawing
new = [] # Each shapes of canvas
created = [] # Temporary list to hold info on every drag
image_elements = [] #list contains all image objects used
shape = "Line" # Shape to draw
color = "Black" # Color of the shape
line_width = 1 # Width of the line shape
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# set up serial comms---------------------------------------------------------------------------------------------------
#ser = serial.Serial('com4', 9600, timeout=10) # create Serial Object, baud = 9600, read times out after 10s
time.sleep(3)  # delay 3 seconds to allow serial com to get established


prev_X_and_Y = [0,0]
# This command sends serial message to stm32 to move to point (x, y)
def set_coordinates_state(x_coord, y_coord):
    global prev_X_and_Y  # Previous X and Y coordinates

    #velocity must be same here as in stm32 code
    speed = 50

    try:
        NumEntries = len(x_coord)
        # handle list / array case
    except TypeError:  # oops, was a float
        NumEntries = 1

    ser.reset_input_buffer()  # clear input buffer

    for i in range(NumEntries):
        if NumEntries > 1:
            thisXCoord = x_coord[i]
            thisYCoord = y_coord[i]
        else:
            thisXCoord = x_coord
            thisYCoord = y_coord

        # In order to allow the arm to move in approximately straight lines between 2 points, we will discretize the
        # path taken between two point such that no 2 points along the path are greater than 1 cm

        # Length of straight line from current coords to target coords
        PathLength = np.sqrt((thisXCoord - prev_X_and_Y[0]) ** 2 + (thisYCoord - prev_X_and_Y[1]) ** 2)

        numberOfPathSteps = math.ceil(PathLength / 1)

        # Find X and Y coordinates along the path --discretize straight line path
        if thisXCoord != prev_X_and_Y[0]:
            Xsteps = np.linspace(prev_X_and_Y[0], thisXCoord, numberOfPathSteps)
            if prev_X_and_Y[0] < thisXCoord:
                Ysteps = np.interp(Xsteps, [prev_X_and_Y[0], thisXCoord], [prev_X_and_Y[1], thisYCoord])
            else:
                Ysteps = np.interp(Xsteps, [thisXCoord, prev_X_and_Y[0]], [thisYCoord, prev_X_and_Y[1]])
        else:
            Ysteps = np.linspace(prev_X_and_Y[1], thisYCoord, numberOfPathSteps)
            if prev_X_and_Y[1] < thisYCoord:
                Xsteps = np.interp(Ysteps, [prev_X_and_Y[1], thisYCoord], [prev_X_and_Y[0], thisXCoord])
            else:
                Xsteps = np.interp(Ysteps, [thisYCoord, prev_X_and_Y[1]], [thisXCoord, prev_X_and_Y[0]])


        #Xsteps and Ysteps are np arrays of steps that will be taken

        #Send moves to stm32
    for i in range(len(Xsteps)):

        start = time.time()

        # send serial data to stm32 in format --> <xcoord>A<ycoord>B
        ser.write(bytes(str(Xsteps[i]), 'UTF-8'))
        ser.write(bytes('A', 'UTF-8'))
        ser.write(bytes(str(Ysteps[i]), 'UTF-8'))
        ser.write(bytes('B', 'UTF-8'))

        #same calculation performed on stm32
        ExpectedTime = np.sqrt((Xsteps[i] - prev_X_and_Y[0]) ** 2 + (Ysteps[i] - prev_X_and_Y[1]) ** 2) / speed
        print("ExpectedTime: " + ExpectedTime)

        try:
            # convert expected time to float (minimum time is 0.005s)
            ExpectedTime = max(ExpectedTime, 0.1)
        except ValueError:
            ExpectedTime = 0.1

        ser.reset_input_buffer()  # clear input buffer

        # if we get a 'y' from stm32, we move on, otherwise we will wait 0.5 sec. We will repeat this 5 times.
        # After which, if we still do not have confirmation, we will print to the monitor that there was a problem
        # and move on

        DidMoveWork = False

        MoveSuccessMessage = ''

        MoveStartTime = time.time()

        while time.time()-MoveStartTime < ExpectedTime*4 and not DidMoveWork:
            if ser.inWaiting():
                MoveSuccessMessage = ser.read(1)  # read one bit from buffer

            if MoveSuccessMessage == b'y':
                DidMoveWork = True
                print("Move was successful")

        if not DidMoveWork:
            print("Move was not successful")

        ser.reset_input_buffer()  # clear input buffer
        end = time.time()

        #print("Difference between expected time and actual time: " + str(end - start - ExpectedTime))

        prev_X_and_Y = [Xsteps[i], Ysteps[i]]  # update prev_X_and_Y

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
        global image_elements
        OG_img = Image.open(BitmapValueEntry.get()) # get image in PIL form
        OG_img= OG_img.resize(( int(max(abs(x-prev_x),10)*2), int(max(abs(y-prev_y),10)*2) )) #resize image
        image_elements.append(ImageTk.PhotoImage(OG_img)) # cast into tk image format
        a = canvas.create_image(prev_x,prev_y, anchor=CENTER, image=image_elements[-1], state=NORMAL)
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
    global created_element_info, canvas, created, new, image_elements
    canvas.delete("all")
    created_element_info = []
    created = []
    image_elements = []
    new = []

def printToBoard():
    #takes a screen cap of the canvas
    img = ImageGrab.grab(bbox=(
        canvas.winfo_rootx(),
        canvas.winfo_rooty(),
        canvas.winfo_rootx() + canvas.winfo_width(),
        canvas.winfo_rooty() + canvas.winfo_height()))
    img = ImageOps.grayscale(img) #turns pic to bit map
    Img_to_Gcode(img) # convert to GCode

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
                                   command=printToBoard,
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
XPosEntry.insert(0,100)
XPosFrame.pack(side=TOP)

YPosFrame = Frame(master=RobotPositionFrame, width=100)
YPosLabel = Label(master=YPosFrame, text=' Y-Position: ',
                                 font=("Courier", 12, 'bold')).pack(side=LEFT, ipadx=0, padx=0, pady=0)
YPosEntry = Entry(YPosFrame)
YPosEntry.pack(side=LEFT)
YPosEntry.insert(0,130)
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
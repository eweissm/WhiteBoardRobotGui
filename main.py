from tkinter import *
import tkinter.messagebox as tmsg

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
line_width = 3 # Width of the line shape

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
    elif shape == "Arc":
        a = canvas.create_arc(prev_x, prev_y, x, y, style=ARC)
    elif shape == "Line":
        a = canvas.create_line(prev_x, prev_y, x, y,
                               width=line_width,
                               smooth=TRUE, splinesteps=3)
    elif shape == "Text":
        a = canvas.create_text(x, y, text="Hello World")
    return a

# Create shapes on mouse dragging and resize and show the shapes on the canvas
def drawShapesOnDragging(e=""):
    global x, y
    try:
        # Update current Position
        x = e.x
        y = e.y

        #Generate Element
        element = createElms()
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
root.title("Drawing Pad")
root.minsize(600, 300) #Minimum Size of the window
# All Widgets here such as canvas, buttons etc

# Canvas
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
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
geometry_shapes = ["Line", "Rectangle", "Arc", "Oval", "Text"]
radiovalue.set("Line")  # Default Select

# Manupulates Radios from the list
for shape in geometry_shapes:
    radio = Radiobutton(frame, text=shape, variable=radiovalue, font="comicsans     12 bold", value=shape, command=shapechanger).pack(side=LEFT, padx=6,pady=3)

#Buttons
Button(frame, text="Clear", font="comicsans 12 bold",
       command=clearCanvas).pack(side=TOP, padx=6)

#Text Input
TextParametersFrame = Frame(master=root, width=100)
TextLableLable = Label(master=TextParametersFrame, text=' Your Text: ',
                                 font=("Courier", 12, 'bold')).pack(side='left', ipadx=0, padx=0, pady=0)
TextValueEntry = Entry(TextParametersFrame).pack(side=LEFT)

FontSizeLabel = Label(master=TextParametersFrame, text=' Text Size: ',
                                 font=("Courier", 12, 'bold')).pack(side='left', ipadx=0, padx=0, pady=0)
FontSizeEntry = Entry(TextParametersFrame).pack(side=LEFT)

TextParametersFrame.pack(fill=BOTH, side=TOP, expand=True)

#Gcode Input
GcodeInputFrame = Frame(master=root, width=100)
GcodeLableLable = Label(master=GcodeInputFrame, text=' Gcode Address: ',
                                 font=("Courier", 12, 'bold')).pack(side='left', ipadx=0, padx=0, pady=0)
GcodeValueEntry = Entry(GcodeInputFrame).pack(side=LEFT)
GcodeInputFrame.pack(fill=BOTH, side=TOP, expand=True)



# Status Bar
status = StringVar()
status.set("Position : x - 0 , y - 0")
statusbar = Label(root, textvariable=status, anchor="w", relief=SUNKEN)
statusbar.pack(side=TOP, fill=X)
root.mainloop()
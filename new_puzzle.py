from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
import random
import tkinter.filedialog
import os


#                             ***   1 - Logic for ALL Tiles   ***


class Tiles:
    def __init__(self, grid):       # initialise required variables
        self.tiles = []
        self.grid = grid
        self.gap = None
        self.moves = 0

    def add(self, tile):            # appends each tile to the Board
        self.tiles.append(tile)

    def getTile(self, *pos):        # returns the position of the tile
        for tile in self.tiles:
            if tile.pos == pos:
                return tile

    def getTileAroundGap(self):     # returns the tile around the empty gap
        gRow, gCol = self.gap.pos
        return self.getTile(gRow, gCol-1), self.getTile(gRow-1, gCol), self.getTile(gRow, gCol+1), self.getTile(gRow+1, gCol)

    def changeGap(self, tile):      # updates the position of 'gap' by incrementing it by 1 in any direction
        try:
            gPos = self.gap.pos
            self.gap.pos = tile.pos
            tile.pos = gPos
            self.moves+=1
        except:
            pass

    def slide(self, key):           # enables the player to 'slide' the tile, with help of arrow keys on keyboard
        left, top, right, down = self.getTileAroundGap()
        if key == 'Up':
            self.changeGap(down)
        if key == 'Down':
            self.changeGap(top)
        if key == 'Left':
            self.changeGap(right)
        if key == 'Right':
            self.changeGap(left)
        self.show()

    def shuffle(self):              # 'Shuffles' all tiles randomly at the start of the game
        random.shuffle(self.tiles)
        i = 0
        for row in range(self.grid):
            for col in range(self.grid):
                self.tiles[i].pos = (row, col)
                i+=1

    def show(self):                 # displays all the tiles present on the board
        for tile in self.tiles:
            if self.gap != tile:
                tile.show()

    def setGap(self, index):        # sets gap between adjacent tiles
        self.gap = self.tiles[index]

    def isCorrect(self):            # checks if each 'tile' is in correct position as displayed in original image
        for tile in self.tiles:
            if not tile.isCorrectPos():
                return False
        return True




#                                 ***    2  --  Logic for EACH Tile   ***



class Tile(Label):              # initialising the variables
    def __init__(self, parent, image, pos):
        Label.__init__(self, parent, image=image)

        self.image = image
        self.pos = pos
        self.curPos = pos

    def show(self):             # displays EACH 'tile' that was divided from the original image
        self.grid(row=self.pos[0], column=self.pos[1])

    def isCorrectPos(self):     # sets the 'correct' position of each tile in regards to the 'original image'
        return self.pos == self.curPos






#                              ***    3  --  Logic for the Board    ***




class Board(Frame):
    MAX_BOARD_SIZE = 1000       # initialising MAX Board size
    def __init__(self, parent, image, grid, win, *args, **kwargs):      # initialising all variables
        Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.grid = grid
        self.win = win
        self.image = self.openImage(image)
        self.tileSize = self.image.size[0]/self.grid
        self.tiles = self.createTiles()
        self.tiles.shuffle()
        self.tiles.show()
        self.bindKeys()

    def openImage(self, image):         # 'Opens' the image selected by player
        image = Image.open(image)
        if min(image.size) > self.MAX_BOARD_SIZE:
            image = image.resize((self.MAX_BOARD_SIZE, self.MAX_BOARD_SIZE), Image.ANTIALIAS)
        if image.size[0] != image.size[1]:
            image = image.crop((0, 0, image.size[0], image.size[0]))
        return image

    def bindKeys(self):                 # 'binds' the arrow keys for controlling the tile on Board
        self.bind_all('<Key-Up>', self.slide)
        self.bind_all('<Key-Down>', self.slide)
        self.bind_all('<Key-Right>', self.slide)
        self.bind_all('<Key-Left>', self.slide)

    def slide(self, event):             # moves tile to new position as played by player
        self.tiles.slide(event.keysym)
        if self.tiles.isCorrect():
            self.win(self.tiles.moves)

    def createTiles(self):              # Creates new tiles from original image by cropping specific size for each tile,
                                        # as per the dimensions of the original image
        tiles = Tiles(self.grid)
        for row in range(self.grid):
            for col in range(self.grid):
                x0 = col*self.tileSize
                y0 = row*self.tileSize
                x1 = x0+self.tileSize
                y1 = y0+self.tileSize
                tileImage = ImageTk.PhotoImage(self.image.crop((x0, y0, x1, y1)))
                tile = Tile(self, tileImage, (row, col))
                tiles.add(tile)
        tiles.setGap(-1)
        return tiles





#                              ***   4  --  Main class consisting of PRIME functions   ***




class Main:
    def __init__(self, parent):             # initialising required variables
        self.parent = parent
        self.board = Frame(self.parent)
        self.winFrame = Frame(self.parent)
        self.mainFrame = Frame(self.parent)
        self.image = StringVar()
        self.winText = StringVar()
        self.grid = IntVar()
        self.create_widgets()

    def create_widgets(self):               # Creates widgets such as :- Frames, Labels, Entries, Buttons, Option Menus.
        Label(self.mainFrame, text="Sliding Puzzle", font=('', 50)).pack(padx=10, pady=10)
        frame = Frame(self.mainFrame)
        Label(frame, text='Image').grid(sticky=W)
        Entry(frame, textvariable=self.image, width=50).grid(row=0, column=1, padx=10, pady=10)
        Button(frame, text='Browse', command=self.browse).grid(row=0, column=2, padx=10, pady=10)
        Label(frame, text='Grid').grid(sticky=W)
        OptionMenu(frame, self.grid, *[1, 2, 3, 4, 5]).grid(row=10, column=1, padx=10, pady=10, sticky=W)
        frame.pack(padx=10, pady=10)
        Button(self.mainFrame, text='Start', command=self.start).pack(padx=10, pady=10)
        self.mainFrame.pack()
        self.board = Frame(self.parent)
        self.winFrame = Frame(self.parent)
        Label(self.winFrame, textvariable=self.winText, font=('', 50)).pack(padx=10, pady=10)
        Button(self.winFrame, text='Play Again', command=self.playAgain).pack(padx=10, pady=10)

    def start(self):                 # Kick Starts the Game when we press the 'Start' button
        image = self.image.get()
        grid = self.grid.get()
        if os.path.exists(image):
            self.board = Board(self.parent, image, grid, self.win)
            self.mainFrame.pack_forget()
            self.board.pack()

    def browse(self):   # The 'Browse' button is used to browse and select images which we want to create the puzzle of.
        self.image.set(tkinter.filedialog.askopenfilename(title='Select Image', filetype=(('png File', '*.png'), ('jpg File', '*.jpg'))))

    def win(self, moves):   # Declares that the player has WON in the respective number of moves.
        self.board.pack_forget()
        self.winText.set('You Won in {0} moves!'.format(moves))
        self.winFrame.pack()

    def playAgain(self):    # Asks the player if he/she wants to play again.
        self.winFrame.pack_forget()
        self.mainFrame.pack()





#                               5  --  Executes the whole program by running the 'Main' class in a loop.



if __name__=="__main__":
    root = Tk()             # set root variable as Tkinter method call
    Main(root)              # execute the root Tk call from the 'Main' class
    root.mainloop()         # keep displaying the root window in a continuous loop


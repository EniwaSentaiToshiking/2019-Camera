import tkinter
from tkinter import *
from PIL import Image, ImageTk
import os
import glob
import random
import sys

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256

class AnnotationTool():

    def __init__(self, master, data_dir):
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)
    
    # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.imagepath = ''
        self.tkimg = None
        self.dataDir = data_dir
    
    # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None
    
    #----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 22, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 6, column = 1, columnspan = 2, sticky = W+E)
        self.deleteBtn = Button(self.ctrPanel, text='Delete', width = 10, command = self.test_method)
        self.deleteBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)
    
    def loadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
        
        # get image list
        self.imageDir = os.path.join(
            self.dataDir, '%03d' % (self.category))
        # 最終更新順で降順ソート（古い順）
        self.imageList = sorted(glob.glob(os.path.join(self.imageDir, '*.jpg')), key=os.path.getmtime, reverse=True)
        print(self.imageDir)
        if len(self.imageList) == 0:
            print ('No .jpg images found in the specified dir!')
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = os.path.join(
            self.dataDir, r'labels', '%03d' % (self.category))
        if not os.path.exists(self.outDir):
            print(self.outDir)
            os.makedirs(self.outDir)

        self.loadImage()
        print ('%d images loaded from %s' %(self.total, s))
    
    def loadImage(self):
        # load image
        self.imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(self.imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))
        print ('Image. %s loaded' %(str(self.imagepath)))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(self.imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
##                    print tmp
                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
    
    def test_method(self):

        if self.labelfilename == '':
            return

        try:
            os.remove(self.imagepath)
            os.remove(self.labelfilename)
            print('delete: %s', str(self.imagepath))
            print('delete: %s', str(self.labelfilename))
            self.imagepath = ''
            self.labelfilename = ''
        except Exception as e:
            print(str(e))

        self.loadDir()

    def clearBBox(self):
            for idx in range(len(self.bboxIdList)):
                self.mainPanel.delete(self.bboxIdList[idx])
            self.listbox.delete(0, len(self.bboxList))
            self.bboxIdList = []
            self.bboxList = []

    def prevImage(self, event = None):
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.cur = idx
            self.loadImage()


if __name__ == '__main__':
    if len(sys.argv) < 2:
            print ("please set data directory path.")
            exit(-1)
    data_dir = sys.argv[1]
    root = tkinter.Tk()
    tool = AnnotationTool(root, data_dir)
    root.resizable(width =  True, height = True)

    root.mainloop()
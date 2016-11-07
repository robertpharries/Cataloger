#Robert Harries
#Catalog
#started 9/2/13
#fin 4/6/13
 
#Import the widget librarys to use, wxPython for its widgets, system, controller for the operating system fileing,
#pickle for encodeing for saving, and a sorter method for the detail items list
import os
import wx
import sys
import pickle
from datetime import datetime
from wx.lib.mixins.listctrl import ColumnSorterMixin
from wx.lib.wordwrap import wordwrap
 
#Creates dictionary for global use
itemDict = {}

#Creates tuple set for global use
itemTup = {}

#States the variable itemOpen and sets it to global, and gives the value of false
global itemOpen
itemOpen = False

#States the wildcard, which is used in the open/save dialogs to limit the type of file chosen/saved
wildcard = "Text file (*.txt)|*.txt"

#Sets the font for later use in the printing
FONTSIZE = 12

#Use of the time funtion in python to get the current time for receipting
now = datetime.now()
day = str(now.day)
month = str(now.month)
year = str(now.year)
hour = str(now.hour)
minute = str(now.minute)
second = str(now.second)
day = day.rjust(2, "0")
month = month.rjust(2, "0")
year = year.rjust(2, "0")
hour = hour.rjust(2, "0")
minute = minute.rjust(2, "0")
second = second.rjust(2, "0")
#Puts the time and date into correct format
time = "%s/%s/%s %s:%s:%s" % (day, month, year, hour, minute, second)
 
#Create main program
class catlog(wx.Frame):
    #Variables for use in other classes 
    #Allows the editing class to know which item to edit
    selectedItem = "clear"
    #Variables for receipt details
    staffName = "clear"
    customerName = "clear"
    customerAddress = "clear"
    customerPhone = "clear"
    #Dictionary for checkout list
    checkoutItemList = {}
    #Dictionary for the ordering list
    orderDict = {}
    #Dictionary to hold received orders information
    rcvOrderDict = {}
    #Mark up percentage
    markUp = 0
    #
    subtot = float(0)
    #What will be executed at initialization of the program
    def __init__(self, parent, id):
        #Creates and sizes the main window
        wx.Frame.__init__(self, parent, id, "Sales", size = (500, 500))
 
        #Creates a panel within the main window that will allow for widgets to be placed, but also include scroll bars, unlike a regular panel
        self.panel = wx.Panel(self)
 
        #Creates a status bar at the bottom of the window
        statusBar = self.CreateStatusBar()
        #Defines a menu bar to be later placed at the top of the window
        menuBar = wx.MenuBar()
       
        #Creates menus for later use on the menu bar
        firstMenu = wx.Menu()
        secondMenu = wx.Menu()
        thirdMenu = wx.Menu()
        fourthMenu = wx.Menu()
 
        #Creates selections in menus
        new = firstMenu.Append(wx.NewId(), "New", "Creates new session")
        load = firstMenu.Append(wx.NewId(), "Open...", "Load saved item lists")
        save = firstMenu.Append(wx.NewId(), "Save...", "Save current item list")
        firstMenu.AppendSeparator()
        quitPrgm = firstMenu.Append(wx.NewId(), "Quit", "Closes the program")
        add = secondMenu.Append(wx.NewId(), "Add Item", "Add item to current list")
        edit = secondMenu.Append(wx.NewId(), "Edit Item", "Edit an items values")
        secondMenu.AppendSeparator()
        deleteMenuBtn = secondMenu.Append(wx.NewId(), "Delete Item", "Delete item(s) from inventory")
        itemListMenu = thirdMenu.Append(wx.NewId(), "Item List", "Displays detailed current item list")
        thirdMenu.AppendSeparator()
        orders = thirdMenu.Append(wx.NewId(), "Orders", "Displays the current and pending orders")
        rcvOrder = thirdMenu.Append(wx.NewId(), "Receive Order", "Finalise order and update item details accordingly")
        help = fourthMenu.Append(wx.NewId(), "Help", "Shows step by step tutorial of the use of this program")
        about = fourthMenu.Append(wx.NewId(), "About", "Shows information about the making of this program")
       
        #Gives names to menu sections
        menuBar.Append(firstMenu,"File")
        menuBar.Append(secondMenu,"Edit")
        menuBar.Append(thirdMenu, "Inquire")
        menuBar.Append(fourthMenu, "Help")
       
        #Finalizes the menu
        self.SetMenuBar(menuBar)
       
        #Adds actions to the selections in the menu, when clicked
        self.Bind(wx.EVT_MENU, self.addItem, add)
        self.Bind(wx.EVT_MENU, self.itemSel, edit)
        self.Bind(wx.EVT_MENU, self.deleteInv, deleteMenuBtn)
        self.Bind(wx.EVT_MENU, self.new, new)
        self.Bind(wx.EVT_MENU, self.loadDlg, load)
        self.Bind(wx.EVT_MENU, self.saveDlg, save)
        self.Bind(wx.EVT_MENU, self.runItemList, itemListMenu)
        self.Bind(wx.EVT_MENU, self.aboutBox, about)
        self.Bind(wx.EVT_MENU, self.Quit, quitPrgm)
        self.Bind(wx.EVT_MENU, self.orders, orders)
        self.Bind(wx.EVT_MENU, self.receiveOrder, rcvOrder)
        self.Bind(wx.EVT_MENU, self.helpPopUp, help)
       
        #Creates title, positions it, sets font
        headFont = wx.Font(19, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading = wx.StaticText(self.panel, -1, "Cataloger Inventory System - Sales", (15, 10), (500, -1), style = wx.ALIGN_CENTER)
        heading.SetFont(headFont)
 
        #Aesthetic lines
        wx.StaticLine(self.panel, pos = (160, 45), size = (2, 365), style = wx.LI_VERTICAL)
        wx.StaticLine(self.panel, pos = (180, 155), size = (285, 2), style = wx.LI_HORIZONTAL)

        #Creates inital list box for checkout list
        self.initCheck = wx.ListBox(self.panel, -1, (183, 226), (270, 123), ["No item selected"], wx.LB_SINGLE)

        #Creates initial list box in sales window
        self.initSel = wx.ListBox(self.panel, -1, (20, 50), (120, 330), ["No items in Inventory", "Add item and refresh..."], wx.LB_SINGLE)

        #Defines the nameList as a list
        self.nameList = []

        #Defines the list for getting the selected item and spliting it to get the name in the checkout list
        self.checklist = []

        self.orderNameList = []

        self.selectedOrderItems = []

        #Creates a refresh button
        #refreshBtn = wx.Button(self.panel, label = "Refresh", pos = (400, 5), size = (60, -1))
        #self.Bind(wx.EVT_BUTTON, self.cmdOut, refreshBtn)
 
        #Creates button for selecting an item for sale
        selectBtn = wx.Button(self.panel, label = "Select", pos = (50, 386), size = (60, -1))
        selectBtn.Bind(wx.EVT_BUTTON, self.subHeadingValCtrl, selectBtn)
 
        #Creates button for adding an item to checkout list
        addBtn = wx.Button(self.panel, label = "Add Item", pos = (400, 175), size = (60, -1))
        addBtn.Bind(wx.EVT_BUTTON, self.checkoutList, addBtn)
 
        #Creates checkout button
        checkOutBtn = wx.Button(self.panel, label = "Checkout!", pos = (262, 380), size = (120, -1))
        checkOutBtn.Bind(wx.EVT_BUTTON, self.customerDetails, checkOutBtn)
 
        #Creates delete button for checkouts
        delBtn = wx.Button(self.panel, label = "DEL", pos = (430, 200), size = (30,-1))
        delBtn.Bind(wx.EVT_BUTTON, self.deleteItem, delBtn)
 
        #Defines the colour white
        self.white = wx.Colour(255, 255, 255)
       
        #Creates subheadings for the item information, and defines and sets fonts for them.
        self.subHeadFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        subHeadName = wx.StaticText(self.panel, -1, "Current item: ", (180, 55), (-1, -1))
        subHeadName.SetFont(self.subHeadFont)
        subHeadPrice = wx.StaticText(self.panel, -1, "Price: ", (180, 85), (-1, -1))
        subHeadPrice.SetFont(self.subHeadFont)
        subHeadSOH = wx.StaticText(self.panel, -1, "Stock on hand: ", (180, 115), (-1, -1))
        subHeadSOH.SetFont(self.subHeadFont)
 
        subHeadQuant = wx.StaticText(self.panel, -1, "Quantity: ", (180, 175), (-1, -1))
        subHeadQuant.SetFont(self.subHeadFont)
        subHeadCurList = wx.StaticText(self.panel, -1, "Checkout list: ", (180, 205), (-1,-1))
        subHeadCurList.SetFont(self.subHeadFont)
        subHeadSubTot = wx.StaticText(self.panel, -1, "Subtotal: ", (180, 350), (-1,-1))
        subHeadSubTot.SetFont(self.subHeadFont)
 
        #Creates spinners for the quantity value in the checkout
        self.quantSpn = wx.SpinCtrl(self.panel, -1, "", (325, 177), (65, -1), style = wx.SP_WRAP)
        self.quantSpn.SetRange(1, 500)
        self.quantSpn.SetValue(1)
 
        #Centers the widget in the screen
        self.Centre()
        self.Show(True)

        #Sets initial values for checking if things have happened
        self.checkoutInitVis = True
        self.itemIsSelected = False
        self.itemListerInitWinVis = True
        self.itemListerItemAdded = False
        self.subHeadingDrawn = False
        self.itemsInDict = False
        self.detailsComplete = False

        #Runs the module to set initial boolean values
        self.initReset(self)
        
    #Module to set/reset the program to a certain state after loading/starting a new log
    def initReset(self, event):
        #Clears the checkout list
        catlog.checkoutItemList.clear()
        #Checks to see if the checkout list has been used
        if self.checkoutInitVis == False:
            #If yes, destroy the listbox
            self.checkoutListbox.Destroy()
            #Creates inital list box for checkout list
            self.initCheck = wx.ListBox(self.panel, -1, (183, 226), (270, 123), ["No item selected"], wx.LB_SINGLE)
            #Resets the check for if its been used or not
            self.checkoutInitVis = True
         
        #Is the check to see if the item lister has been used but has no items 
        if self.itemListerInitWinVis == False and self.itemsInDict == False:
            #Destroys the current list box
            self.itemListBox.Destroy()
            #Draws a new initial list box
            self.initSel = wx.ListBox(self.panel, -1, (20, 50), (120, 330), ["No items in Inventory", "Add item and refresh..."], wx.LB_SINGLE)
            #Excecutes the boolean reset module
            self.boolRes(self)

        #Is the check to see if the program is still in its inital state, but has items in the itemDict, ie, has just loaded a save
        elif self.itemListerInitWinVis == True and self.itemsInDict == True:
            #Executes the boolean reset module
            self.boolRes(self)
            #Executes the itemLister module to draw the items into the listbox
            self.itemLister(self)

        #Is the check to see if the program has items and are draw in the item list box
        elif self.itemListerInitWinVis == False and self.itemsInDict == True:
            #Executes the boolean reset module
            self.boolRes(self)
            #Resets the check for the itemlister inital window being visable
            self.itemListerInitWinVis = False
            #Executes the itemLister module to draw the new items into the item list box
            self.itemLister(self)

        if catlog.subtot != 0:
            self.subTotalPrint.Destroy()
        #Sets the subtotal to 0
        catlog.subtot = float(0)
 
        #Draws and initial value for sub total
        self.subTotalPrint = wx.StaticText(self.panel, -1, "$%.2f" % catlog.subtot, (325, 350), (-1, -1))
        self.subTotalPrint.SetFont(self.subHeadFont)
        self.subTotalPrint.SetBackgroundColour(self.white)

        #Resests the subheadings
        self.subHeadingRes(self)

    #Method for reseting boolean values to their original state
    def boolRes(self, event):
        self.itemIsSelected = False
        self.checkoutInitVis = True
        self.itemListerInitWinVis = True
        self.itemListerItemAdded = False  
        self.detailsComplete = False

    #prints out relevant information
    def cmdOut(self, event):
        print '-------\nitemDict: %s \n\nnameList: %s \n\nlen(nameList): %s \n\ncheckoutList: %s \n\nitemOpen: %s \n-------' % (itemDict, self.nameList, len(self.nameList), catlog.checkoutItemList, itemOpen)
        print 'self.checkoutInitVis = %s \n\nself.itemIsSelected = %s \n\nself.itemListerInitWinVis %s \n\nself.itemListerItemAdded = %s \n\nself.subHeadingDrawn = %s \n\nself.itemsInDict = %s' % (self.checkoutInitVis, self.itemIsSelected, self.itemListerInitWinVis, self.itemListerItemAdded, self.subHeadingDrawn, self.itemsInDict)
        print len(itemDict)

    #Creates method for the checkout list
    def checkoutList(self, event):
        #Checks if an item is selected
        if self.itemIsSelected == True:
            #checks if the initial checkout listbox is visible
            if self.checkoutInitVis == True:
                #Destroys initial checkoutlist
                self.initCheck.Destroy()
                #Tells the program that the checkout window is now not the initial
                self.checkoutInitVis = False
            else:
                #Destroys current list box
                self.checkoutListbox.Destroy()
            
            if self.quantSpn.GetValue() <= itemDict[self.nameList[self.itemListBox.GetSelection()]]["SOH"]:
                #Checks if the chosen item is not in the checkout list already
                if str(self.nameList[self.itemListBox.GetSelection()]) not in catlog.checkoutItemList:
                    #If not, adds item to list
                    catlog.checkoutItemList[self.nameList[self.itemListBox.GetSelection()]] = {'quantity': self.quantSpn.GetValue(), 'price': ("%.2f" % (float(itemDict[self.nameList[self.itemListBox.GetSelection()]]["price"])*int(self.quantSpn.GetValue())))}
            elif self.quantSpn.GetValue() > itemDict[self.nameList[self.itemListBox.GetSelection()]]["SOH"]:
                dlg = wx.MessageDialog(self, 'There is not enough of that item in stock', 'Error', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

            #Re-itterates the list into a new list box
            self.checklist = ["%s, x%s, $%.2f" % (val, catlog.checkoutItemList[val]['quantity'], float(catlog.checkoutItemList[val]['price'])) for val in catlog.checkoutItemList]
            self.checkoutListbox = wx.ListBox(self.panel, -1, (183, 226), (270, 123), self.checklist, wx.LB_SINGLE)

            #Creates a variable for the subtotal
            catlog.subtot = float(0)
            #itterates the prices of the checkout list, adding them up
            for val in catlog.checkoutItemList:
                catlog.subtot += float(catlog.checkoutItemList[val]['price'])
       
        #Draws the subtotal, sets font and colour
        self.subTotalPrint = wx.StaticText(self.panel, -1, "$%.2f" % catlog.subtot, (325, 350), (-1, -1))
        self.subTotalPrint.SetFont(self.subHeadFont)
        self.subTotalPrint.SetBackgroundColour(self.white)

    #Method for deleting an item from the checkout list
    def deleteItem(self, event):
        #If there is an item in the checkout list
        if len(self.checklist) > 0:
            #Get the currently selected item from the checkout list
            checkoutSelectedItem = self.checklist[self.checkoutListbox.GetSelection()]
            #Extract just the name from that selected item
            checkoutSelectedSplit = checkoutSelectedItem.split(", ")
            #Delete that item from the checkout list
            del catlog.checkoutItemList[checkoutSelectedSplit[0]]

            #Destroys the checkout list box and redraws a new one, without the deleted item
            self.checkoutListbox.Destroy()
            self.checklist = ["%s, x%s, $%.2f" % (val, catlog.checkoutItemList[val]['quantity'], float(catlog.checkoutItemList[val]['price'])) for val in catlog.checkoutItemList]
            self.checkoutListbox = wx.ListBox(self.panel, -1, (183, 226), (270, 123), self.checklist, wx.LB_SINGLE)

    #Method for the list box on the sales window
    def itemLister(self, parent, id = -1):
        #Binds an event to the method, which detects a selection of an item in the listbox and runs a method to tell the program an item is selected
        self.Bind(wx.EVT_LISTBOX, self.onSelect)
        if self.itemsInDict == True:
            #Takes the names of the items from the item dictionary and sorts them into a separate list
            self.nameList = [value for value in itemDict]
            self.nameList.sort()
            #Tells the program an item has been added
            self.itemListerItemAdded = True

            #Checks to see if there is an item selected
            if self.itemIsSelected == True:
                #Gets the name of the currently selected item in the list box
                placeSave = self.itemListBox.GetSelection()
                placeSaveVal = self.nameList[placeSave]

            #Checks if the initial item listing window is visable and there is an item added
            if self.itemListerInitWinVis == True and self.itemListerItemAdded == True:
                #Destroys the inital itemlist window
                self.initSel.Destroy()
                #Draws the new item list box
                self.itemListBox = wx.ListBox(self.panel, -1, (20, 50), (120, 330), self.nameList, wx.LB_SINGLE)
                #Tells the program that the current list box is not the initial
                self.itemListerInitWinVis = False

            #If no to above, checks if the the list box is already in use instead of the initial
            elif self.itemListerInitWinVis == False and self.itemListerItemAdded == True:
                #Destroys the list box
                self.itemListBox.Destroy()
                #Draws new list box using the refreshed name list
                self.itemListBox = wx.ListBox(self.panel, -1, (20, 50), (120, 330), self.nameList, wx.LB_SINGLE)
                #Checks if an item is selected

                if self.itemIsSelected == True:
                    #Sets the current selection to which ever item it was before the refresh
                    self.itemListBox.SetSelection(self.nameList.index(placeSaveVal))
                    #Runs method to reset the subheadings
                    self.subHeadingRes(self)

            #Runs method to draw new subheadings
            self.subHeadingValCtrl(self)

    #Method for when an item is selected
    def onSelect(self, event):
        #If the has been no item selected
        if self.itemIsSelected == False:
            #Tell the program an item has been selected
            self.itemIsSelected = True
 
    #Method for controlling the item information values
    def subHeadingValCtrl(self, event):
        if self.itemIsSelected == True:
            if self.subHeadingDrawn == True:
                #Destroys any currently displayed values
                self.SHNValue.Destroy()
                self.SHPValue.Destroy()
                self.SHSOHValue.Destroy()

            #Gets the currently selected item in the list box
            selectionKey = self.nameList[self.itemListBox.GetSelection()]
           
            #Draws the values for the selected item, sets the font, and background colour for the text
            self.SHNValue = wx.StaticText(self.panel, -1, str(selectionKey), (325, 55), (-1, -1))
            self.SHPValue = wx.StaticText(self.panel, -1, "$" + ("%.2f" % itemDict[selectionKey]['price']), (325, 85), (-1, -1))
            self.SHSOHValue = wx.StaticText(self.panel, -1, str(itemDict[selectionKey]['SOH']), (325, 115), (-1, -1))
            self.SHNValue.SetFont(self.subHeadFont)
            self.SHPValue.SetFont(self.subHeadFont)
            self.SHSOHValue.SetFont(self.subHeadFont)
            self.SHNValue.SetBackgroundColour(self.white)
            self.SHPValue.SetBackgroundColour(self.white)
            self.SHSOHValue.SetBackgroundColour(self.white)
            #Tells the program that the subheadings are visible
            self.subHeadingDrawn = True
 
    #Creates method for removing the values for selected item, to force refreshing after editing
    def subHeadingRes(self, event):
        if self.subHeadingDrawn == True:
            #Destroys any currently displayed values
            self.SHNValue.Destroy()
            self.SHPValue.Destroy()
            self.SHSOHValue.Destroy()
            #Tells the program that the values are destroyed
            self.subHeadingDrawn = False
       
    #Defines the dialog to add items
    def addItem(self, parent, id = -1):
        #Creates a text entry widget in wx
        addItemWin = wx.TextEntryDialog(None, "Enter item name:", "Add Item", "Item...")
       
        #If statement to see if the ok button was clicked.
        if addItemWin.ShowModal() == wx.ID_OK:
            #Checks to see if the entered item name is not in the item dictionary
            if str(addItemWin.GetValue()).lower() not in itemDict:
                itemDict[str(addItemWin.GetValue()).lower()] = {'price': 0.00, 'SOH': 0, "capacity": 0, 'MPL': 0}
               
                #Checks if an item has not been added
                if self.itemsInDict == False:
                    #Sets the var so that the program knows an item has been added
                    self.itemsInDict = True
               
                #Executes the itemLister method
                self.itemLister(parent, id)

                #Runs the edit window for the newly added item
                catlog.selectedItem = str(addItemWin.GetValue()).lower()
                self.runValEnt(self)
           
            #If the entered item is in the item dictionary
            elif str(addItemWin.GetValue()).lower() in itemDict:
                #Creates a dialog box to tell the user that the item already exists
                dlg = wx.MessageDialog(self, 'That item already exists.', 'Error', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

    #Method for deleting an item from the inventory
    def deleteInv(self, event):
        #Defines a clear list for the deleted items
        deleteList = []

        #If there is an item in the name list
        if len(self.nameList) > 1:
            #Displys a warning message
            dlg = wx.MessageDialog(self, 'Warning: Deleting items included in future received orders may cause issues.', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

            #Creates a multi choice window for the item list
            delSel = wx.MultiChoiceDialog(self, "Select items to Delete", "Delete selection", self.nameList)

            #If an item(s) is selected, add them to the delete list
            if delSel.ShowModal() == wx.ID_OK:
                deleteList = delSel.GetSelections()

            #If the number of selected items is less than the number of items in the inventory
            if len(deleteList) < len(self.nameList):
                x = 0
                #Changes the original index values in the delete list to their actual names
                for i in deleteList:
                    deleteList[x] = self.nameList[i]
                    x += 1

                #Deletes the items from the inventory
                for name in deleteList:
                    del itemDict[name]

                #Runs the item lister to refresh to a new item list, and the subheading reseter
                self.subHeadingRes(self)
                self.itemLister(self)

            #If there is the same amount of items selected to the name list
            else:
                #Displays a message preventing the deletion of all the items
                dlg = wx.MessageDialog(self, 'You cannot delete all the items in an inventory. \nPress File > New to start a new inventory', 'Error', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy() 

        #If there are none/1 items in the name list
        else:
            #Displays a message saying you cant delete the only item in the inventory
            dlg = wx.MessageDialog(self, 'You cannot delete the only item in an inventory. \nPress File > New to start a new inventory', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    #Method for what will be excecuted when the new button is pressed
    def new(self, event):
        #Prompts the user with a dialog asking if they would like to continue
        dlg = wx.MessageDialog(self, "Unsaved changes will be lost. Continue?", "Just incase", wx.YES_NO | wx.ICON_INFORMATION)
        #If yes, excecute the following
        if dlg.ShowModal() == wx.ID_YES:
            #Clear itemDict and checkoutItemList
            itemDict.clear()
            self.itemsInDict = False 
            #Excecute modules to reset the program back to initial state
            self.initReset(self)
            self.subHeadingRes(self)
        #Destroys the dialog
        dlg.Destroy()
        
    #Method to load a file into the program
    def loadDlg(self, event):
        #Brings up dialog to browse for file to open
        dlg = wx.FileDialog(self, message = "Choose a file", defaultDir = os.getcwd(), defaultFile = "", wildcard = wildcard, style = wx.OPEN)
        #If yes, execute the following
        if dlg.ShowModal() == wx.ID_OK:
            #Resets the nameList
            self.nameList = []
            #Retrieves the chosen files path
            path = dlg.GetPath()
            #Using pickle, loads that path
            temp = pickle.load(open(path, "rb"))
            itemDict.clear()
            #Sets itemDict to the contents of the file that was opened
            itemDict.update(temp)
            self.itemsInDict = True
            #Executes modules to reset the program back to the initial state
            self.initReset(self)
            self.subHeadingRes(self)
        #Destroys the browse dialog
        dlg.Destroy()

    #Method to save the current itemDict
    def saveDlg(self, event):
        fileSaveStr = "Inventory, %s_%s_%s" % (day, now.strftime("%B"), year)
        #Creates a dialog to browse the computer for a location to save
        dlg = wx.FileDialog(self, message = "Choose a file", defaultDir = os.getcwd(), defaultFile = fileSaveStr, wildcard = wildcard, style = wx.SAVE)
        #When yes is pressed
        if dlg.ShowModal() == wx.ID_OK:
            #Retrieves the path
            path = dlg.GetPath()
            #Uses pickle to save the file
            pickle.dump(itemDict, open(path, "wb"))
        #Destroys the dialog
        dlg.Destroy()

    #Defines and opens an "about" box for the program
    def aboutBox(self, event):
        #Gives the dialog information store a reference
        info = wx.AboutDialogInfo()
        #Adds a name to the reference
        info.Name = "Catalog"
        #Adds a version to the reference
        info.Version = "1.6.1"
        #Adds copywrite information to the reference
        info.Copyright = "(C) Robert Harries 2013"
        #Adds a description to the reference
        info.Description = wordwrap('Cataloger Inventory System is for any business in need of keeping track of stock! \n\nThanks goes to the following... \n    zetcode.com\n    codeacademy.com\n    Ubbn on GitHub\n    the developers of wxPython help file\n    and of course the Python Docs', 450, wx.ClientDC(self))
        #Adds a link to a website to the reference
        info.WebSite = ("http://www.youtube.com/watch?v=_sarYH0z948", "_")
        #Adds a list of developers to the reference

        #Runs an about box using the information store just stated
        wx.AboutBox(info)

    #Method for the help information
    def helpPopUp(self, event):
        dlg = wx.MessageDialog(self, 'There is a help video in the same directory as this program!!', 'Halp', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    #Defines the dialog for item selection prior to item value editing
    def itemSel(self, parent, id = -1):
        #Takes the names of the items from the item dictionary and sorts them into a separate list
        self.nameList = [value for value in itemDict]
        self.nameList.sort()
       
        #Creates the single choice dialog window in wx
        itemSct = wx.SingleChoiceDialog(None, 'Select item to edit:', 'Item Select', [value for value in self.nameList])
       
        #If statement to see if the ok button was pressed
        if itemSct.ShowModal() == wx.ID_OK:
            #If ok button was pressed, chosen value is saved into variable and runs handler to open editor class
            catlog.selectedItem = itemSct.GetStringSelection()
            self.runValEnt(self)
       
        #Destroys the window once job has completed
        itemSct.Destroy()

    #Method for aquiring the details required for a receipt
    def customerDetails(self, parent, id = -1):
        #If there is an item in the checkout list
        if len(catlog.checkoutItemList) > 0:
            #Sets a check to see if the details were successfully entered
            self.detailsComplete = False
            #Displays a text entry to get the staff name
            staffName = wx.TextEntryDialog(None, "Enter your name:", "Staff Assistant Name", "First and Last name...")

            if staffName.ShowModal() == wx.ID_OK:
                #Displays a text entry to get the customer name
                customerNameEntry = wx.TextEntryDialog(None, "Enter Customer name:", "Customer Name", "First and Last name...")

                if customerNameEntry.ShowModal() == wx.ID_OK:
                    #Displays a text entry to get the customer address
                    customerAddressEntry = wx.TextEntryDialog(None, "Enter Customer Address:", "Customer Address", "No., Street, Town...")

                    if customerAddressEntry.ShowModal() == wx.ID_OK:
                        #Displays a text entry to get the customer's phone number
                        customerPhoneEntry = wx.TextEntryDialog(None, "Enter Customer Phone Number:", "Customer Phone Number", "Number...")

                        if customerPhoneEntry.ShowModal() == wx.ID_OK:
                            #Sets the holder of the value to the entered value
                            catlog.customerPhone = str(customerPhoneEntry.GetValue())
                            #Tells the program the details were all entered
                            self.detailsComplete = True

                        #Sets the holder of the value to the entered value
                        catlog.customerAddress = str(customerAddressEntry.GetValue())
                    #Sets the holder of the value to the entered value
                    catlog.customerName = str(customerNameEntry.GetValue())
                #Sets the holder of the value to the entered value
                catlog.staffName = str(staffName.GetValue())

            #Itterates through the item dictionary and takes off the quanitiy of the items in the checkout list
            for value in catlog.checkoutItemList:
                itemDict[value]["SOH"] = itemDict[value]["SOH"] - catlog.checkoutItemList[value]["quantity"]

            #Resets all the values if the details were not completely entered
            if self.detailsComplete == False:
                catlog.staffName = "clear"
                catlog.customerName = "clear"
                catlog.customerAddress = "clear"
                catlog.customerPhone = "clear"
            
            #if the details were entered fully, run the recepiting method
            elif self.detailsComplete == True:
                self.exeCheckFin(self)

        #If there are no items in the checkout list then display a message telling the user to add one
        else:
            dlg = wx.MessageDialog(self, 'There are no items in the Checkout list! Please add an item to the Checkout list before attempting to checkout', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    #Method for controlling orders
    def orders(self, parent, id = -1):
        #If there are items in the item dict
        if self.itemsInDict == True:
            #Sets the initial value for the check if the process was completed
            self.detailsComplete = False
            #Defines the order name list as empty
            self.orderNameList = []
            #Clears any current data from the order dictionary
            catlog.orderDict.clear()

            #Gets all the items in the item dictionary that are at or under the minimum product level and adds them to the order name list
            for value in itemDict:
                if itemDict[value]["SOH"] <= itemDict[value]["MPL"]:
                    self.orderNameList.append(value)
            
            #Creates a multi choice dialog for the order name list
            dlg = wx.MultiChoiceDialog(self, "Select items to order", "Order choosing", self.orderNameList)

            #If ok is pressed
            if (dlg.ShowModal() == wx.ID_OK):
                #Get the selected items from the multi choice dialog
                self.selectedOrderItems = dlg.GetSelections()

                x = 0
                #Itterates through the selected order items and get their name from the index in the order name list
                for i in self.selectedOrderItems:
                    self.selectedOrderItems[x] = self.orderNameList[i]
                    x += 1

                #Calculates the amount of stock needed for each item by getting the capacity and taking away the amount already in stock
                for i in self.selectedOrderItems:
                    catlog.orderDict[i] = {"Amount": (itemDict[i]['capacity'] - itemDict[i]['SOH'])}

                #Promts the user for the wholesale markup
                wholesaleMU = wx.TextEntryDialog(None, "Enter Wholesale Markup: ", "Wholesale Markup", "")
                if wholesaleMU.ShowModal() == wx.ID_OK:
                    catlog.markUp = int(wholesaleMU.GetValue())
                    #Tells the program that the process was done
                    self.detailsComplete = True

            #If incomplete, reset the markup value
            if self.detailsComplete == False:
                catlog.markUp = 0

            #If complete, run the order completion window
            elif self.detailsComplete == True:
                self.runOrdWin(self)

        #If there are no items, prompt user about it
        else:
            dlg = wx.MessageDialog(self, 'There are no items in the inventory to order! \nPress Edit > Add item to add an item', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def receiveOrder(self, parent, id = -1):
        #If there are items in the item dict
        if self.itemsInDict == True:
            #Brings up dialog to browse for file to open
            dlg = wx.FileDialog(self, message = "Choose a file", defaultDir = os.getcwd(), defaultFile = "", wildcard = wildcard, style = wx.OPEN)
            #If yes, execute the following
            if dlg.ShowModal() == wx.ID_OK:
                #Retrieves the chosen files path
                path = dlg.GetPath()
                #Using pickle, loads that path
                temp = pickle.load(open(path, "rb"))
                catlog.rcvOrderDict.update(temp)
                self.runRcvOrdWin(self)
            #Destroys the browse dialog
            dlg.Destroy()

        #If there are no items, prompt user about it
        else:
            dlg = wx.MessageDialog(self, 'There are no items in the inventory to order! \nPress Edit > Add item to add an item', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    #A controller for the quit button
    def Quit(self, event):
        self.Close(True)
        self.Destroy()
 
    #is a controller for executing the item details window
    def runItemList(self, event):
        #If there are items in the namelist, run the item list window
        if len(self.nameList) > 0:
            #Recreated fresh tupples for item details window
            itemTup = {index+1: (str(val), str(itemDict[val]['price']), str(itemDict[val]['SOH']), str(itemDict[val]['capacity']), str(itemDict[val]['MPL'])) for index, val in enumerate(itemDict)}
            ItemList(None, -1, 'Item List', itemTup)

        #If there are not any items in the namelist, prompt the user that there needs to be some
        else:
            dlg = wx.MessageDialog(self, 'There are no items in the inventory! \nPress Edit > Add item to add an item', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    #Is a controller to execute the class for value entry
    def runValEnt(self, event):
        #Runs method to remove values from sales window
        self.subHeadingRes(self)
        self.new = valueEntry(parent=None, id=-1)
        self.new.Show() 

    #Is a controller to execute the class for order list generation
    def runOrdWin(self, event):
        self.newOrdWin = OrderingWindow(parent=None, id=-1)
        self.newOrdWin.Show()

    #Is a controller to execute the class for receiving orders
    def runRcvOrdWin(self, event):
        self.subHeadingRes(self)
        self.newRcvOrdWin = OrderReceivingWindow(parent=None, id=-1)
        self.newRcvOrdWin.Show()

    #Is a controller to execute the class for receipting
    def exeCheckFin(self,event):
        self.newCF = CheckoutFinalize(parent=None, id=-1)
        self.newCF.Show()

#######################################################################

#New class for Value editing
class valueEntry(wx.Frame):
    #Defines what is executed at the initialization of the class
    def __init__(self, parent, id):
        #Creates window
        self.VE = wx.Frame.__init__(self, parent, id, 'Value Entry', size = (300, 245))
        #Creates widget panel in window
        self.VEpanel = wx.Panel(self)

        priceSplit = str(itemDict[catlog.selectedItem]['price']).split(".")
 
        #Creates heading/sets font
        VEheadFont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        VEheading = wx.StaticText(self.VEpanel, -1, 'Edit Values', (80, 1), (300, -1))
        VEheading.SetFont(VEheadFont)
 
        #Creates labels for the price spinner
        priceText = wx.StaticText(self.VEpanel, -1, "Price:", (5, 43), (-1, -1))
        priceText2 = wx.StaticText(self.VEpanel, -1, "$/c", (100, 43), (-1, -1))
       
        #Creates spinner for price(dollars)
        self.priceSpnDlr = wx.SpinCtrl(self.VEpanel, -1, "", (120, 40), (65, -1), style = wx.SP_WRAP)
        #Sets the range of the spinner
        self.priceSpnDlr.SetRange(0, 500)
        #Sets the initial value of the spinner
        self.priceSpnDlr.SetValue(int(priceSplit[0]))
 
        #Creates spinner for cent value, sets values,
        self.priceSpnCnt = wx.SpinCtrl(self.VEpanel, -1, "", (195, 40), (65, -1), style = wx.SP_WRAP)
        self.priceSpnCnt.SetRange(0, 99)
        self.priceSpnCnt.SetValue(int(priceSplit[1]))
 
        #Creates spinner for SOH value, sets values, creates label
        SOHText = wx.StaticText(self.VEpanel, -1, "Stock on hand:", (5, 73), (-1, -1))
        self.SOHSpn = wx.SpinCtrl(self.VEpanel, -1, "", (195, 70), (65, -1), style = wx.SP_WRAP)
        self.SOHSpn.SetRange(0, 500)
        self.SOHSpn.SetValue(itemDict[catlog.selectedItem]['SOH'])
 
        #Creates spinner for capacity value, sets values, creates label
        CAPText = wx.StaticText(self.VEpanel, -1, "Shelf capacity:", (5, 103), (-1, -1))
        self.CAPSpn = wx.SpinCtrl(self.VEpanel, -1, "", (195, 100), (65, -1), style = wx.SP_WRAP)
        self.CAPSpn.SetRange(0, 500)
        self.CAPSpn.SetValue(itemDict[catlog.selectedItem]['capacity'])
 
        #Creates spinner for MPL value, sets values, creates label
        MPLText = wx.StaticText(self.VEpanel, -1, "Stock minimum level:", (5, 133), (-1, -1))
        self.MPLSpn = wx.SpinCtrl(self.VEpanel, -1, "", (195, 130), (65, -1), style = wx.SP_WRAP)
        self.MPLSpn.SetRange(0, 500)
        self.MPLSpn.SetValue(itemDict[catlog.selectedItem]['MPL'])
 
        #Creates a check box to let the user select automatic MPL calculation
        self.autoMPL = wx.CheckBox(self.VEpanel, -1, "Auto MPL calculation (CAP/5, user value ignored)", (5, 155), (-1, -1))
 
        #Creates ok button
        editButton = wx.Button(self.VEpanel, label = "Ok", pos = (110, 178), size = (60, -1))
        #Sets the ok button to execute
        self.Bind(wx.EVT_BUTTON, self.editDict, editButton)
 
        #Centers the widget in the screen
        self.Centre()
        self.Show(True)
 
    #Defines the editing of the dictionary and name array
    def editDict(self, parent, id = -1):
        #Gets value from spinners and appends dictionary accordingly
        itemDict[catlog.selectedItem]['price'] = ((self.priceSpnDlr.GetValue() * 100 + self.priceSpnCnt.GetValue())/100.0)
        itemDict[catlog.selectedItem]['SOH'] = self.SOHSpn.GetValue()
        itemDict[catlog.selectedItem]['capacity'] = self.CAPSpn.GetValue()
       
        #if statement to control the use of the auto MPL
        if self.autoMPL.GetValue() == True:
            itemDict[catlog.selectedItem]['MPL'] = ((self.CAPSpn.GetValue()/5)+1)

        elif self.autoMPL.GetValue() == False:
            itemDict[catlog.selectedItem]['MPL'] = self.MPLSpn.GetValue()
       
        #Destroys the class
        self.Destroy()

#######################################################################
 
#Class to control the sorting of the lists when column is selected
class SortedListCtrl(wx.ListCtrl, ColumnSorterMixin):
    #Exceuted on start
    def __init__(self, parent, item):
        #Defines the list control
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)

        #Outlines the number columns to be used
        ColumnSorterMixin.__init__(self, [len(item[val]) for val in item][0])
        #Holder for sorted list
        self.itemDataMap = item
   
    #Returns the list control
    def GetListCtrl(self):
        return self
 
#Class to draw the window for the item listing
class ItemList(wx.Frame):
    #Defines startup exceution
    def __init__(self, parent, id, title, item):
        #Check to ensure only one window is allowed to open at once
        global itemOpen
        if itemOpen == False:
            itemOpen = True
 
            #Draws window
            wx.Frame.__init__(self, parent, id, title, size=(400, 500))
            self.Bind(wx.EVT_CLOSE, self.Quit)
            #Sets a rezizing window and sets it to horizontal only
            hbox = wx.BoxSizer(wx.HORIZONTAL)
 
            #Draws a panel to place widgets on
            panel = wx.Panel(self, -1)
     
            #Draws the colums for sorting the information
            self.list = SortedListCtrl(panel, item)
            self.list.InsertColumn(0, 'Name')
            self.list.InsertColumn(1, 'Price', wx.LIST_FORMAT_RIGHT)
            self.list.InsertColumn(2, 'SOH', wx.LIST_FORMAT_RIGHT)
            self.list.InsertColumn(3, 'Capacity', wx.LIST_FORMAT_RIGHT)
            self.list.InsertColumn(4, 'MPL', wx.LIST_FORMAT_RIGHT, 60)
           
            #Gets item map from SortedListCtrl and gives it value in this class
            items = item.items()
           
            #Inserts item tupple information into the columns
            for key, data in items:
                index = self.list.InsertStringItem(sys.maxint, data[0])
                self.list.SetStringItem(index, 1, data[1])
                self.list.SetStringItem(index, 2, data[2])
                self.list.SetStringItem(index, 3, data[3])
                self.list.SetStringItem(index, 4, data[4])
                self.list.SetItemData(index, key)
           
            #Places the colums into the resizable box
            hbox.Add(self.list, 1, wx.EXPAND)
            panel.SetSizer(hbox)
           
            #Centers the widget in the screen
            self.Centre()
            self.Show(True)
 
    #Method to shut this window when the other is shut
    def Quit(self, event):
        #Tells the program its quit
        self.Destroy()

        #Tells the program 
        global itemOpen
        itemOpen = False

#######################################################################

#Class for the order list window
class OrderingWindow(wx.Frame):
    def __init__(self, parent, id):
        #Defines the frame and panel
        OWFrame = wx.Frame.__init__(self, parent, id, "Order List", size = (366, 535))
        self.OWPanel = wx.Panel(self)

        #Draws aestheticus line
        wx.StaticLine(self.OWPanel, pos = (0, 460), size = (380, 2), style = wx.LI_HORIZONTAL)

        #Draws Save and Close buttons
        saveBtn = wx.Button(self.OWPanel, label = "Save", pos = (90, 465), size = (90, -1))
        saveBtn.Bind(wx.EVT_BUTTON, self.saving, saveBtn)

        closeBtn = wx.Button(self.OWPanel, label = "Close", pos = (190, 465), size = (60, -1))
        closeBtn.Bind(wx.EVT_BUTTON, self.closing, closeBtn)

        #Defines a Spacer for the string method
        spacer = "---------------------"

        #States the order list which is for the list box (each item being a new line)
        self.orderList = [spacer, "ORDER LIST", time, spacer]

        #Defines variable for the subtotal on the receipt
        self.totalOrderPrice = 0

        #Itterates through the order dictionary
        for value in catlog.orderDict:
            #Gets the wholesale price of the item by taking off the markup from the retail price entered into the itemdictionary
            price = (itemDict[value]['price']/100)*(100-catlog.markUp)*int(catlog.orderDict[value]['Amount'])
            #Adds the current item in the itteration to the end of the order list 
            self.orderList.append("%s, x%s, $%.2f" % (value, catlog.orderDict[value]["Amount"], price))

            #Adds the current item's price to the subtota;
            self.totalOrderPrice = self.totalOrderPrice + price

        #Appends on final aesthetic details and the subtotal to the orderlist
        self.orderList.append(spacer)
        self.orderList.append("Total cost: $%.2f" % self.totalOrderPrice)

        #Draws the list box for showing the order list
        self.OWListBox = wx.ListBox(self.OWPanel, -1, (0, 0), (350, 450), self.orderList, wx.LB_SINGLE)

        self.Centre()

    #Method for saving the order dictionary to be later received
    def saving(self, event):
        fileSaveStr = "Order, %s_%s_%s" % (day, now.strftime("%B"), year)
        #Creates a dialog to browse the computer for a location to save
        dlg = wx.FileDialog(self, message = "Choose a file", defaultDir = os.getcwd(), defaultFile = fileSaveStr, wildcard = wildcard, style = wx.SAVE)
        #When yes is pressed
        if dlg.ShowModal() == wx.ID_OK:
            #Retrieves the path
            path = dlg.GetPath()
            #Uses pickle to save the file
            pickle.dump(catlog.orderDict, open(path, "wb"))
            #Clears the order dictionary
            catlog.orderDict.clear()
        #Destroys the dialog
        dlg.Destroy()

    #Method for closing the window
    def closing(self, event):
        self.Destroy()

#######################################################################

class OrderReceivingWindow(wx.Frame):
    def __init__(self, parent, id):
        #Defines the frame and panel
        ORWFrame = wx.Frame.__init__(self, parent, id, "Order List", size = (366, 535))
        self.ORWPanel = wx.Panel(self)

        #Defines the variable for the number of broken items
        self.brokenItems = 0

        #Aesthetic line yeah yeah TB
        wx.StaticLine(self.ORWPanel, pos = (0, 460), size = (380, 2), style = wx.LI_HORIZONTAL)

        #Draws Receive and print button
        saveBtn = wx.Button(self.ORWPanel, label = "Receive Order", pos = (90, 465), size = (90, -1))
        saveBtn.Bind(wx.EVT_BUTTON, self.receive, saveBtn)

        closeBtn = wx.Button(self.ORWPanel, label = "Close", pos = (190, 465), size = (60, -1))
        closeBtn.Bind(wx.EVT_BUTTON, self.closing, closeBtn)

        #Defines an aesthetic spacer for the order list box
        spacer = "---------------------"

        #Defines the orderlist as a list, with each index being a new line for the list box
        self.orderList = [spacer, "ORDER LIST", time, spacer]

        #Resests the total price
        self.totalOrderPrice = 0

        #Puts each item into a string form and then into the last place in the order list
        for value in catlog.rcvOrderDict:
            self.orderList.append("%s, x%s" % (value, catlog.rcvOrderDict[value]["Amount"]))

        #Puts a spacer at the end of the list for aestheticusing
        self.orderList.append(spacer)

        #Draws the list box with the order list in it
        self.ORWListBox = wx.ListBox(self.ORWPanel, -1, (0, 0), (350, 450), self.orderList, wx.LB_SINGLE)

        self.Centre()

    #Method for receiving an order
    def receive(self, event):
        #Itterates through the order list
        for value in catlog.rcvOrderDict:
            #If the item is in the Item Dictionary
            if value in itemDict:
                #Adds the ordered amount to the stock amount in the item dictionary for that item
                itemDict[value]['SOH'] = int(itemDict[value]['SOH']) + int(catlog.rcvOrderDict[value]["Amount"])

            #If that item is not in the item dictionary
            else:
                #Add one to the broken items counter
                self.brokenItems += 1

        #If the broken items were the same number as the items 
        if self.brokenItems == len(catlog.rcvOrderDict):
            dlg = wx.MessageDialog(self, 'No items in this order match with the current inventory. \nPlease ensure you have the correct order', 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        #If there was a broken items
        elif self.brokenItems > 0:
            #Display a message informing the user this has happened, and how many
            dlg = wx.MessageDialog(self, 'Some items were not found in inventory. \n\n%s items found errors' % self.brokenItems, 'Error', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

        #Destroys the receiving order window
        self.Destroy()

    #Method for closing
    def closing(self, event):
        #Destroys the receiving order window
        self.Destroy()

#######################################################################

class CheckoutFinalize(wx.Frame):
    #Resets the chosen save path
    path = "clear"
    def __init__(self, parent, id):
        #Defines the frame and panel for the window
        CFFrame = wx.Frame.__init__(self, parent, id, "Checkout Finalization", size = (366, 535))
        self.CFPanel = wx.Panel(self)

        #Yet more aesthetics
        wx.StaticLine(self.CFPanel, pos = (0, 460), size = (380, 2), style = wx.LI_HORIZONTAL)

        #Draws save and close buttons
        saveBtn = wx.Button(self.CFPanel, label = "Save / Print", pos = (90, 465), size = (90, -1))
        saveBtn.Bind(wx.EVT_BUTTON, self.saving, saveBtn)

        closeBtn = wx.Button(self.CFPanel, label = "Close", pos = (190, 465), size = (60, -1))
        closeBtn.Bind(wx.EVT_BUTTON, self.closing, closeBtn)

        #Defines the temporary string list as an empty list
        tempStringList = []

        #Creates spacer for looking good in the list box
        spacer = "---------------------"
        #Gets the catlog values for the staff and customer details
        SA = "Shop Assistant: %s" % catlog.staffName
        CN = catlog.customerName
        CA = catlog.customerAddress
        CP = catlog.customerPhone
        #Gets the subtotal from catlog class
        total = "Total Cost: $%.2f" % catlog.subtot

        #Creates first portion of the receipt list, for use in the list box
        self.receiptList = [spacer, SA, time, spacer, "Customer:", CN, CA, CP, spacer, ""]

        #Itterates through the items in the checkout item list
        for value in catlog.checkoutItemList:
            #Gets the values from the checkout item list and converts them to strings
            quantity = str(catlog.checkoutItemList[value]['quantity'])
            price = str(catlog.checkoutItemList[value]['price'])
            name = str(value)

            #Formats the strings
            price = "$%s" % price
            quantity = quantity.rjust(3, "0")
            price = price.rjust(12, "_")
            quantity = "x%s" % quantity

            #Puts the strings together into one string for use as one index in the orders list
            self.receiptList.append("%s|%s| %s" % (quantity, price, name))

        #Adds last aestheticiles to the end of the receipt list
        self.receiptList.append(" ")
        self.receiptList.append(spacer)
        self.receiptList.append(total)
        self.receiptList.append("")

        #Draws the list box with the receipt list as the contents
        Receipt = wx.ListBox(self.CFPanel, -1, (0, 0), (350, 450), self.receiptList, wx.LB_SINGLE)

        #Turns the receipt list into one looooooooooooong string for saving purposes
        self.receiptString = str('\n'.join(self.receiptList))

        self.Centre()

    #Method to save the receipt to file
    def saving(self, event):
        fileSaveStr = "%s, %s_%s_%s" % (catlog.customerName, day, now.strftime("%B"), year)
        #Creates a dialog to browse the computer for a location to save
        dlg = wx.FileDialog(self, message = "Choose a file", defaultDir = os.getcwd(), defaultFile = fileSaveStr, wildcard = wildcard, style = wx.SAVE)
        #When yes is pressed
        if dlg.ShowModal() == wx.ID_OK:
            #Retrieves the path
            CheckoutFinalize.path = dlg.GetPath()
            #Saves the file
            with open(CheckoutFinalize.path, "w") as text_file:
                text_file.write(self.receiptString)
            #Excecutes printing modules
            prnt = PrintFramework()
            prnt.Show()
        #Destroys the dialog
        dlg.Destroy()

    #Method for closing
    def closing(self, event):
        #Destroys the window
        self.Destroy()

#######################################################################

#Class for setting up the page for the printout
class TextDocPrintout(wx.Printout):
    def __init__(self, text, title, margins):
        #Defines the variable for the margins and the lines
        wx.Printout.__init__(self, title)
        self.lines = text.split('\n')
        self.margins = margins

    #Checks if the page that you're navagating to exists
    def HasPage(self, page):
        return page <= self.numPages

    #Gets the page info 
    def GetPageInfo(self):
        return (1, self.numPages, 1, self.numPages)

    #Method for calculating the scalling of the page so it is the correct size for the printer
    def CalculateScale(self, dc):
        #Scales the DC such that the printout is about the same as the screen scaling.
        ppiPrinterX, ppiPrinterY = self.GetPPIPrinter()
        ppiScreenX, ppiScreenY = self.GetPPIScreen()
        logScale = float(ppiPrinterX)/float(ppiScreenX)

        #Adjusts if the real page size is reduced. If page width is the same as DC width then nothing changes, otherwise scale down for the DC.
        pw, ph = self.GetPageSizePixels()
        dw, dh = dc.GetSize()
        scale = logScale * float(dw)/float(pw)

        #Set the DCs scale.
        dc.SetUserScale(scale, scale)

        #Finds the logical units per millimeter
        self.logUnitsMM = float(ppiPrinterX)/(logScale*25.4)

    #Sets up the page, using the margins and the amount of lines on a page etc
    def CalculateLayout(self, dc):
        #Determines the position of the margins and the page/line height
        topLeft, bottomRight = self.margins
        dw, dh = dc.GetSize()
        self.x1 = topLeft.x * self.logUnitsMM
        self.y1 = topLeft.y * self.logUnitsMM
        self.x2 = dc.DeviceToLogicalXRel(dw) - bottomRight.x * self.logUnitsMM 
        self.y2 = dc.DeviceToLogicalYRel(dh) - bottomRight.y * self.logUnitsMM 

        #Uses a 1mm buffer around the inside of the box, and a few pixels between each line
        self.pageHeight = self.y2 - self.y1 - 2*self.logUnitsMM
        font = wx.Font(FONTSIZE, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        dc.SetFont(font)

        #Sets the line height from the height of the characters, then gets the number of lines that fit on a page
        self.lineHeight = dc.GetCharHeight() 
        self.linesPerPage = int(self.pageHeight/self.lineHeight)

    #Prepares the layout of the page for printing
    def OnPreparePrinting(self):
        #Calculates the number of pages
        dc = self.GetDC()

        self.CalculateScale(dc)
        self.CalculateLayout(dc)
        self.numPages = len(self.lines) / self.linesPerPage

        if len(self.lines) % self.linesPerPage != 0:
            self.numPages += 1

    #Method to execute when printing a page
    def OnPrintPage(self, page):
        dc = self.GetDC()

        self.CalculateScale(dc)
        self.CalculateLayout(dc)

        #Draws a page outline at the margin points
        dc.SetPen(wx.Pen("black", 0))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        r = wx.RectPP((self.x1, self.y1),
                      (self.x2, self.y2))

        dc.DrawRectangleRect(r)
        dc.SetClippingRect(r)

        #Draws the text lines for this page
        line = (page-1) * self.linesPerPage
        x = self.x1 + self.logUnitsMM
        y = self.y1 + self.logUnitsMM

        while line < (page * self.linesPerPage):
            dc.DrawText(self.lines[line], x, y)
            y += self.lineHeight
            line += 1
            if line >= len(self.lines):
                break

        return True

class PrintFramework(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(640, 480), title="Print Framework Sample")
        self.CreateStatusBar()

        #A text widget to display the doc and let it be edited
        self.tc = wx.TextCtrl(self, -1, "",
                              style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
        self.tc.SetFont(wx.Font(FONTSIZE, wx.TELETYPE, wx.NORMAL, wx.NORMAL))
        filename = os.path.join(os.path.dirname(__file__), CheckoutFinalize.path)
        self.tc.SetValue(open(filename).read())
        self.tc.Bind(wx.EVT_SET_FOCUS, self.OnClearSelection)
        wx.CallAfter(self.tc.SetInsertionPoint, 0)

        #Creates the menu and menubar
        menu = wx.Menu()
        item = menu.Append(-1, "Print...\tF8", "Print the document")
        self.Bind(wx.EVT_MENU, self.OnPrint, item)

        menu.AppendSeparator()

        item = menu.Append(-1, "E&xit", "Close this application")
        self.Bind(wx.EVT_MENU, self.OnExit, item)
        
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")
        self.SetMenuBar(menubar)

        #Initializes the print data and set some default values
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(15,15), wx.Point(15,15))

    #Method for closing 
    def OnExit(self, evt):
        #Closes the window
        self.Close()

    #Method for clearing the selection
    def OnClearSelection(self, evt):
        evt.Skip()
        wx.CallAfter(self.tc.SetInsertionPoint,
                     self.tc.GetInsertionPoint())

    #Method for printing
    def OnPrint(self, evt):
        #Gets relevant data
        data = wx.PrintDialogData(self.pdata)
        printer = wx.Printer(data)
        text = self.tc.GetValue() 
        printout = TextDocPrintout(text, "title", self.margins)
        useSetupDialog = True

        #If the printing fails
        if not printer.Print(self, printout, useSetupDialog) \
           and printer.GetLastError() == wx.PRINTER_ERROR:
            wx.MessageBox(
                "There was a problem printing.\n"
                "Perhaps your current printer is not set correctly?",
                "Printing Error", wx.OK)

        #If the printing process is sucessful
        else:
            data = printer.GetPrintDialogData()
            #Forces a copy
            self.pdata = wx.PrintData(data.GetPrintData())
        printout.Destroy()

#######################################################################

#Keeps the program running
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = catlog(parent = None, id = -1)
    frame.Show()
    app.MainLoop()
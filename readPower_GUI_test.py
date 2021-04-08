import wx
import threading
import time, datetime
import serial
import serial.tools.list_ports

from ctypes import *
def convert(s):
    i = int(s, 16)                   # convert from hex to a Python int
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value         # dereference the pointer, get the float

class my_serial():
	def __init__(self):
		plist = list(serial.tools.list_ports.comports())
		if len(plist)<=0:
			print('No serial port')
		else:
			for i in range(len(plist)):
				if list(plist[i])[1][0:3]=='USB':
					serialName=list(plist[i])[0]
					break
			# plist_0=list(plist[0])
			# serialName=plist_0[0]
			try:
				self.ser=serial.Serial(
					serialName, 
					baudrate=9600,
					# parity=0,
					timeout=1,
					bytesize=8,
					stopbits=1)
			except Exception as e:
				print('---open port error---: ', e)
	
	def open_port(self):
		pass
		# self.ser.open()

	def close_port(self):
		self.ser.close()
		print(self.ser.is_open)

	def send_cmd(self,cmd):
		self.ser.write(cmd)

	def read_data(self):
		response=self.ser.read(9)
		data='{:02X}'.format(response[5])+'{:02X}'.format(response[6])+'{:02X}'.format(response[3])+'{:02X}'.format(response[4])
		print(time.time(),datetime.datetime.now(),convert(data))
		return data





class HelloFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(HelloFrame, self).__init__(*args, **kw)
        self.IsReading=False
        self.ReadingCmd=False
        self.ReadInterval=1
        self.OutputPath=str(datetime.datetime.today())[0:10]+'.csv'
        self.port_open=False
        self.selected_channel=[0, 1, 2, 3, 4, 5]
        self.box_sizer=wx.WrapSizer()
        self.SetAutoLayout(True)
        self.SetSizer(self.box_sizer)

        # and create a sizer to manage the layout of child widgets
        self.SetMinSize((500,650))
        self.SetMaxSize((500,650))
        self.makeTextArea()
        self.makeButtons()
        # create a menu bar
        self.makeMenuBar()

        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")
        self.Bind(wx.EVT_CLOSE, self.OnClose) 

    def makeTextArea(self):
        self.area_text = wx.TextCtrl(self, -1, u'[Info] Initialize\n', size=(700, 250),style=(wx.TE_MULTILINE |  wx.TE_DONTWRAP|wx.TE_READONLY))
        self.area_text.SetInsertionPoint(10)
        self.box_sizer.Add(self.area_text)
        self.area_text_data = wx.TextCtrl(self, -1, u'', size=(700, 250),style=(wx.TE_MULTILINE |  wx.TE_DONTWRAP|wx.TE_READONLY))
        self.area_text_data.SetInsertionPoint(10)
        self.box_sizer.Add(self.area_text_data)

    def makeButtons(self):
    	self.open_port_bt = wx.Button(self,-1, u'Open Serial Port')
    	self.box_sizer.Add(self.open_port_bt)

    	self.close_port_bt = wx.Button(self,-1, u'Close Serial Port')
    	self.box_sizer.Add(self.close_port_bt)
    	
    	self.start_rd_bt = wx.Button(self,-1, u'Start reading')
    	self.box_sizer.Add(self.start_rd_bt)

    	self.stop_rd_bt = wx.Button(self,-1, u'Stop reading')
    	self.box_sizer.Add(self.stop_rd_bt)

    	self.open_port_bt.Bind(wx.EVT_BUTTON,self.OnClickBt_open_port)

    	self.close_port_bt.Bind(wx.EVT_BUTTON,self.OnClickBt_close_port)
    	self.close_port_bt.Disable()

    	self.start_rd_bt.Bind(wx.EVT_BUTTON,self.OnClickBt_start_rd)
    	self.start_rd_bt.Disable()

    	self.stop_rd_bt.Bind(wx.EVT_BUTTON,self.OnClickBt_stop_rd)
    	self.stop_rd_bt.Disable()

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        filePathItem = fileMenu.Append(-1, "&Datafile save path...\tCtrl-H",
                "set the datafile path")
        recordIntervalItem = fileMenu.Append(-1, "&Record interval...\tCtrl-L",
                "set the recording interval")
        selectChannelItem = fileMenu.Append(-1, "&Select channel...\tCtrl-D",
                "select the data channel")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnSetPath, filePathItem)
        self.Bind(wx.EVT_MENU, self.OnSetInterval, recordIntervalItem)
        self.Bind(wx.EVT_MENU, self.OnSelectChannel, selectChannelItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnClickBt_open_port(self,event):
    	self.port=my_serial()
    	self.port.open_port()
    	self.port_open=True
    	self.open_port_bt.Disable()
    	self.close_port_bt.Enable()
    	self.start_rd_bt.Enable()
    	self.stop_rd_bt.Disable()
    	self.area_text.write("[Info] Click Open Port\n")

    	# wx.MessageBox("something")

    def OnClickBt_close_port(self,event):
    	self.port.close_port()
    	self.port_open=False
    	self.open_port_bt.Enable()
    	self.close_port_bt.Disable()
    	self.start_rd_bt.Disable()
    	self.stop_rd_bt.Disable()
    	self.area_text.write("[Info] Click Close Port\n")
    	# wx.MessageBox("something")

    def OnClickBt_start_rd(self,event):
    	self.open_port_bt.Disable()
    	self.close_port_bt.Disable()
    	self.start_rd_bt.Disable()
    	self.stop_rd_bt.Enable()
    	self.OutputFile=open(self.OutputPath,'a')
    	self.area_text.write("[Info] Click Start Reading\n")
    	self.ReadingCmd=True
    	self.ReadingThread=threading.Thread(target=self.ReadPort_test)
    	self.ReadingThread.start()
    	# wx.MessageBox("something")

    def OnClickBt_stop_rd(self,event):
    	self.ReadingCmd=False
    	# while self.ReadingThread.is_alive():
    	# 	pass
    	self.open_port_bt.Disable()
    	self.close_port_bt.Disable()
    	self.start_rd_bt.Disable()
    	self.stop_rd_bt.Disable()
    	self.area_text.write("[Info] Click Stop Reading\n")

    	# wx.MessageBox("something")

    def OnExit(self, event): # 利用
        """Close the frame, terminating the application."""
        # wx.MessageBox("Hello again from wxPython")
        self.Close(True)

    def OnClose(self, event):
    	if self.port_open:
    		self.area_text.write("[Info] Serial port is not closed, cannot close\n")
    	else:
    		self.Destroy()
    	pass

    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def OnSelectChannel(self, event):
    	dialog=wx.MultiChoiceDialog(parent = self, 
    		message = "Select the data channel to read",
    		caption = '',
    		# n = 6, 
    		choices = ['Channel 1','Channel 2', 'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6'],
    		style = wx.OK | wx.CANCEL)
    	dialog.SetSelections(self.selected_channel)
    	if dialog.ShowModal() == wx.ID_CANCEL:
        	return
    	# self.OutputPath= dialog.GetSelections()
    	self.selected_channel=dialog.GetSelections()
    	dialog.Destroy()
    	

    def OnSetPath(self, event):
    	dialog=wx.FileDialog(self, "Select data file to be saved", wildcard="text files (*.csv)|*.csv",style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    	if dialog.ShowModal() == wx.ID_CANCEL:
        	return
    	self.OutputPath= dialog.GetPath()
    	dialog.Destroy()
    	print(self.OutputPath)

    def OnSetInterval(self,event):
    	dialog=wx.TextEntryDialog(self, "set interval (unit: seconds)", caption="set time interval",
                value=str(self.ReadInterval))
    	flag=dialog.ShowModal()
    	if flag==wx.ID_OK:
    		try:
    			value=float(dialog.GetValue())
    			dialog.Destroy()
    			if value < 1:
    				self.area_text.write("[Info] Entered an interval larger than 1.\n")
    			else:
    				self.ReadInterval=value
    				self.area_text.write("[Info] Read interval is set as " +str(value) + "\n")
    		except:
    			dialog.Destroy()
    			self.area_text.write("[Info] Entered interval is not a number.\n")
    	else:
    		pass
    	
    	# print(value)

    def OnAbout(self, event):
        """Display an About Dialog"""
        dialog=wx.MessageBox("Version 1.1, 2021.04.08",
                      "About",
                      wx.OK|wx.ICON_INFORMATION)


    def ReadPort(self): # to be implemented
    	self.IsReading=True
    	while self.ReadingCmd:
    		self.area_text_data.Clear()
    		self.area_text_data.write("[Data] " + str(int(time.time())) + "," + str(datetime.datetime.now()) + "," + "power" + "\n")
    		self.OutputFile.write("[Data] " + str(int(time.time())) + "," + str(datetime.datetime.now()) + "," + "power" + "\n")
    		self.OutputFile.flush()
    		time.sleep(self.ReadInterval)
    	self.IsReading=False
    	self.close_port_bt.Enable()
    	self.start_rd_bt.Enable()
    	self.OutputFile.close()

    def ReadPort_test(self):
    	cmd1=[0x01,0x03,0x11,0x64,0x00,0x02,0x80,0xe8]
    	cmd2=[0x01,0x03,0x11,0x78,0x00,0x02,0x41,0x2e]
    	cmd3=[0x01,0x03,0x11,0x8c,0x00,0x02,0x00,0xdc]
    	cmd4=[0x01,0x03,0x12,0x68,0x00,0x02,0x40,0xaf]
    	cmd5=[0x01,0x03,0x12,0x7c,0x00,0x02,0x00,0xab]
    	cmd6=[0x01,0x03,0x12,0x90,0x00,0x02,0xc1,0x5e]
    	self.IsReading=True
    	while self.ReadingCmd:
    		self.area_text_data.Clear()
    		if 0 in self.selected_channel:
	    		self.port.send_cmd(cmd1)
	    		data=self.port.read_data()
	    		self.area_text_data.write("1," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.write("1," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.flush()
	    	if 1 in self.selected_channel:
	    		self.port.send_cmd(cmd2)
	    		data=self.port.read_data()
	    		self.area_text_data.write("2," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.write("2," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.flush()
    		if 2 in self.selected_channel:
	    		self.port.send_cmd(cmd3)
	    		data=self.port.read_data()
	    		self.area_text_data.write("3," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.write("3," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.flush()
    		if 3 in self.selected_channel:
	    		self.port.send_cmd(cmd4)
	    		data=self.port.read_data()
	    		self.area_text_data.write("4," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.write("4," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.flush()
    		if 4 in self.selected_channel:
	    		self.port.send_cmd(cmd5)
	    		data=self.port.read_data()
	    		self.area_text_data.write("5," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.write("5," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.flush()
    		if 5 in self.selected_channel:
	    		self.port.send_cmd(cmd6)
	    		data=self.port.read_data()
	    		self.area_text_data.write("6," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.write("6," + str(int(time.time())) + "," + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "," + str(convert(data)) + "\n")
	    		self.OutputFile.flush()
	    	time.sleep(self.ReadInterval)
    	self.IsReading=False
    	self.close_port_bt.Enable()
    	self.start_rd_bt.Enable()
    	self.OutputFile.close()



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='加热功率定时查询程序')
    frm.Show()
    app.MainLoop()
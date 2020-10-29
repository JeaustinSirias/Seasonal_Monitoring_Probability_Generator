from tkinter import *
from ttk import Combobox
import pandas as pd
import numpy as np
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt


class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        master.title('SMPG Project v1.0.0')

        #MISC
        self.dekad_lst = ['1-Jan', '2-Jan', '3-Jan', '1-Feb', '2-Feb', '3-Feb', '1-Mar', '2-Mar', '3-Mar', '1-Apr', '2-Apr', 
                      '3-Apr', '1-May', '2-May', '3-May', '1-Jun', '2-Jun', '3-Jun', '1-Jul', '2-Jul', '3-Jul', '1-Aug', 
                      '2-Aug', '3-Aug', '1-Sep', '2-Sep', '3-Sep', '1-Oct', '2-Oct', '3-Oct', '1-Nov', '2-Nov', '3-Nov', 
                      '1-Dec', '2-Dec', '3-Dec']

        #GUI VARIABLES
        self.V1 = IntVar(frame)
        self.V2 = IntVar(frame)
        self.V3 = StringVar(frame)
        self.V4 = StringVar(frame)
        self.V5 = IntVar(frame)
        self.V6 = IntVar(frame)
        self.V7 = IntVar(frame)
        self.V8 = IntVar(frame)
        self.V9 = IntVar(frame)
        self.V0 = IntVar(frame)
        self.fileOpen = ''
        self.out = None

        '''
        self.analogs_lst = np.arange(1, 40, 1)
        self.radio_button = IntVar(self.frame)
        #climatology
        '''

        #LABELS
        self.label0 = Label(frame, text = 'Set up climatological window')
        self.label_analogSettings=Label(frame, text='Analog years settings')
        self.labelz=Label(frame, text='Define a season to monitor')
        self.label1=Label(frame, text='Initial year:')
        self.label2=Label(frame, text='Final year:')
        self.label3=Label(frame, text='From:')
        self.label4=Label(frame, text='to:')
        self.label5=Label(frame, text='Select the number of analog years to compute:')
        self.label6=Label(frame, text='Specify the rank of analog years to show:')
        self.label7=Label(frame, text='Analyisis preferences')

        #BUTTONS
        self.HELP = Button(frame, text='About')
        self.RUN = Button(frame, text='GENERATE REPORTS', command=lambda:App.RUN(self))                                                                                                                                                                                
        self.BROWSE = Button(frame, text='Browse Files', width=25, command=lambda:App.BROWSE(self))
        self.CLEAR = Button(frame, text='Clear', width=17)
        self.entry = Entry(frame, width=54, text=self.fileOpen)
        self.FORECAST = Radiobutton(frame, text='Forecast', variable=self.V7, value=0)
        self.ANALYSIS = Radiobutton(frame, text='Observed data', variable=self.V7, value=1)
        self.SAVE = Checkbutton(frame, text='Save reports', variable=self.V8)
        self.DISPLAY = Checkbutton(frame, text='Display reports', variable=self.V9)
        self.SCENARIO = Checkbutton(frame, text='Include scenarios', variable=self.V0)

        #MENU
        self.init_clim = Combobox(frame, textvariable=self.V1, values=[None])
        self.end_clim = Combobox(frame, textvariable=self.V2, values=[None])
        self.start_dekad = Combobox(frame, textvariable=self.V3, values=tuple(self.dekad_lst))
        self.end_dekad = Combobox(frame, textvariable=self.V4, values=tuple(self.dekad_lst))
        self.analog_menu  = Combobox(frame, textvariable=self.V5, values=[None] )
        self.rank_menu  = Combobox(frame, textvariable=self.V6, values=tuple(range(2, 6)))

        #GRIDS
        self.label0.grid(row=1, column=2, columnspan=4)
        self.label_analogSettings.grid(row=5, column=2, columnspan=3)
        self.labelz.grid(row=3, column=2, columnspan=3)
        self.labelz.grid(row=3, column=2, columnspan=3)
        self.label2.grid(row=2, column=3, padx=10)
        self.label3.grid(row=4, column=1, sticky=E, padx=5)
        self.label4.grid(row=4, column=3, sticky=E, padx=5)
        self.label5.grid(row=6, column=1, pady=15, columnspan=3)
        self.label6.grid(row=7, column=1, columnspan=3)
        self.label7.grid(row=6, column=0)
        self.init_clim.grid(row=2, column=2, pady=15)
        self.end_clim.grid(row=2, column=4)
        self.start_dekad.grid(row=4, column=2, pady=10)
        self.end_dekad.grid(row=4, column=4)
        self.analog_menu.grid(row=6, column=4)
        self.rank_menu.grid(row=7, column=4)
        self.HELP.grid(row=9, column=4)
        self.RUN.grid(row=2, column=0, columnspan=1)
        self.BROWSE.grid(row=0, column=0, pady=20, columnspan=2, sticky=W+E)
        self.entry.grid(row=0, column=2, columnspan=3, padx=0, sticky=E)
        self.CLEAR.grid(row=9, column=0, pady=15, sticky=W)
        self.FORECAST.grid(row=7, column=0, sticky=NW)
        self.ANALYSIS.grid(row=8, column=0, sticky=NW)
        self.SAVE.grid(row=3, column=0, sticky=W)
        self.DISPLAY.grid(row=4, column=0, sticky=W)
        self.SCENARIO.grid(row=5, column=0, sticky=W)

    def BROWSE(self):
        try:
            file = filedialog.askopenfile(mode='r', filetypes=[('csv files', '*.csv')]) 
            indir = str(file.name)
            self.entry.delete(0, END)
            self.entry.insert(0, indir)

        except AttributeError:
            return 0

        if file is not None: 
            data = pd.read_csv(file, header=None)
            df = pd.DataFrame(data)

            #SETUP HEADER AS STRING LIKE 'YEAR|DEK' FIRST 4 CHARACTERS DEFINE YEAR AND LAST 2 CHARACTERS DEFINE ITS DEK
            header = list(df.loc[0][1:-1])
            header_str = []
            for i in range(len(header)):
                head =  str(header[i])[0:6]
                header_str.append(head)

            locNames = np.array(df.loc[1:][0]); locs = [] #locations' names
            for i in range(len(locNames)):
                try:
                    key = str(int(locNames[i]))
                    locs.append(key)

                except ValueError:
                    key = locNames[i]
                    locs.append(key)

            one = int(header_str[0][0:4])
            two = int(header_str[-1][0:4])
            yrs = tuple(np.arange(one, two, 1))
            yrsNum = tuple(np.arange(2, len(yrs) + 1, 1))

            #set up new menus in comboboxes
            self.init_clim['values'] = yrs
            self.end_clim['values'] = yrs
            self.analog_menu['values'] = yrsNum

            raw = np.array(df.loc[1:]).transpose()[1:-1].transpose()
            scenarios = np.array(df.loc[1:]).transpose()[-1].transpose()
            scenarios = [float(scenarios[i]) for i in np.arange(0, len(scenarios), 1) if scenarios[i] != None]

            #=OUTPUT: returns a 3rd dim array with this features: [locations'_tags, header, raw data]
            self.out = np.array([locs, np.array(header_str), raw, scenarios])
            messagebox.showinfo('Data loaded', 'Input dataset goes from {init} to {end}'.format(init=self.out[1][0][0:4], end=self.out[1][-1][0:4]))

        

    def RUN(self):

        a = [1,2,4,7,9,7,8]
        b = range(len(a))
        plt.plot(b, a)
        plt.show()

    

    def CLEAR(self):
        pass

    def HELP(self):
        pass


root = Tk()
app = App(root)
root.mainloop()
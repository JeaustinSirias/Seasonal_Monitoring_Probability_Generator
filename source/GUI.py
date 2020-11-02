import utils
from core import smpgTool
import tkinter as tk
from ttk import Combobox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class App():
    def __init__(self, master):
        frame = tk.Frame(master)
        frame.pack()
        master.title('SMPG Project v1.0.0')

        # MISC
        self.dekad_lst = utils.dek_list()

        # GUI VARIABLES
        self.V1 = tk.IntVar(frame)
        self.V2 = tk.IntVar(frame)
        self.V3 = tk.StringVar(frame)
        self.V4 = tk.StringVar(frame)
        self.V5 = tk.IntVar(frame)
        self.V6 = tk.IntVar(frame)
        self.V7 = tk.IntVar(frame)
        self.V8 = tk.IntVar(frame)
        self.V9 = tk.IntVar(frame)
        self.V0 = tk.IntVar(frame)
        self.fileOpen = ''
        self.dataset = None

        '''
        self.analogs_lst = np.arange(1, 40, 1)
        self.radio_button = IntVar(self.frame)
        '''

        # LABELS
        self.label0 = tk.Label(frame, text = 'Set up climatological window')
        self.label_analogSettings=tk.Label(frame, text='Analog years settings')
        self.labelz = tk.Label(frame, text='Define a season to monitor')
        self.label1 = tk.Label(frame, text='Initial year:')
        self.label2 = tk.Label(frame, text='Final year:')
        self.label3 = tk.Label(frame, text='From:')
        self.label4 = tk.Label(frame, text='to:')
        self.label5 = tk.Label(frame, text='Select the number of analog years to compute:')
        self.label6 = tk.Label(frame, text='Specify the rank of analog years to show:')
        self.label7 = tk.Label(frame, text='Analyisis preferences')

        # BUTTONS
        self.HELP = tk.Button(frame, text='About')
        self.RUN = tk.Button(frame, text='GENERATE REPORTS', command=lambda:self.Run(self))                                                                                                                                                                                
        self.BROWSE = tk.Button(frame, text='Browse Files', width=25, command=lambda:self.Browse())
        self.CLEAR = tk.Button(frame, text='Clear', width=17)
        self.FORECAST = tk.Radiobutton(frame, text='Forecast', variable=self.V7, value=0)
        self.ANALYSIS = tk.Radiobutton(frame, text='Observed data', variable=self.V7, value=1)
        self.SAVE = tk.Checkbutton(frame, text='Save reports', variable=self.V8)
        self.DISPLAY = tk.Checkbutton(frame, text='Display reports', variable=self.V9)
        self.SCENARIO = tk.Checkbutton(frame, text='Include scenarios', variable=self.V0)

        # ENTRIES
        self.entry = tk.Entry(frame, width=54, text=self.fileOpen)

        # MENUS
        self.init_clim = Combobox(frame, textvariable=self.V1, values=[None])
        self.end_clim = Combobox(frame, textvariable=self.V2, values=[None])
        self.start_dekad = Combobox(frame, textvariable=self.V3, values=tuple(self.dekad_lst))
        self.end_dekad = Combobox(frame, textvariable=self.V4, values=tuple(self.dekad_lst))
        self.analog_menu  = Combobox(frame, textvariable=self.V5, values=[None] )
        self.rank_menu  = Combobox(frame, textvariable=self.V6, values=tuple(range(2, 6)))

        # GRIDS
        self.label0.grid(row=1, column=2, columnspan=4)
        self.label_analogSettings.grid(row=5, column=2, columnspan=3)
        self.labelz.grid(row=3, column=2, columnspan=3)
        self.label1.grid(row=2, column=1, padx=10)
        self.label2.grid(row=2, column=3, padx=10)
        self.label3.grid(row=4, column=1, sticky=tk.E, padx=5)
        self.label4.grid(row=4, column=3, sticky=tk.E, padx=5)
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
        self.BROWSE.grid(row=0, column=0, pady=20, columnspan=2, sticky=tk.W+tk.E)
        self.entry.grid(row=0, column=2, columnspan=3, padx=0, sticky=tk.E)
        self.CLEAR.grid(row=9, column=0, pady=15, sticky=tk.W)
        self.FORECAST.grid(row=7, column=0, sticky=tk.NW)
        self.ANALYSIS.grid(row=8, column=0, sticky=tk.NW)
        self.SAVE.grid(row=3, column=0, sticky=tk.W)
        self.DISPLAY.grid(row=4, column=0, sticky=tk.W)
        self.SCENARIO.grid(row=5, column=0, sticky=tk.W)

    def Browse(self):
        file = tk.filedialog.askopenfile(mode='r', filetypes=[('csv files', '*.csv')])
        indir = str(file.name)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, indir)

        if file is not None:
            fst_yr, lst_yr, IDs, raw_data = utils.read(file)
        
        # Updating attributes 
        yrs = tuple(range(fst_yr, lst_yr))
        yrs_num = tuple(range(1, 1+len(yrs)))
        self.init_clim['values'] = yrs
        self.end_clim['values'] = yrs
        self.analog_menu['values'] = yrs_num
        self.dataset = IDs, raw_data

        # Show success message if everything went ok
        tk.messagebox.showinfo('Data loaded', 'Input dataset goes from {} to {}'.format(fst_yr, lst_yr))
    
    def Run(self, fst_cm, lst_cm, fst_dk, lst_dk, analogs_num, rank):
        # Setting up conditions to run & error messages
        if self.dataset == None:
            tk.messagebox.showerror('No dataset loaded', 'You must input a dataset first')
            return
        # Starting up SMPG enviroment
        fst_yr, lst_yr, IDs, raw_data = self.dataset
        SIZE = len(IDs)
        #core.smpgTool(fst_yr, lst_yr, fst_cm, lst_cm, fst_dk, lst_dk, SIZE, analogs_num)

        pass

        

    def RUN(self):

        a = [1,2,4,7,9,7,8]
        b = range(len(a))
        plt.plot(b, a)
        plt.show()

    

    def CLEAR(self):
        pass

    def HELP(self):
        pass


root = tk.Tk()
app = App(root)
root.mainloop()

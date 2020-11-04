import os
import utils
from core import smpgTool
import tkinter as tk
from ttk import Combobox

class App():
    def __init__(self, master):
        # MASTER FRAME
        frame = tk.Frame(master)
        frame.pack()
        master.title('SMPG Project v1.2.0')

        # GUI ATTRIBUTES
        self.dekad_lst = utils.dek_list()
        self.V1 = tk.IntVar(frame)
        self.V2 = tk.IntVar(frame)
        self.V3 = tk.StringVar(frame)
        self.V4 = tk.StringVar(frame)
        self.V5 = tk.IntVar(frame)
        #self.V6 = tk.IntVar(frame)
        self.V7 = tk.BooleanVar(frame)
        self.V8 = tk.BooleanVar(frame)
        self.V9 = tk.BooleanVar(frame)
        self.V0 = tk.IntVar(frame)
        self.fileOpen = ''
        self.dataset = None

        # LABELS
        self.label0 = tk.Label(frame, text = 'Set up climatological window')
        self.label_analogSettings=tk.Label(frame, text='Analog years settings')
        self.labelz = tk.Label(frame, text='Define a season to monitor')
        self.label1 = tk.Label(frame, text='Initial year:')
        self.label2 = tk.Label(frame, text='Final year:')
        self.label3 = tk.Label(frame, text='From:')
        self.label4 = tk.Label(frame, text='to:')
        self.label5 = tk.Label(frame, text='Select the number of analog years to compute:')
        #self.label6 = tk.Label(frame, text='Specify the rank of analog years to show:')
        self.label7 = tk.Label(frame, text='Analyisis preferences')

        # BUTTONS
        self.HELP = tk.Button(frame, text='About', command=lambda: self.Help(master))                                                                                                                                                                              
        self.BROWSE = tk.Button(frame, text='Browse Files', width=25, command=lambda:self.Browse())
        #self.CLEAR = tk.Button(frame, text='Clear', width=17)
        self.FORECAST = tk.Radiobutton(frame, text='Forecast', variable=self.V7, value=True)
        self.ANALYSIS = tk.Radiobutton(frame, text='Observed data', variable=self.V7, value=False)
        self.SAVE = tk.Checkbutton(frame, text='Save reports', variable=self.V8)
        self.DISPLAY = tk.Checkbutton(frame, text='Display reports', variable=self.V9)
        #self.SCENARIO = tk.Checkbutton(frame, text='Include scenarios', variable=self.V0)
        self.RUN = tk.Button(frame, text='GENERATE REPORTS', command=lambda:self.Run(str(self.init_clim.get()), 
																					 str(self.end_clim.get()),
                                                                                     self.start_dekad.get(),
                                                                                     self.end_dekad.get(),
                                                                                     str(self.analog_menu.get())))     
        # ENTRIES
        self.entry = tk.Entry(frame, width=54, text=self.fileOpen)

        # MENUS
        self.init_clim = Combobox(frame, textvariable=self.V1, values=[None])
        self.end_clim = Combobox(frame, textvariable=self.V2, values=[None])
        self.start_dekad = Combobox(frame, textvariable=self.V3, values=tuple(self.dekad_lst))
        self.end_dekad = Combobox(frame, textvariable=self.V4, values=tuple(self.dekad_lst))
        self.analog_menu  = Combobox(frame, textvariable=self.V5, values=[None] )
        #self.rank_menu  = Combobox(frame, textvariable=self.V6, values=tuple(range(2, 6)))

        # GRIDS
        self.label0.grid(row=1, column=2, columnspan=4)
        self.label_analogSettings.grid(row=5, column=2, columnspan=3)
        self.labelz.grid(row=3, column=2, columnspan=3)
        self.label1.grid(row=2, column=1, padx=10)
        self.label2.grid(row=2, column=3, padx=10)
        self.label3.grid(row=4, column=1, sticky=tk.E, padx=5)
        self.label4.grid(row=4, column=3, sticky=tk.E, padx=5)
        self.label5.grid(row=6, column=1, pady=15, columnspan=3)
        #self.label6.grid(row=7, column=1, columnspan=3)
        self.label7.grid(row=6, column=0)
        self.init_clim.grid(row=2, column=2, pady=15)
        self.end_clim.grid(row=2, column=4)
        self.start_dekad.grid(row=4, column=2, pady=10)
        self.end_dekad.grid(row=4, column=4)
        self.analog_menu.grid(row=6, column=4)
        #self.rank_menu.grid(row=7, column=4)
        self.HELP.grid(row=8, column=4, pady=10, sticky=tk.N)
        self.RUN.grid(row=2, column=0, columnspan=1)
        self.BROWSE.grid(row=0, column=0, pady=20, columnspan=2, sticky=tk.W+tk.E)
        self.entry.grid(row=0, column=2, columnspan=3, padx=0, sticky=tk.E)
        #self.CLEAR.grid(row=9, column=0, pady=15, sticky=tk.W)
        self.FORECAST.grid(row=7, column=0, sticky=tk.NW)
        self.ANALYSIS.grid(row=8, column=0, sticky=tk.NW)
        self.SAVE.grid(row=3, column=0, sticky=tk.W)
        self.DISPLAY.grid(row=4, column=0, sticky=tk.W)
        #self.SCENARIO.grid(row=5, column=0, sticky=tk.W)
    #=====================================================================================================
    def Browse(self):
        file = tk.filedialog.askopenfile(mode='r', filetypes=[('csv files', '*.csv')])
        indir = str(file.name)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, indir)

        if not file is None:
            fst_yr, lst_yr, IDs, raw_data = utils.read(file)
        
        # Updating class attributes 
        yrs = tuple(range(fst_yr, lst_yr))
        yrs_num = tuple(range(1, 1+len(yrs)))
        self.init_clim['values'] = yrs
        self.end_clim['values'] = yrs
        self.analog_menu['values'] = yrs_num
        self.dataset = fst_yr, lst_yr, IDs, raw_data

        # Show success message if everything went ok
        tk.messagebox.showinfo('Loaded', 'Input dataset goes from {} to {}'.format(fst_yr, lst_yr))
    #=====================================================================================================
    def Run(self, fst_cm, lst_cm, fst_dk, lst_dk, analogs_num):

        # Setting up conditions to run & error messages
        if self.dataset == None:
            tk.messagebox.showerror('No dataset loaded', 'You must input a dataset first')
            return

        if fst_cm == '' or lst_cm == '':
            tk.messagebox.showerror('Error', 'There are missing values in your setup')
            return 

        if analogs_num == '':
            tk.messagebox.showerror('Error', 'There are missing values in your setup')
            return 

        # Temporary variables. Looking for the way to remove them 
        fst_yr, lst_yr, IDs, raw_data = self.dataset
        fst_cm = int(fst_cm)
        lst_cm = int(lst_cm)
        analogs_num = int(analogs_num)
        SIZE = len(IDs)

        if lst_cm < fst_cm:
            tk.messagebox.showerror('Error', 'Initial year can\'t be less than {} for this dataset'.format(fst_yr))
            return 

        if lst_cm > lst_yr:
            tk.messagebox.showerror('Error', 'End year cannot be greater than {} for this dataset'.format(lst_yr))
            return 

        if fst_cm >= lst_cm:
            tk.messagebox.showerror('Error', 'End year must be greater than initial year' )
            return 

        if analogs_num  <= 1:
            tk.messagebox.showerror('Error', 'More than one analog year must be chosen')
            return 

        #Checking if reports must be saved 
        Dir = None
        if self.V8.get():
            # Ask user to choose a directory
            dir_name = tk.filedialog.askdirectory() 
            # Change the current file directory
            os.chdir(dir_name) 
            Dir = os.getcwd() 

        # Intantiating class object
        SMPG = smpgTool(fst_yr, lst_yr, fst_cm, lst_cm, fst_dk, lst_dk, SIZE, analogs_num, 
                savefile=self.V8.get(), showfile=self.V9.get(), fct=self.V7.get())

        # Main table and seasonal table
        main_table, status_table = SMPG.general_table(raw_data)
        s_table, cs_table = SMPG.seasonal_table(main_table, status_table)
        average = SMPG.Average(main_table)

        # Computing generic accumulation & ensemble tables
        season_acms, actual_accum, Dict = SMPG.seasonal_accummulations(s_table, cs_table)
        ensemble = SMPG.seasonal_ensemble(s_table, actual_accum)

        #Computing analog years algorithm
        sde = utils.SDE(s_table, cs_table)
        sse = utils.SSE(season_acms, actual_accum)
        ranking, analogs = SMPG.compute_analogs(sde, sse)

        # Compuring seasonal accumulations for analogs and climatology
        aa_table, aa_stats = SMPG.analog_accumulation(analogs, Dict)
        ca_table, ca_stats = SMPG.climatological_accumulation(Dict)
        ae_table, ae_stats, ae_pctl = SMPG.analog_ensemble(analogs, ensemble)
        ce_table, ce_stats, ce_pctl = SMPG.climatological_ensemble(ensemble)

        # Computing outlook params
        ae_otlk = utils.outlook(ae_pctl, ae_table)
        ce_otlk = utils.outlook(ce_pctl, ce_table)

        # Generating reports   
        SMPG.reports(IDs, average, status_table, aa_table, aa_stats, actual_accum, 
        ae_table, ce_stats, ranking, ae_otlk, ce_otlk, Dir=Dir) 
    #=====================================================================================================
    def Help(self, master):
        '''Opens up an 'about' window to show some
        some legal software details.

        :param master:
        '''
        # STRUCTURE
        window = tk.Toplevel(master, width=300, height=400)
        window.title('About SMPG Project')

        # LABELS
        title = tk.Label(window, text='Seasonal Monitoring and Probability \n Generator (SMPG) Project v1.2.0', font=('Arial', 13), justify=tk.CENTER)
        version = tk.Label(window, text = 'Under a MIT license\nCopyright (c) 2020', font = ('Arial', 12), justify=tk.CENTER)

        #img = PhotoImage(file='icon.gif')
        #window.iconphoto(False, img)
        #labelLogo = Label(window, image = img)
        #labelLogo.grid(row = 0, column = 1, pady = 15)

        # BUTTONS
        tutorial_button = tk.Button(window, text='Tutorial/Help', command=lambda: webbrowser.open_new(r'./documentacion.pdf'))
        Update_button = tk.Button(window, text = 'Update Center', command = lambda: tk.messagebox.showinfo('Update Center', 'Coming soon'))

        # GRIDS
        title.grid(row=1, column=1, pady=10, padx=25)
        tutorial_button.grid(row=3, column=1, pady=10)
        Update_button.grid(row = 4, column = 1, pady = 10)   
        version.grid(row=2, column=1, pady=10)




root = tk.Tk()
app = App(root)
root.mainloop()

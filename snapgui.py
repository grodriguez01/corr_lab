'''
Requirements:
    python2.7 casperVirtual enviroment
Description:
    When executed this launches a neat gui that makes all the functions 
    you need for correlator lab easily executable. 
======================================================================
NOTES:
    Unfinished implementations
        - Setting adc gain doesn't actually do anything
          adc gain is set in snap_init.
          One could add a parameter to option parser 
          to pass in adc gain from drop down menu. 
        -Live correlation plot does not have data for c.
         See corr_plotter.py
        -Missing some sort of read out of average correlation 
        for Left polarization and right polarization.

Updated 07/25/2020 
'''
import Tkinter
import ttk
import tkFileDialog
import os 
import subprocess
import time
import threading

class snapapp(Tkinter.Tk):
    def __init__(self, parent=None):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.bitcode = ''
        #self.outfile = "default.pkl" 07/25/2020 Unused?
        #Dividers
        self.frame1 = Tkinter.Frame(parent)
        self.frame1.grid(row=0, column=0, rowspan= 3, columnspan=1, sticky='W')

        self.frame2 = Tkinter.Frame(parent)
        self.frame2.grid(row=4, column=0, rowspan=3, columnspan=1, sticky='W')

        self.frame3 = Tkinter.Frame(parent)
        self.frame3.grid(row=16, column=0, rowspan=3, columnspan=1, sticky='W')

        self.frame4 = Tkinter.Frame(parent)
        self.frame4.grid(row=8, column=0, rowspan=3, columnspan=1, sticky='W')
        self.initialize()

    def initialize(self):
        button = Tkinter.Button(self.frame1,text="Select .FPG", command=self.select_bitcode)
        button.grid(column=0,row=1,sticky="W", pady=10, padx=20)
        self.labelBitcode = Tkinter.StringVar()
        label3 = Tkinter.Label(self.frame1,textvariable=self.labelBitcode,anchor="w",borderwidth=1, relief='sunken')
        label3.config(width=66)
        label3.grid(column=1,row=1,sticky="W")
        label7 = Tkinter.Label(self.frame2,text='ADC GAIN:',anchor="w")
        label7.grid(column=0,row=1,sticky="W",pady=10, padx=20)
        coarse_gain_ch1 = [0,1,2]
        self.dropVal = Tkinter.StringVar()
        self.dropVal.set(0)
        self.dropMenu = Tkinter.OptionMenu(self.frame2, self.dropVal, *coarse_gain_ch1, command=self.getGain)
        self.dropMenu.grid(column=2,row=1,sticky="W",pady=1, padx=1)
        button_setup = Tkinter.Button(self.frame2, text='UPLOAD', command=self.okRun)
        button_setup.grid(column=3, row=1, pady=10, padx=10)
        button_pwr = Tkinter.Button(self.frame2, text='PWR MTR', command=self.launchPower)
        button_pwr.grid(column=4, row=1, pady=10, padx=10)
        button_spec = Tkinter.Button(self.frame2, text='LIVE CORR SPECTRUM', command=self.launchSpectrum)
        button_spec.grid(column=5, row=1, pady=10, padx=10)
        button_data = Tkinter.Button(self.frame2, text='GRAB DATA', command=self.grabData)
        button_data.grid(column=6, row=1, pady=10, padx=10)
        label5 = Tkinter.Label(self.frame3, text="System Report: ", font=("Times New Roman",12),anchor="w")
        label5.grid(column=1, row=4,sticky="W", padx=20)
        self.tx = Tkinter.Text(self.frame3, height=40, width=90)
        self.tx.grid(column=1,row=6, pady=10, padx=40)
        
    def getGain(self, value):
        '''
        Under Contruction?
        I wanted to add a drop down of available gain settings in the mask.
        See casper source code for snap adc.
        '''
        return value 

    def select_bitcode(self):
        '''
        Selects a fpg file. 
        '''
        curr_dir = os.getcwd()
        self.bitcode = tkFileDialog.askopenfilename(parent=self,filetypes=[("Bitcode Files","*.fpg")], initialdir=curr_dir, title='Please select a bitcode')
        self.labelBitcode.set(self.bitcode)

    def boardset(self):
        '''
        Executes snap_init.py and passes fpg file location as parameter.
        *GUI is locked until snap is ready.
        '''
        process = subprocess.Popen(['python', 'snap_init.py','localhost','-b', self.bitcode], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.tx.insert(Tkinter.END, output) 

    def launchPower(self):
        '''
        Launches power meter readout. 
        '''
        self.tx.insert(Tkinter.END, "Launching Power Meter...\n") 
        subprocess.Popen(['python', 'adc_power_meter_v0.1.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def launchSpectrum(self):
        '''
        Launch correlator plot
        *NOTE: I needed to update functionality here.
            -subplot phase
            -different correlation selections appart from bb and ab.
        '''
        #EDITED 07/25/2020 instead of old plot i execute the one with awesome phase subplot below this comment:
            #self.tx.insert(Tkinter.END, "Launching bb ab corr spectrum..\n")
            #subprocess.Popen(['python', 'bb_ab_corr.py', 'localhost'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.tx.insert(Tkinter.END, "Launching corr_plotter..\n")
        subprocess.Popen(['python', 'corr_plotter.py', 'localhost'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def grabData(self):
        '''
        Launches adc interleaved data logger and corr logger which timestamp their saves.

        *Note Updated 07/25/2020: 
            capture_data.py now saves adc data interleaved,
            instead of raw. 

            Added corr_logger,  and corr_logger needs implementation for c correlation registers.
        '''
        self.tx.insert(Tkinter.END, "Launching adc data logger..\n")
        process = subprocess.Popen(['python', 'capture_data.py'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.tx.insert(Tkinter.END, output)

        #\/Added this 07/25/2020: Should execute in parallel to adc data logger? UNTESTED!
        self.tx.insert(Tkinter.END, "Launching correlator data logger..\n")
        process = subprocess.Popen(['python', 'corr_logger.py'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, error = process.communicate()
        self.tx.insert(Tkinter.END, output)
        #print("done")
        #self.tx.insert(Tkinter.END, "Done..\n")
        #you probably want to figure out threading
        #output, error = process.communicate()
        #self.tx.insert(Tkinter.END, output) 

    def okRun(self):
        '''
        Checks if its ok to start the snap init. 
        '''
        if self.bitcode == '':
            self.tx.insert(Tkinter.END, 'Warning, no file selected!\n')
            return 
        self.tx.insert(Tkinter.END, "Running SNAP board configuration script....\n")
        self.update()
        self.boardset()
        
def main():
    gui = snapapp(None)
    gui.title('SNAP BOARD CONTROL PANEL')
    #gui.geometry("700x800")
    gui.mainloop()
if __name__ == "__main__":
    main()

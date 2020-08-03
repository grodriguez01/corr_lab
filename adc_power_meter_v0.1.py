#!/usr/bin/env python
'''
Description:
    Display the power going into the ADC chips on SNAP Board.
======================================================================
Notes:
    This script was confirmed to be accurate in dBm units, with a very small difference 
    to powermeter. 

Updated 07/25/2020
'''
import casperfpga 
import numpy as np 

fpga = casperfpga.CasperFpga('localhost')

try:
    import Tkinter as tk # Python 2.x
except:
    import tkinter as tk # Python 3.x


def get_adc_rms():
    '''
    This function gets sum square from 
    adc_sum_sq0, adc_sum_sq1, adc_sum_sq2
    software registers. 

    Parameters:  
    None 

    Returns:
    inputs: a list of Dictionaries with calculated rms and dBm values. 
     
    '''
    inputs = [{},{},{}]

    for input in range(3):
        regname = 'adc_sum_sq%i'%(input)
        inputs[input]['unpacked'] = fpga.read_uint(regname)

        inputs[input]['rms'] = np.sqrt(inputs[input]['unpacked']/(2**16))/(2**(8-1))

        inputs[input]['dBm'] = round(10*np.log10(((inputs[input]['rms'])**2/50)*1000) +  9,3) #added 9 to calibrate 

    return inputs 
    
def update_pwr():
    #Grab ADC power readings
    inputs = get_adc_rms()
    
    #CONTROL THE FONT SIZE HERE
    labelfont = ('Monaco', 125, 'bold')
    
    label0['text'] = '    ADC  Power (dBm)'
    label0.place(x=100, y=0)
    label0.config(font=('Monaco',50, 'bold'))

    label1['text'] = '    A: ' + str(inputs[0]['dBm'])
    label1.place(x=30,y=100)
    label1.config(font=labelfont)
    
    label2['text'] = '    B: ' + str(inputs[1]['dBm'])
    label2.place(x=30,y=400)
    label2.config(font=labelfont)
    
    
    label3['text'] = '    C: ' +  str(inputs[2]['dBm'])
    label3.place(x=30,y=650)
    label3.config(font=labelfont)
    
    root.after(1000, update_pwr)
    

#==========main============
root = tk.Tk()
root.title('ADC_POWER_METER v1.0')
root.geometry('1280x800')
root.configure(background='white')


#creating objects 
label0 = tk.Label(root)
label0.pack()
label1 = tk.Label(root)
label1.pack()
label2 = tk.Label(root)
label2.pack()
label3 = tk.Label(root)
label3.pack()

#start_it 
update_pwr()

root.mainloop()

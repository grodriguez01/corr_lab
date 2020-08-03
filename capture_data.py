"""
Description:
    When executed this script at run time saves ADC data interleaved.
======================================================================
Notes:
    Instead of raw adc dictionary now its interleaved and then saved. 
    This version of script has not been tested.

Updated 07/25/2020
"""
import casperfpga
import pickle
import time 

fpga = casperfpga.CasperFpga('localhost')
fpga.get_system_information() #<- for some reason snapshot blocks dont show up unless this is called

def get_adc_snapshot():
    '''
    This is returning a dct of all
    adc chips ex. adc0:0
    '''
    print('Grabbing Raw Adc Data..')
    fpga.snapshots.adc_snapshot_ss.arm()
    fpga.registers.adc_ss_trigger.write(reg='pulse')
    ss_dct = fpga.snapshots.adc_snapshot_ss.read(arm=False)['data']
    return ss_dct 

'''
ADDED interleave_data on 7/25/2020 *NOT TESTED* I CROSS MY FINGERS THAT IT WORKS ;)
Should work though tested in jupyter notebook. So hopefully disregard this comment?
Maybe i break this script where i use this function?
'''
def interleave_data(data):
    '''
    Interleave cores
    Parameter: data, raw snapshot dct. 
    Returns: inter_data, interleaved core dct. 
    '''
    inter_data = {'adc0':[], 'adc1':[], 'adc2':[]}
    for core in sorted(inter_data.keys()):
        for i in range(0,16384):
            inter_data[core].append(data[core+':0'][i])
            inter_data[core].append(data[core+':1'][i])
            inter_data[core].append(data[core+':2'][i])
            inter_data[core].append(data[core+':3'][i])
    return inter_data

def save_data(data_obj):
    curr_time = time.localtime()
    timestamp = time.strftime("%m-%d-%y_%H-%M",curr_time) #<-- Eddited here 07/25/2020 I'm going to change the colon in between Hr and Min to something else
    filename = 'output/adc_dct' + timestamp + '.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(data_obj, f, pickle.HIGHEST_PROTOCOL)
    return filename

def main():
    print("Data Grabber Launched.")
    #ss_dct = get_adc_snapshot()    <--Eddited here 07/25/2020 I'm going to interleave raw dictionary now
    raw_dct = get_adc_snapshot()
    ss_dct = interleave_data(raw_dct) #END OF POTENTIAL DISASTER I THINK
    filename = save_data(ss_dct)
    print('DATA SAVED: ' + filename)
main()
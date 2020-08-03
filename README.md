# corr_lab
    Correlator lab tools
        Requirements: python 2.7, casperfpga, Tkinter.

    Uses:
         - Interface to select fpg file and run snap init script. 
         - Run power meter gui, correlation plots, and timestamp data. 

    Info: 
        To start gui interface for tools activate casperVirtualenviroment.
            In home directory of labpi run:
                source casperVirtualenv/bin/activate
                
        Then one can run snapgui using python2.7.
                python snapgui.py 

        Output Data is stored in output folder. 
        *NOTE snapgui runs scripts in the same directory*
        
        
                        FILES 
        Name                                Purpose 
        snap_init.py                        Uploads fpg file and initalizes adcs
        snap_cross_plot.py                  Plots correlation and phase. #Need to implement to gui. 
        adc_power_meter_v0.1.py             Display power levels of adc cores. 
        bb_ab_corr.py                       Plots correlation of bb and ab. 
        corr_plotter.py                     Plots correlation of bb and ab and phase.
        capture_data.py                     Saves data of adc chips #need to interleave them before saving.
        corr_logger.py                      Saves raw corr data of fpga registers. #Need to implement to gui.  
        mod_v5_tut_corr_2019-12-03_1550.fpg bitcode for SNAP, ADC snapshot stores adc data in -1/1 
        mod_v5_tut_corr_2019-12-17_1740.fpg bitcode for SNAP, ADC snapshot stores adc data in -127/128 
        





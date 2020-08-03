"""
Description:
    When executed this launches a plot showing correlation and phase.
======================================================================
NOTES: 

    This only shows correlations and phase for a and b.
    It's missing implementations for c.

Updated 07/25/2020
"""
import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib.widgets import Button
import casperfpga, time, struct,sys, logging
#***code from casper with a few motifications. 
katcp_port=7147
freq_range_mhz = np.linspace(0., 400., 1024)

def set_coeff(coeff,nch):
    '''
    Casper code that sets quant registers.
    '''
    quants_coeffs = [coeff] * nch * 2
    quants_coeffs = struct.pack('>{0}H'.format(nch*2),*quants_coeffs)
    for i in range(3):
        fpga.blindwrite('quant{0}_coeffs'.format(i), quants_coeffs)


def get_data():
    '''
    Get raw correlations from correlator registers
    *Note MISSING FUNCTIONALITY:
        -Needs some implementations to read from C correlation
        registers.
    '''
    acc_n = fpga.read_uint('acc_num')
    aa_real_0 = struct.unpack('>512l',fpga.read('dir_x0_aa_real',512*4,0))
    aa_real_1 = struct.unpack('>512l',fpga.read('dir_x1_aa_real',512*4,0))

    bb_real_0 = struct.unpack('>512l',fpga.read('dir_x0_bb_real',512*4,0))
    bb_real_1 = struct.unpack('>512l',fpga.read('dir_x1_bb_real',512*4,0))

    ab_real_0 = struct.unpack('>512l',fpga.read('dir_x0_ab_real',512*4,0))
    ab_real_1 = struct.unpack('>512l',fpga.read('dir_x1_ab_real',512*4,0))

    ab_imag_0 = struct.unpack('>512l',fpga.read('dir_x0_ab_imag',512*4,0))
    ab_imag_1 = struct.unpack('>512l',fpga.read('dir_x1_ab_imag',512*4,0))

    aa_real_inter = [] 
    bb_real_inter = [] 
    ab_real_inter = [] 
    ab_imag_inter = [] 


    ab_inter = []

    for i in range(512):
        aa_real_inter.append(aa_real_0[i])
        aa_real_inter.append(aa_real_1[i]) 

        bb_real_inter.append(bb_real_0[i])
        bb_real_inter.append(bb_real_1[i]) 

        ab_inter.append(complex(ab_real_0[i], ab_imag_0[i]))
        ab_inter.append(complex(ab_real_1[i], ab_imag_1[i]))

        ab_real_inter.append(ab_real_0[i]) 
        ab_real_inter.append(ab_real_1[i])

        ab_imag_inter.append(ab_imag_0[i]) 
        ab_imag_inter.append(ab_imag_1[i])

    return acc_n, aa_real_inter, bb_real_inter, ab_inter, ab_real_inter, ab_imag_inter

def stream_data():
    '''
    Live plot, shows correlation data and phase.
    '''
    plt.clf()
    #ab corr
    acc_n, aa_real_inter, bb_real_inter, ab_inter, ab_real_inter, ab_imag_inter = get_data()
    plt.subplot(211)
    plt.grid()
    plt.plot(freq_range_mhz, 10*np.log10(np.abs(ab_inter)), label='ab')
    plt.plot(freq_range_mhz, 10*np.log10(aa_real_inter), label='aa')
    plt.plot(freq_range_mhz, 10*np.log10(bb_real_inter), label='bb')
    plt.title('Integration number %i '%(acc_n))
    plt.ylabel("Power (dB)")
    plt.xlim(0,400)
    plt.legend()
    plt.subplot(212)
    plt.grid()
    plt.xlabel("Frequency MHz")
    plt.xlim(0,400)
    plt.ylabel("Phase")
    plt.plot(freq_range_mhz, (np.angle(ab_inter)))
    plt.draw()
    fig.canvas.manager.window.after(100, stream_data)

#Eddited 07/25/2020
#I Don't know why i had this but, wont delete cuz maybe something spooky happens?
#def clicked():
#   print('hello')

#main
if __name__ == '__main__':
    from optparse import OptionParser


    p = OptionParser()
    p.set_usage('spectrometer.py <ROACH_HOSTNAME_or_IP> [options]')
    p.set_description(__doc__)
    p.add_option('-n', '--nchannel', dest='nch',type=int, default=1024,
		help='The number of frequency channel. Default is 1024.')
    p.add_option('-c', '--coeff', dest='coeff', type=int, default=1000,
		help='Set the coefficients in quantisation (4bit quantisation scalar).')
    p.add_option('-l', '--acc_len', dest='acc_len', type='int',default=2*(2**28)/2048,
        help='Set the number of vectors to accumulate between dumps. default is 2*(2^28)/2048, or just under 2 seconds.')
    p.add_option('-b', '--baseline', dest='baseline', type='str',default='ab', help='Plot this cross correlation mag and phase. Default=ab')
    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
        print 'Please specify a SNAP board. Run with the -h flag to see all options.\nExiting.'
        exit()
    else:
        snap = args[0] 
    baseline=opts.baseline

try:

    print('Connecting to server %s on port %i... '%(snap,katcp_port)),
    fpga = casperfpga.CasperFpga(snap)
    time.sleep(0.2)

    if fpga.is_connected():
        print 'ok\n'
    else:
        print 'ERROR connecting to server %s on port %i.\n'%(snap,katcp_port)
        exit_fail()


    print 'Configuring accumulation period...',
    sys.stdout.flush()
    if opts.acc_len:
        fpga.write_int('acc_len',opts.acc_len)
    print 'done'

    fpga.write_int('ctrl',0) 
    fpga.write_int('ctrl',1<<16) #clip reset
    fpga.write_int('ctrl',0) 
    fpga.write_int('ctrl',1<<17) #arm
    fpga.write_int('ctrl',0) 
    fpga.write_int('ctrl',1<<18) #software trigger
    fpga.write_int('ctrl',0) 
    fpga.write_int('ctrl',1<<18) #issue a second trigger
    fpga.write_int('ctrl',0) 
    time.sleep(0.1)

    if opts.coeff:
        print 'Configuring quantisation coefficients with parameter {0}...'.format(opts.coeff),
        sys.stdout.flush()
        set_coeff(opts.coeff,opts.nch)
        print 'done'

   #set up the figure with a subplot to be plotted
    fig = plt.figure()
    fig.add_subplot(2,1,1)

    # start the process
    fig.canvas.manager.window.after(100, stream_data)
    plt.show()
    #file_name = raw_input('filename: ') 
    print 'Plot started.'


except KeyboardInterrupt:
    exit()

exit()
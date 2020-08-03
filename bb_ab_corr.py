#!/usr/bin/env python
'''
This code demonstrates readount of a SNAP spectrometer. You need a SNAP with:
-- A 10 MHz, 8dBm or 1.59 Vp-p  reference going into the SYNTH_OSC SMA (3rd SMA from the left)

'''
import matplotlib
import pylab
import numpy 
import casperfpga,casperfpga.snapadc,time,struct,sys,logging
katcp_port=7147
save = False 

freq_range_mhz = numpy.linspace(0., 400., 1024)
#if save:file_name = raw_input('file: ')
#opening files 
cross_real_file = open('cross_real_raw.txt', 'ab')
cross_imag_file = open('cross_imag_raw.txt', 'ab')
cross_power_file = open('cross_power_raw.txt', 'ab')
auto_real_file  = open('auto_real_raw.txt', 'ab')

def set_coeff(coeff,nch):
    quants_coeffs = [coeff] * nch * 2
    quants_coeffs = struct.pack('>{0}H'.format(nch*2),*quants_coeffs)
    for i in range(3):
        fpga.blindwrite('quant{0}_coeffs'.format(i), quants_coeffs)

def get_data():
    acc_n = fpga.read_uint('acc_num')
    bb_real_0 = struct.unpack('>512l',fpga.read('dir_x0_bb_real',512*4,0))
    bb_real_1 = struct.unpack('>512l',fpga.read('dir_x1_bb_real',512*4,0))

    ab_real_0 = struct.unpack('>512l',fpga.read('dir_x0_ab_real',512*4,0))
    ab_real_1 = struct.unpack('>512l',fpga.read('dir_x1_ab_real',512*4,0))

    ab_imag_0 = struct.unpack('>512l',fpga.read('dir_x0_ab_imag',512*4,0))
    ab_imag_1 = struct.unpack('>512l',fpga.read('dir_x1_ab_imag',512*4,0))

 
    bb_real_inter = [] #a
    ab_real_inter = [] #b
    ab_imag_inter = [] #c

    for i in range(512):
        bb_real_inter.append(bb_real_0[i])
        bb_real_inter.append(bb_real_1[i]) #a 

        ab_real_inter.append(ab_real_0[i]) #b 
        ab_real_inter.append(ab_real_1[i])

        ab_imag_inter.append(ab_imag_0[i]) #c 
        ab_imag_inter.append(ab_imag_1[i])

    bb_real_inter = numpy.array(bb_real_inter, dtype=numpy.float)
    ab_real_inter = numpy.array(ab_real_inter, dtype=numpy.float)
    ab_imag_inter = numpy.array(ab_imag_inter, dtype=numpy.float)
    
    numpy.savetxt(auto_real_file, bb_real_inter)
    numpy.savetxt(cross_real_file, ab_real_inter)
    numpy.savetxt(cross_imag_file, ab_imag_inter)
    ab_real_inter = numpy.sqrt(numpy.power(ab_real_inter, 2) + numpy.power(ab_imag_inter,2))
    numpy.savetxt(cross_power_file, ab_real_inter)

 
    return acc_n, bb_real_inter, ab_real_inter, ab_imag_inter


def plot_spectrum():
    matplotlib.pyplot.clf()
    acc_n, bb_real_inter, ab_real_inter, ab_imag_inter = get_data()

    bb_real_inter = 10*numpy.ma.log10(bb_real_inter)
    bb_real_inter = bb_real_inter.filled(0)
    ab_real_inter = 10*numpy.ma.log10(ab_real_inter)
    ab_real_inter = ab_real_inter.filled(0)
    ab_imag_inter = 10*numpy.ma.log10(ab_imag_inter)
    ab_imag_inter = ab_imag_inter.filled(0)

    
    matplotlib.pylab.plot(freq_range_mhz, bb_real_inter, label='bb_auto')
    matplotlib.pylab.plot(freq_range_mhz, ab_real_inter,'r', label='ab_cross')
    #matplotlib.pylab.plot(freq_range_mhz, ab_imag_inter,'g')

    if acc_n > 30 and save:    
        print('Saving spectrum @' + str(acc_n)) 
        numpy.save(file_name + '_bb_auto_accn' + str(acc_n),bb_real_inter)
        numpy.save(file_name + '_ab_cross_accn' + str(acc_n), ab_real_inter)
    #   return 

    matplotlib.pylab.legend()
    matplotlib.pylab.title('Integration number %i.'%acc_n)
    matplotlib.pylab.ylabel('Power (dB)')
    matplotlib.pylab.xlabel('Freq (MHz)')
    matplotlib.pylab.xlim(freq_range_mhz[0], freq_range_mhz[-1])
    matplotlib.pylab.grid() 
    fig.canvas.draw()
    fig.canvas.manager.window.after(100, plot_spectrum)
 

#START OF MAIN:
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
    opts, args = p.parse_args(sys.argv[1:])

    if opts==[]:
        print 'Please specify a SNAP board. Run with the -h flag to see all options.\nExiting.'
        exit()
    else:
        snap = args[0] 

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

    print(opts.nch);

    if opts.coeff:
        print 'Configuring quantisation coefficients with parameter {0}...'.format(opts.coeff),
        sys.stdout.flush()
        set_coeff(opts.coeff,opts.nch)
        print 'done'

    save_data = False 
    #set up the figure with a subplot to be plotted
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(1,1,1)

    # start the process
    fig.canvas.manager.window.after(100, plot_spectrum)
    matplotlib.pyplot.show()



except KeyboardInterrupt:
    exit()

exit()


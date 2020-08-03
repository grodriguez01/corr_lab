"""
Description:
    When executed this saves correlation data stream from correlation 
    registers.
======================================================================
NOTES: 
    This only saves correlations for a and b.
    It's missing implementations for c.

Updated 07/25/2020
"""
import numpy as np 
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
    Read correlation registers and interleave them. 

    Returns:
        accumulation number, and respective correlation list interleaved.
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

def save_data():
    '''
    Saves lists to disk.
    '''
    acc_n, aa_real_inter, bb_real_inter, ab_inter, ab_real_inter, ab_imag_inter = get_data()
    np.savetxt(aa_real_file, np.array(aa_real_inter))
    np.savetxt(bb_real_file, np.array(bb_real_inter))
    np.savetxt(ab_inter_file, np.array(ab_inter)) 
    np.savetxt(ab_real_file, np.array(ab_real_inter))
    np.savetxt(ab_imag_file, np.array(ab_imag_inter))
    
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
    print("Saving data...")
    curr_time = time.localtime()
    timestamp = time.strftime("%m-%d-%y_%H-%M",curr_time) #<added - between hour and min 07/25/2020 
    aa_real_file = open("output/aa_real_" + timestamp + ".txt","ab")
    bb_real_file = open("output/bb_real_" + timestamp + ".txt","ab")
    ab_inter_file = open("output/ab_inter_" + timestamp + ".txt","ab")
    ab_real_file = open("output/ab_real_" + timestamp + ".txt","ab")
    ab_imag_file = open("output/ab_imag_" + timestamp + ".txt","ab")
    ab_imag_file = open("output/ab_imag_" + timestamp + ".txt","ab")
    acc_n = fpga.read_uint('acc_num')

    '''
    07/25/2020
    Was going to use acc_num but 
    didn't work out so did a for.., i mean 
    while loop. 
    '''
    cnt = 0
    while True:
        #acc_n = fpga.read_uint('acc_num')
        print(str(cnt)) #Waring! if script is executed right after a cancled data capture it has a disastrous potential to overwrite data. 
        if cnt <= 50:  #if you want more data increase counter. 
            save_data()
        else:
            break
        cnt += 1 
    print("Data saved to output...")

except KeyboardInterrupt:
    exit()

exit()
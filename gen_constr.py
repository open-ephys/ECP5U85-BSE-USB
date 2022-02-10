"""
Very simple and hacky script to create a LPF file for Lattice FPGAs from a KiCAD netlist
Netlist needs to be exported in OrCADPCB2 format and the reailing asterisk manually removed 

Probably should make filenames and part number a proper argument, but I am lazy right now
"""
import sexpdata
import re

filename = "pcb/ecp5u85-bse-usb.net" #input file
outputfile = "balls.lpf" #output file
partname = "U1" #part number in schematic

#nets that do not need to be in the LPF file (e.g.: power)
nonets = ('GND', '(?:\+|-)\d+V\d*', '[\+-]\d+\.\d+V', '.*VCC.*', '.*VREF.*', '.*VDD.*', '/DONE', '/\~\{INIT\}', 'FCLK', '.+-')

#options for nets. Each tuple contains: nets that should match, io type, (optional) different extra parameters
opts = (
    (('A\[\d+\]','DQ\[\d+\]','BA\[\d+\]','[LU]DM', 'ODT', 'RASn','CASn','MEM_RESETn','CSn','WEn','CK_p','CKE'),'SSTL15_I','SLEWRATE=FAST'), #RAM
    (('[LU]DQS_p'),'SSTL15_I','SLEWRATE=FAST','DIFFRESISTOR=100'), #RAM DQS
    (('DATA\[\d+\]','BE\[\d\]', 'WRn', 'FTCLK', 'S1\[\d\]'),'LVCMOS33'), #FTDI inouts, outs and clock
    (('RXFn','TXEn', 'GPIO\[0\]'),'LVCMOS33','CLAMP=OFF'), #FTDI inputs
    (('S0\[\d\]', 'WAKEUPn'),'LVCMOS33','CLAMP=OFF','OPENDRAIN=ON'),
    (('D[236]IO_p\[\d\]'),'LVDS'),
    (('D[236]I_p\[\d\]', 'CLK100_p'),'LVDS','DIFFRESISTOR=100'),
    (('S8\[\d\]', 'LED\[\d\]', 'FT_RSTreqn'),'LVCMOS25'),
    (('S8\[\d\]','FD\[\d\]','FMISO','FMOSI','FCSn','FPGA_RESETrqn'),'LVCMOS33')
    
    )

def sanitize(port):
    ball = port[0].tosexp();
    
    #general cleans
    net = re.findall('/*(?:.+/)*(.+)',port[1].tosexp())[0]
    
    if val := re.match('\~\{(.+)\}',net):
        net = val[1] + 'n'
    elif val := re.match('(.+)\+',net):
        net = val[1] + '_p'
    
    #port-specific
    if val := re.match('(D\dIO?)(\d+)(.*)',net):
        net = '{pre}{sub}[{idx}]'.format(pre = val[1],sub = val[3],idx = val[2])
    elif val := re.match('(S\d)(\d+)',net):
        net = '{pre}[{idx}]'.format(pre = val[1], idx = val[2])
    elif val := re.match('(\D+)(\d+)',net):
        net = '{pre}[{idx}]'.format(pre = val[1], idx = val[2])
        
    return(net, ball)
    

def main():
    file = open(filename,"r")
    data = file.read()
    file.close()
    sdata = sexpdata.loads(data)

    for part in sdata:
        if not(type(part) is list):
            continue
        if part[2].tosexp() == partname:
            break
            
    antimatches = '(?:{0})'.format('|'.join(nonets))
    nets = [ sanitize(x) for x in part if (type(x) is list and len(x) == 2 and not re.fullmatch(antimatches,x[1].tosexp(),flags=re.IGNORECASE)) ]
    
    file = open(outputfile,"w")
    for ball in nets:
        file.write('LOCATE COMP "{net}" SITE "{site}" ;\n'.format(net=ball[0], site=ball[1]))
        for opt in opts:
            if type(opt[0]) is tuple:
                matchstring = '(?:{0})'.format('|'.join(opt[0]))
            else:
                matchstring = opt[0]
            if re.fullmatch(matchstring,ball[0],flags=re.IGNORECASE):
                file.write('IOBUF PORT "{net}" IO_TYPE={io} '.format(net=ball[0], io=opt[1]))
                for extra in opt[2:]:
                    file.write(extra+' ')
                file.write(';\n');
                break;
        
    file.close()
    

if __name__ == "__main__":
    main()
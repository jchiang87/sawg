infile = 'segmentation.txt'

outfile = 'segmentation.txt_new'
output = open(outfile, 'w')
for line in open(infile):
    if line.startswith('#'):
        output.write(line)
        continue

    tokens = line.split()
    if len(tokens) < 19:
        output.write(line)
        continue

    tokens[8] = '0'     # gain percent variation
    tokens[10] = '0'    # bias level percent variation
    tokens[12] = '0'    # read noise percent variation
    tokens[14] = '0'    # dark current percent variation
    tokens[15] = '3'    # serial prescan for ITL sensors
#    tokens[15] = '10'    # serial prescan for e2v sensors
    tokens[16] = '0'    # parallel prescan
    tokens[17] = '22'   # parallel overscan
    tokens[18] = '20'   # serial overscan

    my_line = '  '.join(tokens)
    output.write(my_line + '\n')
output.close()

import pyfits

def convert_to_DM_fits(infile, hdu, outfile):
    keywords = ('PCOUNT GCOUNT DETSIZE DATASEC'.split() +
                'DETSEC DTV1 DTV2 DTM1_1 DTM2_2'.split())
    input = pyfits.open(infile)
    output = pyfits.HDUList()
    output.append(pyfits.PrimaryHDU())

    output[0].data = input[hdu].data
    for keyword in keywords:
        output[0].header[keyword] = input[hdu].header[keyword]

    output.writeto(outfile, clobber=True)

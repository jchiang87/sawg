import os
import glob
import pyfits
from AmplifierGeometry import AmplifierGeometry, amp_loc

channels = '10 11 12 13 14 15 16 17 07 06 05 04 03 02 01 00'.split()

prototype = glob.glob('lsst_a*.fits.gz')[0]
prefix = prototype.split('_C')[0]
suffix = prototype.split('_C')[1][2:]

foo = pyfits.open(prototype)
naxis1 = foo[0].header['NAXIS1']
naxis2 = foo[0].header['NAXIS2']
amp_geom = AmplifierGeometry(prescan=3, nx=509, ny=2000,
                             detxsize=8*naxis1, detysize=2*naxis2,
                             amp_loc=amp_loc['ITL'])

output = pyfits.HDUList()
output.append(pyfits.PrimaryHDU())
for amp, channel in zip(range(1, 17), channels):
    infile = "%s_C%s%s" % (prefix, channel, suffix)
    print amp, infile
    hdu = pyfits.open(infile, do_not_scale_image_data=True)[0]
    hdu.header['DATASEC'] = amp_geom[amp]['DATASEC']
    hdu.header['DETSEC'] = amp_geom[amp]['DETSEC']
    hdu.name = 'Segment%s' % channel
    output.append(hdu)

outfile = prefix + '_MEF' + suffix
outfile = os.path.basename(outfile.rstrip('.gz'))
output.writeto(outfile, clobber=True)

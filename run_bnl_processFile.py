import sys
import subprocess
import glob
from convert_to_DM_fits import convert_to_DM_fits

get_ext = lambda filename, hdu : (filename.split('_')[2].split('.')[0] 
                                  + ('_%02i' % hdu))

files = sorted(glob.glob('../120.00sec*'))

dmfile = files[-1]
hdu = 12
ext = get_ext(dmfile, hdu)

imfile = 'image_%(ext)s.fits' % locals()

convert_to_DM_fits(dmfile, hdu, imfile)

command = """processFile.py %(imfile)s \
--outputCatalog catalog_%(ext)s.fits \
--verbose --loglevel FATAL \
--config variance=-1 --configfile bnl_config.py""" % locals()
print command

subprocess.call(command, shell=True)


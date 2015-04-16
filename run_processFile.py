import sys
import subprocess

try:
    suffix = "%03i" % int(sys.argv[1])
except:
    print "usage: python run_processFile.py <resampling factor>"
    sys.exit()

command = """processFile.py star_grid_unwarped_oversamp_%(suffix)s.fits \
    --outputCatalog cat_unwarped_oversamp_%(suffix)s.fits \
    --verbose --config variance=-1 edgeRolloff.applyModel=False""" % locals()
print "****************************"
print "* Processing unwarped data *"
print "****************************"
subprocess.call(command, shell=True)

command = """processFile.py star_grid_warped_oversamp_%(suffix)s.fits \
    --outputCatalog cat_warp_oversamp_%(suffix)s.fits \
    --verbose --config variance=-1 edgeRolloff.applyModel=False""" % locals()
print "******************************************************"
print "* Processing warped data, without edge rolloff model *"
print "******************************************************"
subprocess.call(command, shell=True)

command = """processFile.py star_grid_warped_oversamp_%(suffix)s.fits \
    --outputCatalog cat_warp_modeled_oversamp_%(suffix)s.fits \
    --verbose --config variance=-1 --configfile config/edgerolloff_config.py""" % locals()
print "***************************************************"
print "* Processing warped data, with edge rolloff model *"
print "***************************************************"
subprocess.call(command, shell=True)

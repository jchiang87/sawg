import sys
import subprocess

try:
    suffix = "%03i" % int(sys.argv[1])
except:
    print "usage: python run_processFile.py <resampling factor>[=10]"
    print "using resampling factor = 10"
    suffix = "010"

command = """processFile.py star_grid_unwarped_oversamp_%(suffix)s.fits \
    --outputCatalog cat_unwarped_oversamp_%(suffix)s.fits \
    --verbose --loglevel FATAL \
    --config variance=-1 edgeRolloff.applyModel=False""" % locals()
print "****************************"
print "* Processing unwarped data *"
print "****************************"
subprocess.call(command, shell=True)

command = """processFile.py star_grid_warped_oversamp_%(suffix)s.fits \
    --outputCatalog cat_warp_oversamp_%(suffix)s.fits \
    --verbose --loglevel FATAL \
    --config variance=-1 edgeRolloff.applyModel=False""" % locals()
print "******************************************************"
print "* Processing warped data, without edge rolloff model *"
print "******************************************************"
subprocess.call(command, shell=True)

command = """processFile.py star_grid_warped_oversamp_%(suffix)s.fits \
    --outputCatalog cat_warp_modeled_oversamp_%(suffix)s.fits \
    --verbose  --loglevel FATAL --config variance=-1 \
    --configfile config/sensor_distortion_config.py""" % locals()
print "***************************************************"
print "* Processing warped data, with edge rolloff model *"
print "***************************************************"
subprocess.call(command, shell=True)

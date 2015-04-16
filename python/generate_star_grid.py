import sys
import numpy as np
import galsim
from lsst.obs.lsstSim import EdgeRolloffConfig
from EdgeRolloffWarper import EdgeRolloffWarper
from SensorSimConfig import SensorSimConfig, TanWcsConfig

def rebin(image, resamp_factor):
    '''
    Rebin a galsim.Image into a smaller galsim.Image of the same rank
    whose dimensions are resamp_factor smaller than the original
    dimensions.  resamp_factor must be a divisor of the number of
    pixels in each dimension.
    >>> a=rand(6, 4); b=rebin(a, 2)
    >>> a=rand(6); b=rebin(a, 2)
    '''
    if resamp_factor == 1:
        return image
    a = image.array
    shape = a.shape
    for x in shape:
        if x % resamp_factor != 0:
            raise RuntimeError("resamp_factor must be a common factor  "
                               + "of all image dimensions.")
    args = tuple(x/resamp_factor for x in a.shape)
    lenShape = len(shape)
    factor = np.asarray(shape)/np.asarray(args)
    evList = ['a.reshape('] + \
             ['args[%d],factor[%d],'%(i,i) for i in range(lenShape)] + \
             [')'] + ['.sum(%d)'%(i+1) for i in range(lenShape)]
    #print ''.join(evList)
    rebinned_array = eval(''.join(evList))
    rebinned_image = galsim.ImageF(args[1], args[0],
                                   scale=image.scale*resamp_factor)
    rebinned_image.array[:] = rebinned_array
    return rebinned_image

random_seed = 147918741

#
# Read in the default configs
#
simConfig = SensorSimConfig()
edgeRolloffConfig = EdgeRolloffConfig()
tanWcsConfig = TanWcsConfig()
#
simConfig.star_coords_file = 'star_grid_coords_%03i.txt' % simConfig.oversampling
#
# Increase the scale of the edge rolloff by a factor of 10 to make the
# effects more obvious.
#
edgeRolloffConfig.xscale *= 10
edgeRolloffConfig.yscale *= 10

#
# Object to perform transformation from nominal pixel to actual pixel.
#
warper = EdgeRolloffWarper(edgeRolloffConfig,
                           oversampling=simConfig.oversampling)

star_coords = open(simConfig.star_coords_file, 'w')

#
# Create the (oversampled) image.
#
pixel_scale = simConfig.pixel_scale/float(simConfig.oversampling)
psf_image = galsim.ImageF(simConfig.nxpix*simConfig.oversampling,
                          simConfig.nypix*simConfig.oversampling,
                          scale=pixel_scale)

#
# Create an array of stars, using a Moffat profile PSF.
#
print "Creating an array of stars"
psf = galsim.Moffat(beta=simConfig.psf_beta, fwhm=simConfig.psf_fwhm,
                    trunc=simConfig.psf_trunc, flux=simConfig.psf_flux)

def offset(x, y, x0=simConfig.x0, y0=simConfig.y0):
    return x - x0, y - y0

for ix in range(simConfig.nxstars+1):
    if ix % ((simConfig.nxstars+1)/4) == 0:
        sys.stdout.write('!')
        sys.stdout.flush()
    else:
        sys.stdout.write('.')
        sys.stdout.flush()
    for iy in range(simConfig.nystars+1):
        xpos = ix*simConfig.star_grid_dx - simConfig.star_grid_dx/2.
        ypos = iy*simConfig.star_grid_dy - simConfig.star_grid_dy/2.
        psf.drawImage(psf_image, offset=offset(xpos, ypos), add_to_image=True)
        #
        # Write nominal and actual star locations in pixel coordinates
        #
        xposw, yposw = warper.nominal_to_actual_pixel(xpos, ypos)
        star_coords.write('%.4f  %.4f  %.4f  %.4f\n' 
                          % (xpos/simConfig.oversampling,
                             ypos/simConfig.oversampling,
                             xposw/simConfig.oversampling,
                             yposw/simConfig.oversampling))
star_coords.close()
print "Done"
#
# Add sky noise.
#
ud = galsim.UniformDeviate(random_seed)
sky_level_pixel = simConfig.sky_level*pixel_scale**2
noise = galsim.PoissonNoise(ud, sky_level=sky_level_pixel)
psf_image.addNoiseSNR(noise, simConfig.signal_to_noise)

#
# Warp the image using the edge rolloff transform.  This involves a 
# pixel-by-pixel mapping
#
print "Warping image"
warped_image = warper.run(psf_image)

#
# Rebin at the actual sensor resolution.
#
psf_image = rebin(psf_image, simConfig.oversampling)
warped_image = rebin(warped_image, simConfig.oversampling)

#
# Add sky projection TanWCS.
#
affine = galsim.AffineTransform(tanWcsConfig.dudx, tanWcsConfig.dudy, 
                                tanWcsConfig.dvdx, tanWcsConfig.dvdy,
                                origin=psf_image.trueCenter())
sky_center = galsim.CelestialCoord(ra=tanWcsConfig.ra_center*galsim.hours,
                                   dec=tanWcsConfig.dec_center*galsim.degrees)
wcs = galsim.TanWCS(affine, sky_center, units=galsim.arcsec)

psf_image.wcs = wcs
warped_image.wcs = wcs

psf_image.write('star_grid_unwarped_oversamp_%03i.fits' % simConfig.oversampling)
warped_image.write('star_grid_warped_oversamp_%03i.fits' % simConfig.oversampling)

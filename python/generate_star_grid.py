import sys
import numpy as np
import galsim
from EdgeRolloffWarper import EdgeRolloffWarper

def getTanWCS(image, ra=10, dec=0):
    dudx = 1
    dudy = 0
    dvdx = 0
    dvdy = 1
    affine = galsim.AffineTransform(dudx, dudy, dvdx, dvdy,
                                    origin=image.trueCenter())
    sky_center = galsim.CelestialCoord(ra=ra*galsim.hours,
                                       dec=dec*galsim.degrees)
    wcs = galsim.TanWCS(affine, sky_center, units=galsim.arcsec)
    return wcs

random_seed = 147918741

nxpix = 80       # image size
nypix = 80

nx = 4           # number of star columns
ny = 4           # number of star rows
dx = nxpix/nx    # grid spacing
dy = nypix/ny

# Warping parameters in pixels
warp_amp = 2       # Amplitude of astrometric shift.
warp_scale = 30    # Exponential scale of shift.  This is about a 
                   # factor of 10 larger than measured
warp_width = 4000  # Sensor width

pixel_scale = 0.2    # arcsec / pixel
sky_level = 1e6      # ADU / arcsec^2

signal_to_noise = 100000   # bright stars

psf_flux = 1
psf_beta = 3
psf_fwhm = 0.5    # arcsec
psf_trunc = 2.*psf_fwhm
psf_image = galsim.ImageF(nxpix, nypix, scale=pixel_scale)

def offset(x, y, x0=nxpix/2., y0=nypix/2.):
    return x - x0, y - y0

#
# Create an array of stars, using a Moffat profile psf.
#
print "Creating array of stars"
psf = galsim.Moffat(beta=psf_beta, fwhm=psf_fwhm, trunc=psf_trunc,
                    flux=psf_flux)
for ix in range(nx+1):
    if ix % ((nx+1)/4) == 0:
        sys.stdout.write('!')
        sys.stdout.flush()
    else:
        sys.stdout.write('.')
        sys.stdout.flush()
    for iy in range(ny+1):
        xpos = ix*dx - dx/2.
        ypos = iy*dy - dy/2.
        psf.drawImage(psf_image, offset=offset(xpos, ypos), add_to_image=True)
print "Done"
#
# Add sky noise.
#
ud = galsim.UniformDeviate(random_seed)
sky_level_pixel = sky_level*pixel_scale**2
noise = galsim.PoissonNoise(ud, sky_level=sky_level_pixel)
psf_image.addNoiseSNR(noise, signal_to_noise)

#
# Warp the image using the edge rolloff transform.  This involves a 
# pixel-by-pixel mapping
#
warper = EdgeRolloffWarper(warp_amp, warp_scale, warp_width,
                           warp_amp, warp_scale, warp_width)

print "Warping image"
warped_image = warper.run(psf_image)

psf_image.wcs = getTanWCS(psf_image)
warped_image.wcs = psf_image.wcs

psf_image.write('star_grid_unwarped.fits')
warped_image.write('star_grid_warped.fits')

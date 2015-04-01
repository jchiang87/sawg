import sys
import numpy as np
import galsim
import lsst.afw.geom as afwGeom
import lsst.obs.lsstSim as obs_lsstSim

random_seed = 147918741

nxpix = 400
nypix = 400

xfunctor = obs_lsstSim.EdgeRolloffFunctor(2, 30, nxpix)
yfunctor = obs_lsstSim.EdgeRolloffFunctor(2, 30, nypix)

xytransform = afwGeom.SeparableXYTransform(xfunctor, yfunctor)

nx = 20
ny = 20
dx = nxpix/nx
dy = nypix/ny

pixel_scale = 1.0  # arcsec / pixel
sky_level = 1e6    # ADU / arcsec^2
signal_to_noise = 1000

psf_beta = 3
psf_fwhm = 2.85
psf_trunc = 2.*psf_fwhm
psf_image = galsim.ImageF(nxpix, nypix, scale=pixel_scale)

flux_range = 10.
flux_min = 1.
ud = galsim.UniformDeviate(random_seed)
k = 0
psf_flux = 1

def jacobian(transform, x, y):
    if not isinstance(transform, afwGeom.SeparableXYTransform):
        raise RuntimeError("Not a SeparableXYTransform")
    return (transform.getXfunctor().derivative(x)**2 +
            transform.getYfunctor().derivative(y)**2)/2.

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
##
## Add sky noise.
##
#sky_level_pixel = sky_level*pixel_scale**2
#noise = galsim.PoissonNoise(ud, sky_level=sky_level_pixel)
#psf_image.addNoiseSNR(noise, signal_to_noise)

psf_image.array[:] += np.ones((nypix, nxpix), dtype=np.float)*psf_flux/30.

#
# Warp the image using the edge rolloff transform.  This involves a 
# pixel-by-pixel mapping
#
print "Warping image"
warped_image = galsim.ImageF(nxpix, nypix, scale=pixel_scale)
for xw in range(nxpix):
    if xw % (nxpix/4) == 0:
        sys.stdout.write('!')
        sys.stdout.flush()
    elif xw % (nxpix/20) == 0:
        sys.stdout.write('.')
        sys.stdout.flush()
    for yw in range(nypix):
        ptw = afwGeom.Point2D(xw, yw)
        pt0 = xytransform.reverseTransform(ptw)
        x0 = int(np.round(pt0.getX()))
        y0 = int(np.round(pt0.getY()))
        try:
            warped_image.array[yw][xw] = \
                psf_image.array[y0][x0]/jacobian(xytransform, pt0.getX(), pt0.getY())
        except IndexError:
            pass
print "Done"

psf_image.write('psf_array_0.fits')
warped_image.write('psf_array_warped.fits')

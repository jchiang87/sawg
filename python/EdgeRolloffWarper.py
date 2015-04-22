import sys
import numpy as np
import galsim
import lsst.afw.image as afwImage
import lsst.afw.geom as afwGeom
import lsst.obs.lsstSim as obs_lsstSim

class EdgeRolloffWarper(object):
    def __init__(self, config, oversampling=1):
        xfunctor = obs_lsstSim.EdgeRolloffFunctor(config.xamp*oversampling,
                                                  config.xscale*oversampling, 
                                                  config.xwidth*oversampling)
        yfunctor = obs_lsstSim.EdgeRolloffFunctor(config.yamp*oversampling,
                                                  config.yscale*oversampling, 
                                                  config.ywidth*oversampling)
        self.transform = afwGeom.SeparableXYTransform(xfunctor, yfunctor)
    def jacobian(self, x, y):
        return (self.transform.getXfunctor().derivative(x)**2 +
                self.transform.getYfunctor().derivative(y)**2)/2.
    def run(self, image, verbose=True):
        try:
            # Assume it's an afwImage Image.
            warped_image = image.Factory(image, image.getBBox())
            wiarr = warped_image.getArray()
            imarr = image.getArray()
        except AttributeError:
            # It must be a galsim Image.
            warped_image = image.copy()
            wiarr = warped_image.array
            imarr = image.array
        ny, nx = wiarr.shape
        for xw in range(nx):
            self._progress(xw, nx, verbose=verbose)
            for yw in range(ny):
                ptw = afwGeom.Point2D(xw, yw)
                pt0 = self.transform.forwardTransform(ptw)
                x0 = int(np.round(pt0.getX()))
                y0 = int(np.round(pt0.getY()))
                try:
                    wiarr[yw][xw] = imarr[y0][x0]*self.jacobian(pt0.getX(),
                                                                pt0.getY())
                except IndexError:
                    pass
        if verbose:
            print "Done"
        return warped_image
    def nominal_to_actual_pixel(self, xpos, ypos):
        pt0 = afwGeom.Point2D(xpos, ypos)
        ptw = self.transform.reverseTransform(pt0)
        return ptw.getX(), ptw.getY()
    def _progress(self, x, nx, verbose=False, dx0=4, dx1=20):
        if not verbose:
            return
        if x % (nx/dx0) == 0:
            sys.stdout.write('!')
        elif x % (nx/dx1) == 0:
            sys.stdout.write('.')
        sys.stdout.flush()

if __name__ == '__main__':
    nx, ny = 400, 400
    #
    # Create an EdgeRolloffWarper
    #
    warper = EdgeRolloffWarper(2, 3, nx, 2, 3, ny)
    #
    # Apply it to a flat galsim image
    #
    image = galsim.ImageF(nx, ny)
    image.array[:] += np.ones(image.array.shape)

    warped_image = warper.run(image)

    image.write('unwarped_flat.fits')
    warped_image.write('warped_flat.fits')

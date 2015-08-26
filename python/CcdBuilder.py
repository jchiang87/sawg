import numpy as np
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.afw.cameraGeom.fitsUtils as fitsUtils
import lsst.ip.isr as ipIsr

def _parseGeomKeyword(value):
    tokens = value.split('[')[1].split(']')[0].split(',')
    xbounds = [int(x) for x in tokens[0].split(':')]
    ybounds = [int(x) for x in tokens[1].split(':')]
    return xbounds, ybounds

class CcdBuilder(fitsUtils.DetectorBuilder):
    _namps = 16
    def __init__(self, infile, **kwds):
        ampfiles = ['%s[%i]' % (infile, amp) for amp in range(1, self._namps+1)]
        super(CcdBuilder, self).__init__(infile, ampfiles, **kwds)
    def _sanitizeHeaderMetadata(self, metadata, clobber):
        naxis1 = metadata.get('NAXIS1')
        naxis2 = metadata.get('NAXIS2')
        # Infer redundant BIASSEC from DATASEC and NAXIS1
        xbnds, ybnds = _parseGeomKeyword(metadata.get('DATASEC'))
        biassec = '[%i:%i,1:%i]' % (xbnds[1]+1, naxis1, ybnds[1])
        fitsUtils.setByKey(metadata, 'BIASSEC', biassec, clobber)
        # Get channel number and convert to zero index
        channel = fitsUtils.getByKey(metadata, 'CHANNEL')-1
        if channel is None:
            raise ValueError("Channel keyword not found in header")
        ny = channel//8
        sign = 1 if ny%2 else -1
        nx = 7*ny - sign*(channel%8)
        fitsUtils.setByKey(metadata, 'DTV1', nx*naxis1, clobber)
        fitsUtils.setByKey(metadata, 'DTV2', ny*naxis2, clobber)
        # Infer DTM values from DETSEC values.
        xb, yb = _parseGeomKeyword(metadata.get('DETSEC'))
        fitsUtils.setByKey(metadata, 'DTM1_1', np.sign(xb[1] - xb[0]), clobber)
        fitsUtils.setByKey(metadata, 'DTM2_2', np.sign(yb[1] - yb[0]), clobber)
        self._defaultSanitization(metadata, clobber)
    def assembleImage(self, gains=None):
        imDict = {}
        hdus = {}
        for i in range(self._namps):
            hdu = i + 1
            filename = '%s[%i]' % (infile, hdu)
            md = afwImage.readMetadata(filename)
            imDict[md.get('EXTNAME')] = afwImage.ImageF(filename)
            hdus[md.get('EXTNAME')] = hdu
        det = self.buildDetector()
        assembleInput = {}
        for amp in det:
            im = imDict[amp.getName()]
            oscanim = im.Factory(im, amp.getRawHorizontalOverscanBBox())
            oscan = afwMath.makeStatistics(oscanim, afwMath.MEDIAN).getValue()
            im -= oscan
            if gains is not None:
                im *= gains[hdus[amp.getName()]]
            assembleInput[amp.getName()] = self.makeExposure(im)

        assembleConfig = ipIsr.AssembleCcdTask.ConfigClass()

        assembleConfig.doTrim = True
        assembler = ipIsr.AssembleCcdTask(config=assembleConfig)
        resultExp = assembler.assembleCcd(assembleInput)
        return resultExp.getMaskedImage().getImage()

if __name__ == '__main__':
#    infile = '113-03_lambda_1000_flat_20140709172215.fits.gz'
#    outfile = '113-03_assembled_image.fits'

#    infile = '114-04_lambda_0980_flat_20140501072543.fits.gz'
#    outfile = '114-04_assembled_image.fits'

    infile = 'snap_1440463613702-firstset-dark-500-0.fits'
    outfile = 'snap_mosaicked.fits'

#    infile = 'snap_ltkw_repaired.fits'
#    outfile = 'snap_ltkw_repaired_mosaicked.fits'

    builder = CcdBuilder(infile, inAmpCoords=True, clobberMetadata=True)

    ccd_image = builder.assembleImage(gains=dict((x, 2) for x in range(1, 17)))
    ccd_image.writeFits(outfile)

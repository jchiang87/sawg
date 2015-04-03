import numpy as np
import lsst.afw.table as afwTable
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.daf.base as dafBase
import lsst.meas.algorithms as measAlg
import lsst.afw.display.ds9 as ds9

from lsst.meas.algorithms.detection import SourceDetectionTask
from lsst.meas.algorithms.measurement import SourceMeasurementTask, \
    SourceSlotConfig
from lsst.pipe.tasks.calibrate import CalibrateTask

def measure_stars(image_file='star_grid_warped.fits'):
    schema = afwTable.SourceTable.makeMinimalSchema()
    schema.setVersion(0)

    cal_config = CalibrateTask.ConfigClass()
    cal_config.doAstrometry = False
    cal_config.doPhotoCal = False
    cal_config.doBackground = True

    calibrateTask = CalibrateTask(config=cal_config)
    calibrateTask.repair.config.doCosmicRay = False
    calibrateTask.detection.config.thresholdValue = 5
    calibrateTask.detection.config.includeThresholdMultiplier = 1

    det_config = SourceDetectionTask.ConfigClass()
    det_config.reEstimateBackground = False
    detectionTask = SourceDetectionTask(config=det_config, schema=schema)

    meas_config = SourceMeasurementTask.ConfigClass()
    meas_config.algorithms.names.clear()
    for alg in "shape.sdss flux.sinc flux.aperture flux.gaussian".split():
        meas_config.algorithms.names.add(alg)
    meas_config.algorithms['flux.aperture'].radii = (1, 2, 4, 8, 16)

    algMetaData = dafBase.PropertyList()
    measureTask = SourceMeasurementTask(schema, algMetaData, config=meas_config)

    output_table = afwTable.SourceTable.make(schema)

    exposure = afwImage.ExposureF(image_file)
    mi = exposure.getMaskedImage()
    varclip = afwMath.makeStatistics(mi.getImage(), 
                                     afwMath.VARIANCECLIP).getValue()
    #print "varclip =", varclip
    mi.getVariance().getArray()[:] = np.ones(mi.getArrays()[0].shape)*varclip
 
    calibrateTask.config.initialPsf.fwhm = 2.85
    calibrateTask.installInitialPsf(exposure)

    result = calibrateTask.run(exposure)
    exposure, calibSources = result.exposure, result.sources

#    sources = detectionTask.run(output_table, exposure, sigma=5).sources

    # Disable psfFlux since it is crashing.
    measureTask.config.slots.psfFlux = None
    measureTask.run(exposure, calibSources)
    return exposure, calibSources

if __name__ == '__main__':
    exposure0, sources0 = measure_stars('star_grid_unwarped.fits')
    exposure1, sources1 = measure_stars('star_grid_warped.fits')

    for srcs in zip(sources0[:3], sources1):
        for src in srcs:
            for span in src.getFootprint().getSpans():
                print span.getY(), span.getX0(), span.getX1()
            print
        print
    
#    frame = 1
#    ds9.mtv(exposure, frame=frame)
#    for source in sources:
#        xy = source.getCentroid()
#        ds9.dot('o', *xy, frame=frame)

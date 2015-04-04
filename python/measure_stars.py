import sys
import numpy as np
import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath
import lsst.afw.table as afwTable
import lsst.afw.display.ds9 as ds9
import lsst.daf.base as dafBase

from lsst.meas.algorithms.detection import SourceDetectionTask
from lsst.meas.algorithms.measurement import SourceMeasurementTask
from lsst.pipe.tasks.calibrate import CalibrateTask

from EdgeRolloffWarper import EdgeRolloffWarper

image_file='star_grid_warped.fits'
schema = afwTable.SourceTable.makeMinimalSchema()
schema.setVersion(0)

#
# CalibrateTask
#
cal_config = CalibrateTask.ConfigClass()
cal_config.doAstrometry = False
cal_config.doPhotoCal = False
cal_config.doBackground = True

calibrateTask = CalibrateTask(config=cal_config)

calibrateTask.repair.config.doCosmicRay = False
calibrateTask.detection.config.thresholdValue = 5
calibrateTask.detection.config.includeThresholdMultiplier = 1
calibrateTask.config.initialPsf.fwhm = 2.85

#
# SourceDetectionTask
#
det_config = SourceDetectionTask.ConfigClass()
det_config.reEstimateBackground = False

detectionTask = SourceDetectionTask(config=det_config, schema=schema)

#
# SourceMeasurementTask
#
meas_config = SourceMeasurementTask.ConfigClass()
meas_config.algorithms.names.clear()
for alg in "shape.sdss flux.sinc flux.aperture flux.gaussian".split():
    meas_config.algorithms.names.add(alg)
meas_config.algorithms['flux.aperture'].radii = (1, 2, 4, 8, 16)

algMetaData = dafBase.PropertyList()
measureTask = SourceMeasurementTask(schema, algMetaData, config=meas_config)

exposure = afwImage.ExposureF(image_file)
#
# Add variance, inferred from the data, to the exposure
#
mi = exposure.getMaskedImage()
varclip = afwMath.makeStatistics(mi.getImage(), 
                                 afwMath.VARIANCECLIP).getValue()
mi.getVariance().getArray()[:] = np.ones(mi.getArrays()[0].shape)*varclip

#
# Run calibration task
#
result = calibrateTask.run(exposure)
exposure, calibSources = result.exposure, result.sources

#
# Create XYTransform for the edge rolloff effect
#
warper = EdgeRolloffWarper(2, 30, 400, 2, 30, 400)
transform = warper.transform.clone()
distortedTanWcs = afwImage.DistortedTanWcs(afwImage.TanWcs.cast(exposure.getWcs()), transform)

#output_table = afwTable.SourceTable.make(schema)
#sources = detectionTask.run(output_table, exposure, sigma=5).sources
#
## Disable psfFlux since it is crashing.
#measureTask.config.slots.psfFlux = None
#measureTask.run(exposure, calibSources)

#if __name__ == '__main__':
#    exposure0, sources0 = measure_stars('star_grid_unwarped.fits')
#    exposure1, sources1 = measure_stars('star_grid_warped.fits')
#
#    for srcs in zip(sources0[:3], sources1):
#        for src in srcs:
#            for span in src.getFootprint().getSpans():
#                print span.getY(), span.getX0(), span.getX1()
#            print
#        print
#    
#    frame = 1
#    ds9.mtv(exposure, frame=frame)
#    for source in sources:
#        xy = source.getCentroid()
#        ds9.dot('o', *xy, frame=frame)

import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage
import lsst.pex.config as pexConfig
from lsst.obs.lsstSim import EdgeRolloffFunctor

class EdgeRolloffConfig(pexConfig.Config):
    """
    Config class for modeling the sensor edge rolloff via
    lsst.obs.lsstSim.EdgeRolloffFunctors and a SeparableXYTransform.
    """
    xamp = pexConfig.Field(dtype=float, default=-2,
                           doc="amplitude (pixels) of edge rolloff distortion in the x-direction")
    xscale = pexConfig.Field(dtype=float, default=3,
                             doc="scale (pixels) of edge rolloff distortion in the x-direction")
    xwidth = pexConfig.Field(dtype=float, default=4096,
                             doc="width (pixels) of sensor in x-direction")
    yamp = pexConfig.Field(dtype=float, default=-2,
                           doc="amplitude (pixels) of edge rolloff distortion in the y-direction")
    yscale = pexConfig.Field(dtype=float, default=3,
                             doc="scale (pixels) of edge rolloff distortion in the y-direction")
    ywidth = pexConfig.Field(dtype=float, default=4004,
                             doc="width (pixels) of sensor in y-direction")
    applyModel = pexConfig.Field(dtype=bool, default=False,
                                 doc="If True, then apply the distortion model in the WCS")

def addEdgeRolloffDistortion(exposure, config=EdgeRolloffConfig()):
    xfunctor = EdgeRolloffFunctor(config.xamp, config.xscale, config.xwidth)
    yfunctor = EdgeRolloffFunctor(config.yamp, config.yscale, config.ywidth)
    transform = afwGeom.SeparableXYTransform(xfunctor, yfunctor)
    tanWcs = afwImage.TanWcs.cast(exposure.getWcs())
    distortedTanWcs = afwImage.DistortedTanWcs(tanWcs, transform)
    exposure.getInfo().setWcs(distortedTanWcs)

class LinearWarpConfig(pexConfig.Config):
    """
    Config class for modeling linear sensor distortions using
    lsst.afw.geom.LinearFunctors and a SeparableXYTransform.
    """
    xslope = pexConfig.Field(dtype=float, default=1,
                             doc="slope of linear distortion in x-direction")
    xintercept = pexConfig.Field(dtype=float, default=2.,
                                 doc="intercept of linear distortion in x-direction")
    yslope = pexConfig.Field(dtype=float, default=1.,
                             doc="slope of linear distortion in y-direction")
    yintercept = pexConfig.Field(dtype=float, default=3,
                                 doc="intercept of linear distortion in y-direction")
    applyModel = pexConfig.Field(dtype=bool, default=False,
                                 doc="If True, then apply the distortion model in the WCS")

def addLinearWarpDistortion(exposure, config=LinearWarpConfig()):
    xfunctor = afwGeom.LinearFunctor(config.xslope, config.xintercept)
    yfunctor = afwGeom.LinearFunctor(config.yslope, config.yintercept)
    transform = afwGeom.SeparableXYTransform(xfunctor, yfunctor)
    tanWcs = afwImage.TanWcs.cast(exposure.getWcs())
    distortedTanWcs = afwImage.DistortedTanWcs(tanWcs, transform)
    exposure.getInfo().setWcs(distortedTanWcs)

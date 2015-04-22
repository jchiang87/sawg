import lsst.pex.config as pexConfig
from lsst.obs.lsstSim import EdgeRolloffConfig

class TanWcsConfig(pexConfig.Config):
    """
    Configuration class for TanWcs projection used by galsim.TanWCS.
    """
    dudx = pexConfig.Field(dtype=float, default=1, doc="")
    dudy = pexConfig.Field(dtype=float, default=0, doc="")
    dvdx = pexConfig.Field(dtype=float, default=0, doc="")
    dvdy = pexConfig.Field(dtype=float, default=1, doc="")
    ra_center = pexConfig.Field(dtype=float, default=12, doc='RA in hours')
    dec_center = pexConfig.Field(dtype=float, default=0,
                                 doc='Dec in degrees')

class SensorSimConfig(pexConfig.Config):
    """
    Configuration class for GalSim-based star grid simulations to
    study sensor warping effects.
    """
    xextent = pexConfig.Field(dtype=int, default=4000,
                              doc="Number of pixels in sensor x-direction")
    yextent = pexConfig.Field(dtype=int, default=4000,
                              doc="Number of pixels in sensor y-direction")
    oversampling = pexConfig.Field(dtype=int, default=10,
                                   doc="Number of micro pixels per pixel")
    pixel_scale = pexConfig.Field(dtype=float, default=0.2, doc="arcsec / pixel")

    sky_level = pexConfig.Field(dtype=float, default=1e6, doc="ADU / arcsec^2")
    signal_to_noise = pexConfig.Field(dtype=float, default=1e4,
                                      doc="star flux relative to sky noise")

    psf_flux = pexConfig.Field(dtype=float, default=1, doc="")
    psf_beta = pexConfig.Field(dtype=float, default=3,
                               doc="Moffat profile beta parameter")
    psf_fwhm = pexConfig.Field(dtype=float, default=0.5, doc='arcsec')
    psf_trunc_scale = pexConfig.Field(dtype=float, default=2.,
                                      doc='psf_trunc = psf_trunc_scale*psf_fwhm')
    
    nxpix = pexConfig.Field(dtype=int, default=200,
                            doc="Number of x pixels to simulate starting at llc")
    nypix = pexConfig.Field(dtype=int, default=200,
                            doc="Number of y pixels to simulate starting at llc")
    nxstars = pexConfig.Field(dtype=int, default=10,
                              doc="Number of stars columns")
    nystars = pexConfig.Field(dtype=int, default=10,
                              doc="Number of stars rows")
    star_coords_file = pexConfig.Field(dtype=str,
                                       default='star_grid_coordinates.txt',
                                       doc='output file for MC star coords')
    @property
    def psf_trunc(self):
        return self.psf_trunc_scale*self.psf_fwhm
    @property
    def star_grid_dx(self):
        return self.nxpix*self.oversampling/self.nxstars
    @property
    def star_grid_dy(self):
        return self.nypix*self.oversampling/self.nystars
    @property
    def x0(self):
        "x-coordinate of image center (pixels)"
        return (self.nxpix/2. - 0.5)*self.oversampling
    @property
    def y0(self):
        "y-coordinate of image center (pixels)"
        return (self.nypix/2. - 0.5)*self.oversampling


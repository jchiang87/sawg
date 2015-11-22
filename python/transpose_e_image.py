import pyfits

foo = pyfits.open('lsst_e_99999999_f2_R22_S11_E000.fits.gz',
                  do_not_scale_image_data=True)

# Perform a flip in x and a -90 rotation about z.
foo[0].data = foo[0].data.transpose()[::-1,::-1]

foo.writeto('lsst_e_transpose.fits', clobber=True)

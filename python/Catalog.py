import pyfits

class Catalog(object):
    def __init__(self, catalog_file):
        self.filename = catalog_file
        self.hdulist = pyfits.open(catalog_file)
    def getCentroids(self, centroid='GaussianCentroid'):
        return (self.hdulist[1].data.field('base_%s_x' % centroid),
                self.hdulist[1].data.field('base_%s_y' % centroid))
    def getCoords(self):
        coords = self.hdulist[1].data.field('coord')
        return zip(*coords)
    def getColumn(self, colname):
        return self.hdulist[1].data.field(colname)
    def write_region_file(self, outfile='ds9.reg', centroid='GaussianCentroid'):
        output = open(outfile, 'w')
        output.write("""# Region file format: DS9 version 4.1
global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
physical
""")
        for xx, yy in zip(*self.getCentroids(centroid=centroid)):
            x = xx + 1
            y = yy + 1
            output.write("point(%(x).4f,%(y).4f) # point=circle\n" % locals())
        output.close()
        
    

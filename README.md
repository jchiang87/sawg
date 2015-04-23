# sawg
Work for LSST Camera Sensor Analysis Working Group

This package should be used with an LSST stack installation that has versions of lsst.afw and lsst.obs.lsstSim no earlier than those indicated here:
```
In [1]: import lsst.afw

In [2]: lsst.afw.__version__
Out[2]: 'master-g8708957e45+2'

In [3]: import lsst.obs.lsstSim

In [4]: lsst.obs.lsstSim.__version__ 
Out[4]: 'master-gc584ed14e8+3'
```

Once you have the stack setup, just add the python directory to your PYTHONPATH and the bin directory to your PATH.

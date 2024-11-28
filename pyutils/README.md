# python utilities (pyutils)

## Purpose

pyutils aims to provide a user friendly interface between EventNtuple and python. We aim to use packages available in the standard mu2e python environment and provide functionality that will be common to many Mu2e analysis groups.

## Analysis Environment

The Analysis python Environment is maintained by the L4 for Analysis Environment (currently Sam Grant).

To activate the environment:

```
source /cvmfs/mu2e.opensciencegrid.org/env/ana/current/bin/activate
```

If a package you require is not present, please contact Sam.


## General Functionality

The mu2epyutils script currently contains several key classes.

### Usage

To use the mu2e pyutils:

```
import pyimport as evn
import pyvector as vec
import pyplot as plot
import pyprint as prnt
```

### Imports

Imports the ntuple and places the contents into awkward array ready for analysis. To import an EventNtuple made using v6:

```
mytuple = evn.Import("file.root", "EventNtuple", "ntuple")

```
To accsess a given tree:

```
treename = 'trksegs'
ntuple = test_evn.ImportTree()
branch = test_evn.ImportBranches(ntuple,[str(treename)])
```

We also provide function to access a given surface ID:

```
surface_id = 0 # tracker entrance
trkent = test_evn.SelectSurfaceID(branch, treename, surface_id)
```

Here the user is asking for the trk fit (trksegs) as measured at the front of the tracker.

### Plots/style

We hope to provide standard plotting functions with a specific style to make presentaions and papers more professional. We encourage users to use one of the standard style options for their plots. The current style file is: mu2e.mplstyle. It is imported in pyplotter.py automatically (called in the init of that class).

If you wish to use this style in your own scripts:

```
plt.style.use('mu2e.mplstyle')
```

To use the plotter functions, create a pyplot object:

```
myhist = plot.Plot()
```


### Vectors

EventNtuple when imported into python does not retain the vector operations (mag, angle etc.). We are left with simply x,y,z coordinates for momentum or positions. The Vector class acts to restore vector operations in a pure python environment.

To use the vector functionality:

```
myvect = vec.Vector()
vecbranchname = 'mom'
vector_test = myvect.GetVectorXYZ(trkent, treename, vecbranchname)
magnitude = myvect.Mag(vector_test)
print("list of mom mags: ", magnitude)

# make 1D plot of magnitudes
myhist.PlotMagValueHist(magnitude, 95, 115, "fit mom at Trk Ent [MeV/c]","log")
```

## MC util

Development underway by Leo Borrel (contact for update).

## Development

Reach out to Andy (L3 Analysis Tools/L4 Analysis Framework), Sophie (L3 Analysis Tools) or Sam (L4 Analysis Environment) if you want to contribute.

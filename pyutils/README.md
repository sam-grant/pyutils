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

### Importing multiple files

If you are working with a list of files, write the list to a text file and use:

```
test_evn.ImportFileList(fullpath/filename.list)
```

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

The plot class allows standard histograms in 1D and 2D with optional error bars as well as graphs. Several examples are shown in example.py.

The arguments are somewhat details, here is a list of definitions:

Plot1D (with defaults)
* weights_=None: to scale a histogram
* nbins=100: number of bins
* xmin=-1.0:  xmax=1.0:  x axis range
* title=None:  title of plot
* xlabel=None:  x axis label
* ylabel=None:  y axis label
* col='black':  colour choice
* leg_pos='best':  legend position
* fout='hist.png':  file name to save to
* NDPI=300: 
* stats=True:  plot the stats box
* log_x=False:  log scale in x
* log_y=False:  log scale in y
* under_over=False:  add under/over flow to stats box
* stat_errors=False:  add stat errors to stat box
* error_bars=False:  draw error bars
* show=True: show plot interactively

Plot2D (with defaults):

* weights_=None
* nbins_x=100:  number of bins in x
* xmin=-1.0:  x axis range
* xmax=1.0:  x axis range
* nbins_y=100:  number of bins in y
* ymin=-1.0:  y axis range
* ymax=1.0: y axis range
* title=None: title of plot
* xlabel=None:  x axis label
* ylabel=None:  y axis label
* zlabel=None:  z axis label
* fout='hist.png': file name to save to
* cmap='inferno':  for weight axis
* NDPI=300:  
* log_x=False: log scale in x
* log_y=False: log scale in y
* log_z=False:  log scale in z
* cb=True: add colour bar
* show=True: show plot interactively


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
flatarraymom = ak.flatten(magnitude, axis=None)
myhist.Plot1D(flatarraymom  , None, 100, 100,115, "example", "fit mom at Trk Ent [MeV/c]", "#events per bin", 'black', 'best', 'time.pdf', 300, True, False, True, False, True, True, True)
```

## MC util

Development underway by Leo Borrel (contact for update).

## Development

Reach out to Andy (L3 Analysis Tools/L4 Analysis Framework), Sophie (L3 Analysis Tools) or Sam (L4 Analysis Environment) if you want to contribute.

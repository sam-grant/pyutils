# python utilities (pyutils)

## Purpose

pyutils aims to provide a user friendly interface between EventNtuple and python. We aim to use packages available in the standard mu2e python environment and provide functionality that will be common to many Mu2e analysis groups.

## General Functionality

The mu2epyutils script currently contains several key classes.

### Imports

Imports the ntuple and places the contents into awkward array ready for analysis.

A few functions to make applying standard signal selection cuts easier are under development.


### Plots/style

We hope to provide standard plotting functions with a specific style to make presentaions and papers more professional. We encourage users to use one of the standard style options for their plots.

We also encourage suggestions and enhancements here.

### Vectors

EventNtuple when imported into python does not retain the vector operations (mag, angle etc.). We are left with simply x,y,z coordinates for momentum or positions. The Vector class acts to restore vector operations in a pure python environment.

## MC utils

Development underway by Leo Borrel (contact for update).

The MC utils provide an interface for anyone wanting to know the true nature of a given track and link us back to the process origin of the track.

## Development

Reach out to Andy (L3 Analysis Tools/L4 Analysis Framework), Sophie (L3 Analysis Tools) or Sam (L4 Analysis Environment) if you want to contribute.

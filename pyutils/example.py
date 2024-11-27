import pyimport as evn
import pyvector as vec
import pyplot as plot

import uproot
import awkward as ak
import matplotlib.pyplot as plt
import math
import numpy as np
import vector
from scipy import stats
from matplotlib.ticker import ScalarFormatter
import matplotlib.colors as colors

def main():
  """ simple test function to run some of the utils """
  """
  test_evn = evn("/exp/mu2e/app/users/sophie/ProductionEnsembles_v2/py-ana/trkana/pass0a.root", "TrkAna", "trkana")
  surface_id = 0 # tracker entrance
  vector_test = test_evn.GetVectorXYZ("demfit", "mom", surface_id)
  print("vector magnitudes extracted : ", vector_test.mag)
  test_evn.PlotMagValueHist("demfit", "mom", surface_id, 95, 115, "fit mom at Trk Ent [MeV/c]","log")
  test_evn.PlotValueHist("demfit", "time", surface_id, 450, 1700, "fit time at Trk Ent [ns]", 'linear')
  """
  
  # import the files
  test_evn = evn.Import("/exp/mu2e/data/users/sophie/ensembles/MDS1/MDS1a.root", "EventNtuple", "ntuple")
  filepath = "/exp/mu2e/data/users/sophie/ensembles/MDS1/file.list"
  #test_evn.ImportFileList(filepath)
  
  # import code and extract branch
  treename = 'trksegs'
  branchname = 'time'
  surface_id = 0 # tracker entrance FIXME - we need a better way for this
  ntuple = test_evn.ImportTree()
  branch = test_evn.ImportBranches(ntuple,[str(treename)])
  
  # find fit at chosen ID
  trkent = test_evn.SelectSurfaceID(branch, treename, surface_id)
  
  # make plots
  myhist = plot.Plot()
  myhist.PlotValueHist(trkent, treename, branchname,  450, 1650, "fit time at Trk Ent [ns]", 'linear')
  
  
  """
  vector_test = vec.Vector.GetVectorXYZ(branch, treename, branchname, surface_id)
  print("vector magnitudes extracted : ", vector_test.mag)
  
  plot.Plot.PlotMagValueHist(vector_test, surface_id, 95, 115, "fit mom at Trk Ent [MeV/c]","log")
  """
  
if __name__ == "__main__":
    main()

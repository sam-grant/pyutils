import pyimport as evn
import pyvector as vec
import pyplot as plot
import pyprint as prnt
import awkward as ak
def main():
  """ simple test function to run some of the utils """

  # import the files
  test_evn = evn.Import("/exp/mu2e/data/users/sophie/ensembles/MDS1/MDS1a.root", "EventNtuple", "ntuple")

  # import code and extract branch
  treename = 'trksegs'
  branchname = 'time'
  surface_id = 0 # tracker entrance FIXME - we need a better way for this
  ntuple = test_evn.ImportTree()
  
  print(ntuple.keys())

  # apply a simple cut
  treenames = ['trksegs','trksegpars_lh','trksegpars_lh']
  branch = test_evn.ImportBranches(ntuple,treenames)
  branchnames = ['time','t0err','maxr']
  minvals = [700,0,450]
  maxvals = [1650,0.9,680]
  cutarray = test_evn.MultiTrkCut(branch, treenames, branchnames, minvals, maxvals, surface_id)
  flatarraycut = ak.flatten(cutarray[str(treename)][str(branchname)], axis=None)
  
  # make 1D plot
  trkent = test_evn.SelectSurfaceID(branch, treename, surface_id)
  print(trkent)
  myhist = plot.Plot()
  flatarraytime = ak.flatten(trkent[str(branchname)], axis=None)
  
  dictarrays = { "no cut" : flatarraytime, "with cut" : flatarraycut }
  myhist.Plot1DOverlay(dictarrays, 100, 450, 1695, "Mu2e Example", "fit time at Trk Ent [ns]", "#events per bin", 'timecut.pdf', 'best', 300,False, True, True)
  
  
  
  
if __name__ == "__main__":
    main()

import pyimport as evn
import pyvector as vec
import pyplot as plot
import pyprint as prnt
import awkward as ak

def main():
  """ simple test function to run some of the utils """
  
  # import the files
  test_evn = evn.Import(None, "EventNtuple", "ntuple")
  
  #import a list of files
  filepath = "/exp/mu2e/data/users/sophie/ensembles/MDS1/file.list"

  # import code and extract branch
  treename = 'trksegs'
  branchname = 'time'
  surface_id = 0 # tracker entrance FIXME - we need a better way for this
  branch = test_evn.ImportTreeFromFileList(filepath, treename)

  # find fit at chosen ID
  trkent = test_evn.SelectSurfaceID(branch, treename, surface_id)

  # make 1D plot
  myhist = plot.Plot()
  flatarraytime = ak.flatten(trkent[str(branchname)], axis=None)
  myhist.Plot1D(flatarraytime, None, 100, 450, 1695, "Mu2e Example", "fit time at Trk Ent [ns]", "#events per bin", 'black', 'best', 'time_merged.pdf', 300, True, False, False, False, True, True, True)
  
if __name__ == "__main__":
    main()

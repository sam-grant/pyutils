import pyimport as evn
import pyvector as vec
import pyplot as plot
import pyprint as prnt
import pyselect as slct
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
  branch = test_evn.ImportBranches(ntuple,[str(treename)])
  
  # find fit at chosen ID
  mysel = slct.Select()
  trkent = mysel.SelectSurfaceID(branch, treename, surface_id)
  
  # make 1D plot
  myhist = plot.Plot()
  flatarraytime = ak.flatten(trkent[str(branchname)], axis=None)
  myhist.Plot1D(flatarraytime, None, 100, 450, 1695, "Mu2e Example", "fit time at Trk Ent [ns]", "#events per bin", 'black', 'best', 'time.pdf', 300, True, False, False, False, True, True, True)
  
  # apply a simple cut
  cutarray = mysel.SingleTrkCut(branch, treename, branchname, 700, 1650)
  flatarraycut = ak.flatten(cutarray[str(branchname)], axis=None)
  dictarrays = { "no cut" : flatarraytime, "with cut" : flatarraycut }
  myhist.Plot1DOverlay(dictarrays, 100, 450, 1695, "Mu2e Example", "fit time at Trk Ent [ns]", "#events per bin", 'timecut.pdf', 'best', 300,False, True, True)
  
  # access vectors
  myvect = vec.Vector()
  vecbranchname = 'mom'
  trkentall = mysel.SelectSurfaceID(branch, treename, surface_id)
  vector_test = myvect.GetVectorXYZFromLeaf(trkentall, vecbranchname)
  magnitude = myvect.Mag(vector_test)
  print("list of mom mags: ", magnitude)
  
  # make 1D plot of magnitudes
  flatarraymom = ak.flatten(magnitude, axis=None)
  myhist.Plot1D(flatarraymom  , None, 100, 95, 115, "Mu2e Example", "fit mom at Trk Ent [MeV/c]", "#events per bin", 'black', 'best', 'mom.pdf', 300, True, False, True, False, True, True, True)

  # 2D mom time plot
  myhist.Plot2D( flatarraymom, flatarraytime, None, 100, 95, 115, 100, 450, 1650, "Mu2e Example", "fit mom at Trk Ent [MeV/c]", "fit time at Trk Ent [ns]", None, 'timevmom.pdf', 'inferno',300,False, False, False, True,True)
        
  
if __name__ == "__main__":
    main()

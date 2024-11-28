import pyimport as evn
import pyvector as vec
import pyplot as plot
import pyprint as prnt
import awkward as ak
def main():
  """ simple test function to run some of the utils """
  
  # import the files
  test_evn = evn.Import("/exp/mu2e/data/users/sophie/ensembles/MDS1/MDS1a.root", "EventNtuple", "ntuple")
  filepath = "/exp/mu2e/data/users/sophie/ensembles/MDS1/file.list"
  
  # import code and extract branch
  treename = 'trksegs'
  branchname = 'time'
  surface_id = 0 # tracker entrance FIXME - we need a better way for this
  ntuple = test_evn.ImportTree()
  branch = test_evn.ImportBranches(ntuple,[str(treename)])
  
  # find fit at chosen ID
  trkent = test_evn.SelectSurfaceID(branch, treename, surface_id)

  # make 1D plot
  myhist = plot.Plot()
  flatarraytime = ak.flatten(trkent[str(treename),str(branchname)], axis=None)
  myhist.Plot1D(flatarraytime, None, 100, 450, 1650, "example", "fit time at Trk Ent [ns]", "#events per bin", 'black', 'best', 'time.pdf', 300, True, False, False, False, True, True, True)
  
  # access vectors
  myvect = vec.Vector()
  vecbranchname = 'mom'
  vector_test = myvect.GetVectorXYZ(trkent, treename, vecbranchname)
  magnitude = myvect.Mag(vector_test)
  print("list of mom mags: ", magnitude)
  
  # make 1D plot of magnitudes
  flatarraymom = ak.flatten(magnitude, axis=None)
  myhist.Plot1D(flatarraymom  , None, 100, 100,115, "example", "fit mom at Trk Ent [MeV/c]", "#events per bin", 'black', 'best', 'time.pdf', 300, True, False, True, False, True, True, True)
  
  # plot example overlays (mc truth .v. reco)
  treenamemc = 'trksegsmc'
  branchmc = test_evn.ImportBranches(ntuple,[str(treenamemc)])
  trkentmc = test_evn.SelectSurfaceID(branchmc, treenamemc, surface_id)
  flatarraymc = ak.flatten(trkent[str(treenamemc),str(vecbranchname)], axis=None)
  dictarrays = { "true" : flatarraymc, "reco" : flatarraymom }
  myhist.Plot1DOverlay(dictarrays, 100, 95,115, "example", "fit mom at Trk Ent [MeV/c]", "#events per bin", 'overlay.pdf', 'best', 300,False, True, False, True)

  # 2D mom time plot
  myhist.Plot2D( flatarraymom, flatarraytime, None, 100, 95, 115, 100, 450, 1650, "example", "fit mom at Trk Ent [MeV/c]", "fit mom at Trk Ent [MeV/c]", None, 'timevmom.pdf', 'inferno',300,False, False, False, True,True)
        
  # printing
  myprint = prnt.Print()
  
  #import a list of files
  #test_evn.ImportFileList(filepath)
  
if __name__ == "__main__":
    main()

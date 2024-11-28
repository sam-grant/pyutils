import pyimport as evn
import pyvector as vec
import pyplot as plot

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
  myhist.PlotValueHist(trkent, treename, branchname,  450, 1650, "fit time at Trk Ent [ns]", 'linear')
  
  # access vectors
  myvect = vec.Vector()
  vecbranchname = 'mom'
  vector_test = myvect.GetVectorXYZ(trkent, treename, vecbranchname)
  magnitude = myvect.Mag(vector_test)
  print("list of mom mags: ", magnitude)
  
  # make 1D plot of magnitudes
  myhist.PlotMagValueHist(magnitude, 95, 115, "fit mom at Trk Ent [MeV/c]","log")
  
  #import a list of files
  #test_evn.ImportFileList(filepath)
  
if __name__ == "__main__":
    main()

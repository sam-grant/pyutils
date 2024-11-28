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
  test_evn.ImportFileList(filepath)

  
if __name__ == "__main__":
    main()

import uproot
import awkward as ak

class Import:
  """ class to help users import a trkana tree and branch """
  def __init__(self, filename, dirname="EventNtuple", treename="ntuple"):
    self.filename= filename
    self.dirname = dirname
    self.treename = treename
    self.Array = ak.Array
  
  def ImportFileList(self, path): 
    """ Import list of files from a text file """
    with open(path, "r") as file_list_: # Open file
      lines_ = file_list_.readlines() # Read file
      lines_ = [line.strip() for line in lines_]  # Remove leading/trailing whitespace
    return lines_ # Return lines as a list

  def ImportFileListFromSAM(self):
    """ import list of files """
    #TODO
    pass

  def ImportTree(self):
    """ import root tree """
    input_file = uproot.open(self.filename)
    input_tree = input_file[self.dirname][self.treename]
    return input_tree
    
  def MakeAwkArray(self):
    """ import root tree and save it as an Awkward array """
    input_tree = self.ImportTree()
    self.Array = input_tree.arrays(library='ak')
    return self.Array


  def ImportBranches(self, tree, branchnames):
    """ import list of branches from trkana"""
    list_names = []
    for i, branchname  in enumerate(branchnames):
        list_names.append("/"+str(branchname)+"/")
    branches = tree.arrays(filter_name=list_names, library='ak')
    return branches
      
  def SelectSurfaceID(self, branch, treename, sid):
    """ allows user to see trk fits only on chosen surface"""
    # take the chosen position to evaluate
    trk_mask = (branch[str(treename)]['sid']==sid)
    values = branch.mask[(trk_mask)]
    return values
    
  def EvtCut(self):
    #TODO
    pass
    
  def TrkCut(self):
    #TODO
    pass
  
  def TrkSegCut(self):
    #TODO
    pass
    
  def TrkCrvCoincsCut(self):
    #TODO
    pass


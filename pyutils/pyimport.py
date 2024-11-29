#! /usr/bin/env python
import uproot
import awkward as ak

class Import:
  """ class to help users import a trkana tree and branch """
  def __init__(self, filename=None, dirname="EventNtuple", treename="ntuple", filelist=False):
    self.filename= filename
    self.dirname = dirname
    self.treename = treename
    self.Array = ak.Array
    
  def ImportTreeFromFileList(self, path, branchname): 
    """ Import list of files from a text file and merge a specific branch"""
    with open(path, "r") as file_list_: # Open file
      filelist = file_list_.readlines() # Read file
      # Remove leading/trailing whitespace
      filelist = [line.strip() for line in filelist]
    print("file list", filelist)
    # Concatenate the TTrees named "mytree" from each file
    merged_tree = uproot.concatenate([f"{file}:"+str(self.dirname)+"/"+str(self.treename)+"/"+str(branchname) for file in filelist])
    return merged_tree

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
      
  def SelectSurfaceIDAll(self, branch, treename, sid=0):
    """ allows user to see trk fits only on chosen surface but retains all branch """
    trk_mask = (branch[str(treename)]['sid']==sid)
    values = branch.mask[(trk_mask)]
    return values
    
  def SelectSurfaceID(self, branch, treename, sid=0):
    """ allows user to see trk fits only on chosen surface chooses a specified branch """
    trk_mask = (branch[str(treename)]['sid']==sid)
    values = branch[str(treename)].mask[(trk_mask)]
    return values
    
  def SingleTrkCut(self, branch, treename, leaf, minv, maxv, surface_id=0):
    """ apply a single cut as a mask on the chosen branch leaf """
    mask_max = (branch[str(treename)][str(leaf)]< maxv)
    mask_min = (branch[str(treename)][str(leaf)]> minv)
    trk_mask = (branch[str(treename)]['sid']==0)
    values = branch[str(treename)].mask[(mask_min) & (mask_max) & trk_mask ]
    return values
    
  def ApplyTrkCutList(self, branch, treenames, leafs, minvs, maxvs, surface_id=0):
    """ apply a list of cuts at trk level """
    pass
    
  def TrkCrvCoincsCut(self, trk, crv, tmin, tmax):
    """ simple function to remove anything close to a crv coinc """
    pass


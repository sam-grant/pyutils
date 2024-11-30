#! /usr/bin/env python
import uproot
import awkward as ak

class Import:
  """ class to help users import a trkana tree and branch """
  def __init__(self, filename, dirname="EventNtuple", treename="ntuple"):
    self.filename= filename
    self.dirname = dirname
    self.treename = treename
    
  def ImportTreeFromFileList(self, path, branchname): 
    """ Import list of files from a text file and merge a specific branch"""
    with open(path, "r") as file_list_: # Open file
      filelist = file_list_.readlines() # Read file
      # Remove leading/trailing whitespace
      filelist = [line.strip() for line in filelist]
    print("file list", filelist)
    # Concatenate the TTrees named "mytree" from each file
    merged = uproot.concatenate([f"{file}:"+str(self.dirname)+"/"+str(self.treename)+"/"+str(branchname) for file in filelist])
    return merged

  def ImportFileListFromSAM(self):
    """ import list of files """
    #TODO
    pass

  def ImportTree(self):
    """ import root tree """
    input_file = uproot.open(self.filename)
    input_tree = input_file[self.dirname][self.treename]
    return input_tree
    
  def ImportBranches(self, tree, branchnames):
    """ import list of branches from trkana"""
    list_names = []
    for i, branchname  in enumerate(branchnames):
        list_names.append("/"+str(branchname)+"/")
    branches = tree.arrays(filter_name=list_names, library='ak')
    return branches

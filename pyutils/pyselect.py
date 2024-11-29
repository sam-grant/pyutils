#! /usr/bin/env python
import uproot
import awkward as ak

class Select:
  def __init__(self):
    """  Placeholder init """
    pass 
  
  def isDeM(self):
    """ checks if trk is a downstream e- """
    pass
  
  def isDeP(self):
    """ checks if trk is downstream e+ """
    pass
       
  def SelectSurfaceIDAll(self, branch, treename, sid=0):
    """ allows user to see trk fits only on chosen surface but retains all branch (trksegs trksegsmc) """
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
    
  def MultiTrkCut(self, branch, treenames, leaves, minvs, maxvs, surface_id=0):
    """ apply a list of cuts at trk level """
    mask_list = ""
    trk_mask = (branch['trksegs']['sid']==surface_id)
    #for i, tree in enumerate(treenames):
    i=0
    tree=treenames[i]
    print(i, tree, leaves[i], minvs[i], maxvs[i])
    mask_max = (branch[str(tree)][str(leaves[i])]< maxvs[i])
    mask_min = (branch[str(tree)][str(leaves[i])]> minvs[i])
    mask_list+=str(mask_min)+" & "+str(mask_max)+" & "
    print(mask_list)
    values = branch.mask[ mask_min & mask_max & trk_mask  ]
    return values
    
  def TrkCrvCoincsCut(self, trk, crv, tmin, tmax):
    """ simple function to remove anything close to a crv coinc """
    pass

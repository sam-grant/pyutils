#! /usr/bin/env python
import uproot
import awkward as ak
import numpy as np

class Event:
  def __init__(self, trk, trksegs, trkpars, trkhits=None, crvcoins=None):
    """  Placeholder init """
    self.trk = trk
    self.trkpars = trkpars
    self.trksegs = trksegs
    self.trkhits = trkhits
    self.crvcoin = crvcoins
    #TODO - use or remove?
    
class Select:
  def __init__(self):
    """  Placeholder init """
    pass

  def isElec(self, branch):
    """ checks if trk is a  e- """
    trk_mask = (branch['trk.pdg']==11)
    return trk_mask
  
  def isPos(self, branch):
    """ checks if trk is  e+ """
    trk_mask = (branch['trk']['pdg']==-11)
    return trk_mask
    
  def isDown(self, trksegs):
    """ checks if track is down stream going """
    trk_mask = (trksegs['trksegs']['mom']["fCoordinates"]["fZ"]>0)
    return trk_mask
    
  def hasTrkCrvCoincs(self, trks, crvs, tmax): #FIXME we need only trker times
    """ simple function to remove anything close to a crv coinc """
    has_coin = np.ones(ak.num(trks, axis=0), dtype=bool)
    for i_evt, evt in enumerate(trks['trksegs']['time']):
        for i_trk, trk in enumerate(evt):
            if ak.num(ak.drop_none(trk), axis = 0) > 0:
                for i_crv, crv in enumerate(crvs['crvcoincs.time'][ i_evt]):
                    print(i_evt, i_trk, i_crv, "trk inside", trk)
                    if np.abs(trk[0] - crv) < tmax: #FIXME - is [0] OK?
                        has_coin[i_evt] = False
    return has_coin
    
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
    trk_mask = (branch[str(treename)]['sid']==0) #FIXME return just the mask
    values = branch[str(treename)].mask[(mask_min) & (mask_max) & trk_mask ]
    return values
 
  def MultiTrkCut(self, branch, treenames, leaves, minvs, maxvs):
    """ apply a list of cuts at trk level """ # FIXME
    mask_list = ""
    for i, tree in enumerate(treenames):
      print(i, tree, leaves[i], minvs[i], maxvs[i])
      print(branch[str(tree)])
      mask_max = (branch[str(tree)][str(leaves[i])]< maxvs[i])
      mask_min = (branch[str(tree)][str(leaves[i])]> minvs[i])
      mask_list.append(mask_max)
      mask_list.append(mask_min)
    return mask_list # returns just the mask
    


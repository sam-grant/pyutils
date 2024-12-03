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

  def isElectron(self, ntuple):
    """ checks if trk is a  e- """
    trks = ntuple["trk"] 
    branch = trks.arrays(library='ak')
    trk_mask = (branch['trk.pdg']==11)
    return trk_mask
  
  def isPositron(self, ntuple):
    """ checks if trk is  e+ """
    trks = ntuple["trk"] 
    branch = trks.arrays(library='ak')
    trk_mask = (branch['trk.pdg']==-11)
    return trk_mask
    
  def isMuonPlus(self, ntuple):
    """ checks if trk is a  mu- """
    trks = ntuple["trk"] 
    branch = trks.arrays(library='ak')
    trk_mask = (branch['trk.pdg']==-13)
    return trk_mask
  
  def isMuonMinus(self, branch):
    """ checks if trk is  mu+ """
    trks = ntuple["trk"] 
    branch = trks.arrays(library='ak')
    trk_mask = (branch['trk.pdg']==13)
    return trk_mask
    
  def isDownstream(self, trksegs):
    """ checks if trackseg is downstream going """
    trk_mask = (trksegs['trksegs']['mom']["fCoordinates"]["fZ"] > 0)
    return trk_mask
  
  def isUpstream(self, trksegs):
    """ checks if trackseg is upstream going """
    trk_mask = (trksegs['trksegs']['mom']["fCoordinates"]["fZ"] < 0)
    return trk_mask
    
  def SelectSurfaceID(self, branch, treename, sid=0):
    """ allows user to see trk fits only on chosen surface chooses a specified branch """
    trk_mask = (branch[str(treename)]['sid']==sid)
    values = branch[str(treename)].mask[(trk_mask)]
    return values
    
  def IsReflected(self, trksegs):
    """ A track is a reflected track if we have both an upstream and a downstream segment at the tracker entrance """
    hasupstream = False
    hasdownstream = False
    hasboth = False
    # TODO look at TrkEnt, if more than once, loop the see if up and down stream
    return hasboth
    
  def SelectTrkQual(self, tree, value):
    """ select trks of this quality """
    trkqual = tree["trkqual"] 
    mytrkqual = trkqual.arrays(library='ak')
    mask = (mytrkqual['trkqual.result'] > value)
    return mask
   
  def SelectHits(self, ntuple, value):
    """ select the number of active hits in fit """
    trks = ntuple["trk"] 
    branch = trks.arrays(library='ak')
    trk_mask = (branch['trk.nactive'] > value)
    return trk_mask
   
  def hasTrkCrvCoincs(self, trks, ntuple, tmax):
    """ simple function to remove anything close to a crv coinc """
    crvst = ntuple["crvcoincs"]
    crvs = crvst.arrays(library='ak')
    has_coin = np.ones(ak.num(trks, axis=0), dtype=bool)
    for i_evt, evt in enumerate(trks['trksegs']['time']):
        for i_trk, trk in enumerate(evt):
            if ak.num(ak.drop_none(trk), axis = 0) > 0:
                for i_crv, crv in enumerate(crvs['crvcoincs.time'][ i_evt]):

                    if np.abs(trk[0] - crv) < tmax:
                        has_coin[i_evt] = False
    return has_coin

  def MakeMask(self, branch, treename, leaf, eql, v1, v2=None):
    """ makes a mask for the chosen branch/leaf v1 = min, v2 = max, use eql if you want it == v1"""
    mask=""
    if eql == True:
      mask = (branch[str(treename)][str(leaf)]==v1)
    else:
      mask = (branch[str(treename)][str(leaf)] >  v1) & (branch[str(treename)][str(leaf)] < v2)
    return mask
  
  def MakeMaskList(self, branch, treenames, leaves, eqs, v1s, v2s):
    """ makes a mask for the chosen branch/leaf v1 = min, v2 = max, use eql if you want it == v1"""
    mask_list=[]
    print(treenames,leaves,eqs,v1s,v2s)
    for i, tree in enumerate(treenames):
      print(treenames[i],leaves[i],eqs[i],v1s[i],v2s[i])
      mask = ""
      if eqs[i] == True:
        mask = (branch[str(treenames[i])][str(leaves[i])] == v1s[i])
        print(i, mask)
      else:
        mask = (branch[str(treenames[i])][str(leaves[i])] >  v1s[i]) & (branch[str(treenames[i])][str(leaves[i])] < v2s[i])
        print(i, mask)
      mask_list.append(mask)
    return mask_list

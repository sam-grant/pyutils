#! /usr/bin/env python
import pyimport as evn
import pyvector as vec
import pyplot as plot
import pyprint as prnt
from pyselect import Select as slct
from pyselect import Event as evt
import awkward as ak
def main():
  """ simple test function to run some of the utils """

  # import the files
  myevn = evn.Import("/exp/mu2e/data/users/sophie/ensembles/MDS1/MDS1av0.root", "EventNtuple", "ntuple")

  # import code and extract branch
  ntuple = myevn.ImportTree()
  
  # make a pyselect object
  mysel = slct()
  
  # check if fit is for an elec
  trks = ntuple["trk"] 
  mytrks = trks.arrays(library='ak')
 
  # import branches associated with trk fits
  trksegs = myevn.ImportBranches(ntuple,['trksegs','trksegpars_lh','trkhits'])
  
  # check if it is an electron going downstream
  is_elec = mysel.isElectron(mytrks)
  is_down = mysel.isDownstrem(trksegs)
  
  # check trk quality
  trkqual_mask = mysel.SelectTrkQual(ntuple, 0.2)

  # check for crv coincidences 
  crvs = ntuple["crvcoincs"]
  mycrvs = crvs.arrays(library='ak')
  crv_mask = mysel.hasTrkCrvCoincs( trksegs, mycrvs, 150)
  
  # set of trkseg cuts
  treenames = [ 'trksegs', 'trksegs', 'trksegpars_lh', 'trksegpars_lh', 'trksegpars_lh', 'trksegpars_lh']
  leaves = [ 'sid', 'time', 't0err','maxr','tanDip','d0']
  equals = [True, False, False, False, False, False]
  v1s = [0, 640, 0, 450, 0.5, -100]
  v2s = [None, 1650, 0.9, 680, 1.0, 100]
  
  trkseg_mask_list = mysel.MakeMaskList(trksegs, treenames, leaves, equals, v1s, v2s)
  
  # apply joint mask --> can we make this tidier?
  mytrksegs = trksegs['trksegs'].mask[(is_elec) & (is_down) & (trkqual_mask) & (crv_mask) & (trkseg_mask_list[0]) & (trkseg_mask_list[1]) &  (trkseg_mask_list[2]) & (trkseg_mask_list[3]) & (trkseg_mask_list[4]) & (trkseg_mask_list[5]) ]
  
  # make some plots to compare before/after cuts
  myhist = plot.Plot()
  
  # plot time before and after cuts:
  flatarraytime = ak.flatten(trksegs['trksegs']['time'], axis=None)
  flatarraycut = ak.flatten(mytrksegs['time'], axis=None)
  dictarrays = { "no cut" : flatarraytime, "with cut" : flatarraycut }
  myhist.Plot1DOverlay(dictarrays, 100, 450, 1695, "Mu2e Example", "fit time at Trk Ent [ns]", "#events per bin", 'timecut.pdf', 'best', 300,False, True, True)
  
  # plot the momentum before and after the cuts
  myvect = vec.Vector()
  electrksegs = trksegs['trksegs'].mask[(is_elec) & (is_down)]
  vector_all = myvect.GetVectorXYZFromLeaf(electrksegs, 'mom')
  magnitude_all = myvect.Mag(vector_all)
  
  vector_cut = myvect.GetVectorXYZFromLeaf(mytrksegs, 'mom')
  magnitude_cut = myvect.Mag(vector_cut)
  
  flatarraymom_all = ak.flatten(magnitude_all, axis=None)
  flatarraymom_cut = ak.flatten(magnitude_cut, axis=None)
  
  myhist.Plot1D(flatarraymom_cut  , None, 100, 95, 115, "Mu2e Example", "fit mom at Trk Ent [MeV/c]", "#events per bin", 'black', 'best', 'momcut.pdf', 300, True, False, True, False, True, True, True)
  
  dictarrays = { "all dem" : flatarraymom_all, "dem + trkcuts" : flatarraymom_cut }
  myhist.Plot1DOverlay(dictarrays, 100, 95,115, "Mu2e Example", "fit mom at Trk Ent [ns]", "#events per bin", 'momcutcompare.pdf', 'best', 300,False, True, True)
  
if __name__ == "__main__":
    main()

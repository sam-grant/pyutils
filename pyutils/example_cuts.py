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
  test_evn = evn.Import("/exp/mu2e/data/users/sophie/ensembles/MDS1/MDS1a.root", "EventNtuple", "ntuple")

  # import code and extract branch
  ntuple = test_evn.ImportTree()


  # make a pyselect object
  mysel = slct()
  
  # check if fit is for an elec
  trks = ntuple["trk"] 
  mytrks = trks.arrays(library='ak')
 
  # check if it is an electron
  is_elec = mysel.isElec(mytrks)
  
  # import branches associated with trk fits
  trksegs = test_evn.ImportBranches(ntuple,['trksegs','trksegpars_lh','trkhits'])
    
  # print out the first 10 events:
  myprnt = prnt.Print()
  myprnt.PrintNEvents(trksegs,10)
  
  # check if fit is going down stream
  is_down = mysel.isDown(trksegs)

  # is trk entrance
  trkent_mask = (trksegs['trksegs']['sid']==0)
  
  # is in time
  trksegs_mask = (trksegs['trksegs']['time'] > 640) & (trksegs['trksegs']['time'] < 1650)
  
  # check trk pars
  trkpars_mask = (trksegs['trksegpars_lh']['t0err'] < 0.9) & (trksegs['trksegpars_lh']['maxr'] < 680) & (trksegs['trksegpars_lh']['maxr'] > 450) 
  
  # these are deprecated cuts
  oldtrkpar_mask = (trksegs['trksegpars_lh']['tanDip'] > 0.5) & (trksegs['trksegpars_lh']['tanDip'] < 1.0) & (trksegs['trksegpars_lh']['d0'] > -100) & (trksegs['trksegpars_lh']['d0'] < 100)
  
  # check trk quality
  trkqual = ntuple["trkqual"] 
  mytrkqual = trkqual.arrays(library='ak')
  trkqual_mask = (mytrkqual['trkqual.result']> 0.2)
  
  # check for crv coincidences 
  crvs = ntuple["crvcoincs"]
  mycrvs = crvs.arrays(library='ak')
  crv_mask = mysel.hasTrkCrvCoincs( trksegs, mycrvs, 150)
  
  # apply joint mask
  mytrksegs = trksegs.mask[(is_elec) & (is_down) & (trkent_mask)  & (trksegs_mask) & (trkqual_mask) & (trkpars_mask) & crv_mask & oldtrkpar_mask]
  
  # print out the first 10 events:
  myprnt.PrintNEvents(mytrksegs,10)
  
  # plot the momentum before and after the cuts
  myvect = vec.Vector()
  trkentall = mysel.SelectSurfaceIDAll(trksegs, 'trksegs', 0)
  electrksegs = trkentall.mask[(is_elec) & (is_down)]
  vector_all = myvect.GetVectorXYZ(electrksegs, 'trksegs', 'mom')
  magnitude_all = myvect.Mag(vector_all)
  
  vector_cut = myvect.GetVectorXYZ(mytrksegs, 'trksegs', 'mom')
  magnitude_cut = myvect.Mag(vector_cut)
  
  myhist = plot.Plot()
  flatarraymom_all = ak.flatten(magnitude_all, axis=None)
  flatarraymom_cut = ak.flatten(magnitude_cut, axis=None)
  
  myhist.Plot1D(flatarraymom_cut  , None, 100, 100, 115, "Mu2e Example", "fit mom at Trk Ent [MeV/c]", "#events per bin", 'black', 'best', 'momcut.pdf', 300, True, False, True, False, True, True, True)
  
  dictarrays = { "all dem" : flatarraymom_all, "dem + trkcuts" : flatarraymom_cut }
  myhist.Plot1DOverlay(dictarrays, 100, 95,115, "Mu2e Example", "fit mom at Trk Ent [ns]", "#events per bin", 'momcutcompare.pdf', 'best', 300,False, True, True)


  
if __name__ == "__main__":
    main()

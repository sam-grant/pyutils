# Import external packages
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
# Import the Procssor class
from pyutils.pyprocess import Processor 
from pyutils.pymcutil import MC
from pyselect import Select
from pyutils.pyvector import Vector

def main():
  # Initialise the Importer with increased verbosity 
  # verbosity=0 will only show errors
  processor = Processor(verbosity=2)

  # Define the path to our example file
  file_name = "/pnfs/mu2e/tape/phy-nts/nts/mu2e/MDS2ac-OnSpillTriggered/MDC2020aw_perfect_v1_3/root/8c/0b/nts.mu2e.MDS2ac-OnSpillTriggered.MDC2020aw_perfect_v1_3.0.root"

  # Define the branches we want to access
  # For a complete list of available branches, see:
  # https://github.com/Mu2e/EventNtuple/blob/main/doc/branches.md
  # Also refer to ntuplehelper, available after mu2e setup EventNtuple
  branches = ["trksegs"]

  # Import the branches from the file
  # This loads the data into memory and returns an awkward array
  data = processor.process_data(
      file_name=file_name,
      branches=branches
  )
  
  selector = Select()
  
  trk_opa = selector.select_surface(data, surface_name="OPA")
  trkfit_opa = data.mask[(trk_opa)]['trksegs']
  vector = Vector()
  mom_mag_opa = vector.get_mag(trkfit_opa ,'mom')
  mom_mag_opa = ak.nan_to_none(mom_mag_opa)
  mom_mag_opa = ak.drop_none(mom_mag_opa)
  print("has opa", len(mom_mag_opa))
  mom_mag_opa = np.array(ak.flatten(mom_mag_opa , axis=None))
  n,bins,patch = plt.hist(mom_mag_opa , color='green',range=(0.,300.),alpha=0.5, bins=50, histtype='step', label = 'OPA')
  
  trk_st = selector.select_surface(data, surface_name="ST_Foils")
  trkfit_st = data.mask[(trk_st)]['trksegs']
  vector = Vector()
  mom_mag_st = vector.get_mag(trkfit_st ,'mom')
  mom_mag_st = ak.nan_to_none(mom_mag_st)
  mom_mag_st = ak.drop_none(mom_mag_st)
  print("has st", len(mom_mag_st))
  mom_mag_st = np.array(ak.flatten(mom_mag_st , axis=None))
  n,bins,patch = plt.hist(mom_mag_st , color='red',range=(0.,300.),alpha=0.5, bins=50, histtype='step', label = 'ST')
  
  trk_front = selector.select_surface(data, surface_name="TT_Front")
  trkfit_ent = data.mask[(trk_front)]['trksegs']
  vector = Vector()
  mom_mag_ttfront = vector.get_mag(trkfit_ent ,'mom')
  mom_mag_ttfront = ak.nan_to_none(mom_mag_ttfront)
  mom_mag_ttfront = ak.drop_none(mom_mag_ttfront)
  print("has tt front", len(mom_mag_ttfront))
  mom_mag_ttfront  = np.array(ak.flatten(mom_mag_ttfront , axis=None))
  n,bins,patch = plt.hist(mom_mag_ttfront , color='blue',range=(0.,300.),alpha=0.5, bins=50, histtype='step', label = 'TTFront')
  
  plt.legend()
  plt.yscale('log')
  plt.show()
  
if __name__ == "__main__":
    main()

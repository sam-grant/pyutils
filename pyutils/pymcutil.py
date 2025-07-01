import numpy as np
import awkward as ak

class MC:
    """Utility class for importing mc information for use in analysis
    """
    
    def __init__(self, data):
        """Initialise the importer
        
        Args:
            data : array in format produced from processing
        """
        self.particle_count_return
        self.print_prefix = "[pymcutil] "
        
      print(f"{self.print_prefix}Initialised")
      
    def count_particle_types(self, data):
      """
      Counts the occurrences of different particle types based on
      simulation data, leveraging the properties of Awkward Arrays.

      Args:
          data (ak.Array): An Awkward Array containing simulation data,
                           including ''trkmcsim' nested field.

      Returns:
          list: A list containing particle type identifiers for each event.
      """

      # Check for empty data
      if ak.num(data, axis=0) == 0:
          print("No events found in the data.")
          return []

      # Vectorized approach for efficiency using Awkward Array operations
      #  This is generally faster than looping through events individually for large datasets.

      # Get startCode for the first track in each event, handling empty lists
      # Use ak.firsts to safely get the first element or None if the list is empty
      proc_codes = ak.firsts(data['trkmcsim', 'startCode'], axis=1) 
      gen_codes = ak.firsts(data['trkmcsim', 'gen'], axis=1) 

      # Use vectorized comparisons and selection for counting
      dio_mask = (proc_codes == 166)  # Create boolean mask for DIO events
      ce_mask = (proc_codes == 168)   # Create boolean mask for CE events
      erpc_mask = (proc_codes == 178)  # Create boolean mask for external RPC events
      irpc_mask = (proc_codes == 179)  # Create boolean mask for internal RPC events
      cosmic_mask = ((gen_codes == 44) | (gen_codes == 38))  # Create boolean mask for cosmic events

      # Combine masks to identify 'other' events
      other_mask = ~(dio_mask | ce_mask | erpc_mask | irpc_mask | cosmic_mask)

      # Initialize particle_count with -2 for 'others'
      particle_count = ak.zeros_like(proc_codes, dtype=int) - 2
      
      # Assign particle types based on masks
      particle_count = ak.where(dio_mask, 166, particle_count)
      particle_count = ak.where(cosmic_mask, -1, particle_count)
      particle_count = ak.where(other_mask, -2, particle_count)
      particle_count = ak.where(irpc_mask, 179, particle_count)
      particle_count = ak.where(erpc_mask, 178, particle_count)
      particle_count = ak.where(ce_mask, 168, particle_count)
      self.particle_count_return = particle_count
      #particle_count = ak.any(dio_mask, axis=1)
      # Count the occurrences of each particle type
      counts = {
          166: (len(particle_count[ak.any(dio_mask, axis=1)==True])),
          168:  (len(particle_count[ak.any(ce_mask, axis=1)==True])),
          178:  (len(particle_count[ak.any(erpc_mask, axis=1)==True])),
          179:  (len(particle_count[ak.any(irpc_mask, axis=1)==True])), 
          -1:  (len(particle_count[ak.any(cosmic_mask, axis=1)==True])),
          -2:  (len(particle_count[ak.any(other_mask, axis=1)==True])),
      }
        
      # Print the yields to terminal for cross-check
      print("===== MC truth yields for full momentum and time range=====")
      print("N_DIO: ", counts[166])
      print("N_CE: ", counts[168])
      print("N_eRPC: ", counts[178])
      print("N_iRPC: ", counts[179])
      print("N_cosmic: ", counts[-1])
      print("N_others: ", counts[-2])
      
      # Now return a 1D list with one element per event corresponding to the primary trk
      #self.particle_count_return = ak.flatten(self.particle_count_return, axis=None)
      #    The mask will be True for values that are not -2.
      primary_mask = self.particle_count_return != -2

      # Apply the mask to the flattened array to select desired elements
      self.particle_count_return = self.particle_count_return[primary_mask]
      self.particle_count_return = [[sublist[0]] for sublist in self.particle_count_return]
      self.particle_count_return = ak.flatten(self.particle_count_return, axis=None)
      print("returned particle count length",len(self.particle_count_return))
      
      return self.particle_count_return
        

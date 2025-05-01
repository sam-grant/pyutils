#! /usr/bin/env python
import uproot
import awkward as ak
import numpy as np
    
class Select:
    """
    Class for standard selection cuts with EventNtuple data in Awkward format
    
    """
    def __init__(self, verbosity=1):
        """Initialise the selector
        
            Args: 
                verbosity (int, optional): Print detail level (0: minimal, 1: medium, 2: maximum). Defaults to 1. 
        """
        # Add verbosity 
        self.verbosity = verbosity 
        # Printout prefix
        self.print_prefix = "[pyselect] " 
        # PDG ID dict
        self.particles = { 
            "e-" : 11,
            "e+" : -11,
            "mu-" : 13,
            "mu+" : -13
        }
        if self.verbosity > 0:
            print(f"{self.print_prefix}Initialised Select with verbosity = {self.verbosity}")

    def is_electron(self, data):
        """ Return boolean array for electron tracks which can be used as a mask 

            Args:
                data (awkward.Array): Input array containing the "trk" branch
        """
        # Construct mask
        mask = (data["trk.pdg"] == self.particles["e-"])

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for e- tracks") 
            
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_electron(): {e}") from e
            
    def is_positron(self, data):
        """ Return boolean array for positron tracks which can be used as a mask 

            Args:
                data (awkward.Array): Input array containing the "trk" branch
        """
        # Construct mask
        mask = (data["trk.pdg"] == self.particles["e+"])

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for e+ tracks") 
            
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_positron(): {e}") from e

    def is_mu_minus(self, data):
        """ Return boolean array for negative muon tracks which can be used as a mask 

            Args:
                data (awkward.Array): Input array containing the "trk" branch
        """
        # Construct mask
        mask = (data["trk.pdg"] == self.particles["mu-"])

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for mu- tracks") 
            
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_mu_minus(): {e}") from e

    def is_mu_plus(self, data):
        """ Return boolean array for positive muon tracks which can be used as a mask 

            Args:
                data (awkward.Array): Input array containing the "trk" branch
        """
        # Construct mask
        mask = (data["trk.pdg"] == self.particles["mu+"])

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for mu+ tracks") 

        # Try to return mask
        try:
            return mask 
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_mu_plus(): {e}") from e

    # More general function for particle selection
    def is_particle(self, data, particle):
        """ Return boolean array for tracks of a specific particle type which can be used as a mask 

            Args:
                data (awkward.Array): Input array containing the "trk" branch
                particle (string): particle type, 'e-', 'e+', 'mu-', or 'mu+'
        """
        # "trk" is not the only branch that uses pdgIDs, crvcoincsmc is another, how to handle that? 
        # Construct mask
        mask = (data["trk.pdg"] == self.particles[particle])

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for {particle} tracks") 
        
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_particle(): {e}") from e
            
    def is_downstream(self, data, branch_name="trksegs"):
        """ Return boolean array for upstream track segments

            Args:
                data (awkward.Array): Input array containing the segments branch
                branch_name (str, optional): Name of the segments branch for backwards compatibility. Defaults to 'trksegs'
        """
        # Construct mask
        mask = (data[branch_name]["mom"]["fCoordinates"]["fZ"] > 0)
        
        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for downstream track segments (p_z > 0)")
            
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_downstream(): {e}") from e

    def is_upstream(self, data, branch_name="trksegs"):
        """ Return boolean array for downstream track segments 

            Args:
                data (awkward.Array): Input array containing the segments branch
                branch_name (str, optional): Name of the segments branch for backwards compatibility. Defaults to 'trksegs'
        """
        # Construct mask
        mask = (data["trksegs"]["mom"]["fCoordinates"]["fZ"] < 0)

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for upstream track segments (p_z < 0)")
            
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_upstream(): {e}") from e

    def select_surface(self, data, sid, sindex=0, branch_name="trksegs"):
        """ Return boolean array for track segments intersecting a specific surface 
        
        Args:
            data (awkward.Array): Input array containing segments branch
            sid (int): ID of the intersected surface 
            sindex (int, optional): Index to the intersected surface (for multi-surface elements). Defaults to 0. 
            branch_name (str, optional): Name of the segments branch for backwards compatibility. Defaults to 'trksegs'
        """
        # Construct mask
        mask = (data[branch_name]['sid']==sid) & (data[branch_name]['sindex']==sindex) 
        
        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for {branch_name} with sid = {sid} and sindex = {sindex}")

        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in select_surface(): {e}") from e
        

    def is_reflected(self, data, branch_name="trksegs"):
        """ Return boolean array for reflected tracks  
        
        Reflected tracks have both upstream and downstream segments at the tracker entrance 
        
        Args:
            data (awkward.Array): Input array containing segments branch
            branch_name (str, optional): Name of the segments branch for backwards compatibility. Defaults to 'trksegs'
        """

        # Construct track segment conditions
        trkent = self.is_surface(data, sid=0, branch_name=branch_name)
        upstream = self.is_upstream(data, branch_name=branch_name)
        downstream = self.is_downstream(data, branch_name=branch_name)

        # Construct condition for reflected tracks 
        # Does the track have any segments with p_z > 0 at the tracker entrance 
        # AND at any segments with p_z < 0 at the tracker entrance?
        reflected = (ak.any((upstream & trkent), axis=-1) & ak.any((downstream & trkent), axis=-1))

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for reflected tracks")
            
        # Try to return mask
        try:
            return reflected
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in is_reflected(): {e}") from e

    
    def select_trkqual(self, data, quality):
        """ Return boolean array for tracks above a specified quality   

        Args: 
            data (awkward.Array): Input array containing the trkqual.result branch
            quality (float): The numerical output of the MVA

        """
        # Construct mask
        mask = (data["trkqual.result"] > quality)

        if self.verbosity > 0: 
            print(f"{self.print_prefix}Returning mask for trkqual > {quality}")

        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in select_trkqual(): {e}") from e
   
    def has_n_hits(self, data, nhits):
        """ Return boolean array for tracks with hits above a specified value 

        Hits in this context is nactive planes

        Args: 
            data (awkward.Array): Input array containing the trk.nactive branch
            nhits (int): The minimum number of track hits 

        """
        # Construct mask
        # Why nactive and not nhits?
        mask = (data["trk.nactive"] >= nhits)
        
        # Try to return mask
        try:
            return mask
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌ Exception in select_trkqual(): {e}") from e

    def hasTrkCrvCoincs(self, trks, ntuple, tmax):
        """ simple function to remove anything close to a crv coinc """

        # Looping through events like this is pretty inefficient 
        # Can we do it with array operations? 
        # Can we explain a bit more about what this does?
        
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

        # Can we explain a bit more about what this does?
        
        mask=""
        if eql == True:
            mask = (branch[str(treename)][str(leaf)]==v1)
        else:
            mask = (branch[str(treename)][str(leaf)] >  v1) & (branch[str(treename)][str(leaf)] < v2)
        return mask

    def MakeMaskList(self, branch, treenames, leaves, eqs, v1s, v2s):
        """ makes a mask for the chosen branch/leaf v1 = min, v2 = max, use eql if you want it == v1"""

        # Can we explain a bit more about what this does?
        
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
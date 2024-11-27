import uproot
import awkward as ak
import math
import numpy as np
import vector

class Vector:
  
  def __init__(self):
    """  Placeholder init """ 
    pass  
    
  def GetVectorXYZ(self, branch, leafname, vectorreq, sid=0):
    """ 
    imports a XYZ vector branch e.g. mom and turns it into something which can use funcitons are found in:
    https://vector.readthedocs.io/en/latest/api/vector._methods.html 
    """

    # register the vector class
    vector.register_awkward()

    # take the chosen position to evaluate (nominally entrance)
    trk_ent_mask = (branch[str(leafname)]['sid']==sid)

    # apply mask
    trkent = branch[(trk_ent_mask)]

    # make the Vector 3D TODO - protect against str(leafname)  doesnt exist error
    trkvect3D = ak.zip({
        "x": trkent[str(leafname)][str(vectorreq)]["fCoordinates"]["fX"],
        "y": trkent[str(leafname)][str(vectorreq)]["fCoordinates"]["fY"],
        "z": trkent[str(leafname)][str(vectorreq)]["fCoordinates"]["fZ"],
    }, with_name="Vector3D")
    
    return trkvect3D
  
  def Mag(self, vector):
    #TODO
    return 0
    
  def Angle(self, vector):
    #TODO
    return 0

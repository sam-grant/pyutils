from pyutils.pylogger import Logger
import subprocess


class Display:
    """
    Class for executing the EventDisplay
    
    Note:
      For this to work:
      * mu2einit
      * muse setup
      * assumes local copy of EventDisplay via clone or musing
    """
    def __init__(self, verbosity=1):
      # Start logger
      self.logger = Logger( 
          print_prefix = "[pydisplay]", 
          verbosity = verbosity
      )
    
    def pick_event(self, dataset, run, subrun, event):
      """ use pickEvent tool to extract event, run, subrun from given data set """
      result = subprocess.run(['pickEvent', '-e','-v',str(dataset),' ',str(run)+'/'+str(subrun)+'/'+str(event)], capture_output=True, text=True)
      print(result.stdout)
    
    def launch_display(self, dataset, run, subrun, event):
      """ launches the mu2e event display 
      """
      launch_display = subprocess.run(['mu2e','-c','EventDisplay/examples/nominal_example.fcl', str(dataset)+'_'+str(run)+'_'+str(subrun)+'_'+str(event)+'.art'], capture_output=True, text=True)
      print(launch_display.stdout)

    

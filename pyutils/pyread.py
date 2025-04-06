import uproot
import subprocess

class Reader:
    """Unified interface for accessing files, either locally or remotely"""
    
    def __init__(self, use_remote=False, verbosity=2):
        """Initialise the reader
        
        Args:
            use_remote: Whether to use remote access methods
            verbose: Whether to print detailed information
        """
        self.use_remote = use_remote # access files from outside NFS
        self.verbosity = verbosity 
        self.print_prefix = "[pyread] "

    def read_file(self, filepath):
        """Read a file using the appropriate method
        
        Args:
            filepath: Path to the file
            
        Returns:
            Uproot file object
        """
        if self.use_remote:
            return self._read_remote_file(filepath)
        else:
            return self._read_local_file(filepath)
    
    def _read_local_file(self, filepath):
        """Open a local file directly"""
        try: 
            file = uproot.open(filepath)
            if self.verbosity > 0:
                print(f"{self.print_prefix}✅  Opened {filepath}")
            return file
        except Exception as e:
            raise Exception(f"{self.print_prefix}❌  Exception while opening {filepath}: {e}") from e
    
    def _read_remote_file(self, filepath):
        """Open a file from /pnfs via xroot"""
        if self.verbosity > 1:
            print(f"{self.print_prefix}Opening remote file: {filepath}")
        
        try:
            # Setup commands to generate xroot URL
            commands = 'source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh; muse setup ops;'
            commands += f'echo {filepath} | mdh print-url -s root -'
            # Execute commands
            xroot_url = subprocess.check_output(commands, shell=True, universal_newlines=True).strip()
            if self.verbosity > 1:
                print(f"{self.print_prefix}Created xroot URL: {xroot_url}")
            # Open the file using the xroot URL
            return self._read_local_file(xroot_url)
            # return uproot.open(xroot_url)
            
        except Exception as e1:
            # If there's an error, try copying to local and opening
            print(f"{self.print_prefix}❌  Exception while opening {filepath}: {e1}")
            print(f"{self.print_prefix}Retrying with local copy...")

            try:
                commands = 'source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh; muse setup ops;'
                commands += f'echo {filepath} | mdh copy-file -s tape -l local -'
                
                # Execute the copy command
                subprocess.check_output(commands, shell=True, universal_newlines=True)
                
                # Open the file directly after copying
                return self._read_local_file(filepath)
            
            except Exception as e2:
                raise Exception(f"{self.print_prefix}❌  Failed to open local copy: {e2}") from e2
import uproot
import awkward as ak
from pyread import Reader
from pyprocess import Processor

class Importer:
    """High-level interface for importing branches from files and datasets"""
    
    def __init__(self, dir_name="EventNtuple", tree_name="ntuple", verbosity=1):
        """Initialise the importer
        
        Args:
            verbosity: Print detail level (0: minimal, 1: medium, 2: maximum) 
        """
        self.dir_name = dir_name
        self.tree_name = tree_name
        self.verbosity = verbosity 
        
        # Create reader and processor only when needed
        self.reader = None
        self.processor = None
        
        # Print prefix
        self.print_prefix = "[pyimport] "

        print(f"{self.print_prefix}Initialised with path '{dir_name}/{tree_name}' and verbosity={self.verbosity}") 
        
    def _get_array(self, file_name, branches=None, quiet=False):
    
        """Process file and extract specified branches
        
            This is the core function that actually extracts the data
        """
    
        try:
            # Open the file
            file = self.reader.read_file(file_name)
            
            # Access the tree
            if self.dir_name in file and self.tree_name in file[self.dir_name]:
                # Get tree
                tree = file[self.dir_name][self.tree_name]
                # Print tree info 
                if self.verbosity > 1 and not quiet:
                    print(f"{self.print_prefix} Accessing branches in tree:")
                    tree.show(filter_name=branches, interpretation_width=100)
                
                # Get array for specifed branches 
                result = {}

                if branches is None: 
                    print(f"{self.print_prefix}❌  Please provide a list of branches, or branches='*' to import all") 
                    return None
        
                # Flat list
                elif isinstance(branches, list):
                    result = tree.arrays(filter_name=branches, library="ak")
        
                # Grouped dictionary
                elif isinstance(branches, dict):
                    data = {}
                    # Get arrays per field/group
                    for group, sub_branches in branches.items():
                        data[group] = tree.arrays(filter_name=sub_branches, library="ak")
                    # Zip them together 
                    result = ak.zip(data) 
        
                # If using "*" get all branches
                elif branches == "*":
                    branches = [branch for branch in tree.keys()] 
                    if self.verbosity > 0:
                        print(f"{self.print_prefix} Importing all branches")
                    # Return array 
                    result = tree.arrays(filter_name=branches, library="ak")
                    
                else: 
                    print(f"{self.print_prefix}❌ Branches type {branches.type} not recognised") 
                    return None

                # Close file
                file.close()
                # Return
                return result
                
            else:
                print(f"{self.print_prefix}❌  Could not find tree {self.dir_name}/{self.tree_name} in file {file_name}")
                return None
    
        except Exception as e:
            print(f"{self.print_prefix}❌  Error getting branches in file {file_name}: {e}")
            return None
    
    def import_file(self, file_name, branches=None, 
                    use_remote=False, quiet=False): 
        """Import branches from a single file 
        
        Args:
            file_name: Path to the file
            branches: Flat list or grouped dict of branches to import
            use_remote: If accessing the file remotely (/pnfs not mounted)
            quiet: limit verbosity if calling from import_dataset
            
        Returns:
            Awkward array with imported data
        """
        
        # Initialise reader instance 
        self.reader = Reader(use_remote=use_remote, verbosity=self.verbosity)

        # Result container
        result = {}

        # Get the branches 
        result = self._get_array(
            file_name,
            branches=branches,
            quiet=quiet
        )
        
        if result is not None:
            if self.verbosity > 0 and not quiet:
                print(f"{self.print_prefix}✅  Imported branches")
            if self.verbosity > 1 and not quiet:
                print(f"{self.print_prefix} Array structure:")
                result.type.show()
        else:
            print(f"{self.print_prefix}❌  Failed to import branches")
            
        return result

    def import_dataset(self, defname=None, file_list_path=None,
                       branches=None, use_remote=False, max_workers=None):
        """Import branches from a SAM definition or a file list
        
        Wraps import_file in a process function and sends it to Processor
        
        Args:
            defname: SAM definition name
            file_list: file list path
            branches: Flat list or grouped dict of branches to import
            use_remote: If accessing the file remotely (/pnfs not mounted)
            max_workers: Maximum number of parallel workers
            
        Returns:
            Concatenated awkward array with imported data from all files
        """

        # Check inputs
        if bool(defname is None) == bool(file_list_path is None): # Both None or both have values
            print(f"{self.print_prefix}❌  Please provide exactly one of 'defname' or 'file_list'")
            return None

        # Initialise processor 
        processor = Processor(verbosity=self.verbosity) 
        
        # Prepare file list
        file_list = []
        if defname: 
            # Get file list from SAM definition
            file_list = processor.get_file_list(defname=defname)
        elif file_list_path: 
            # Get file list from file list path 
            file_list = processor.get_file_list(file_list_path=file_list_path)

        # Wrap import_file() in process function
        def process_func(file_name):
            return self.import_file(
                file_name=file_name,
                branches=branches,
                use_remote=use_remote,
                quiet=True
            )

        # Get list of arrays 
        arrays = processor.process_files_parallel(
            file_list,
            process_func,
            max_workers=max_workers
        )

        # Concatenate them
        result = ak.concatenate(arrays)

        if result is not None:
            if self.verbosity > 0:
                print(f"{self.print_prefix}✅  Returning concatenated array containing {len(result)} events")
            if self.verbosity > 1:
                print(f"{self.print_prefix} Array structure:")
                result.type.show()
        else:
            print(f"{self.print_prefix}❌ Concatenated array is None: failed to import branches")
        
        if len(result) == 0:
            print(f"{self.print_prefix}⚠️  No events found in array")
            
        return result
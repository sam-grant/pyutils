import uproot
import awkward as ak
from pyread import Reader

# Could make this a callable class... 
class Importer:
    """Utility class for importing branches from ROOT TTree files

    Intended to used via by the pyprocess Processor class
    """
    
    def __init__(self, file_name, branches, dir_name="EventNtuple", tree_name="ntuple", use_remote=False, location="tape", schema="root", verbosity=1):
        """Initialise the importer
        
        Args:
            file_name: Name of the file
            branches: Flat list or grouped dict of branches to import
            dir_name: Ntuple directory in file 
            tree_name: Ntuple name in file directory
            use_remote: Flag for reading remote files 
            location: Remote files only. File location: tape (default), disk, scratch, nersc 
            schema: Remote files only. Schema used when writing the URL: root (default), http, path, dcap, samFile
            verbosity: Print detail level (0: minimal, 1: medium, 2: maximum) 
        """
        self.file_name = file_name
        self.branches = branches
        self.dir_name = dir_name
        self.tree_name = tree_name
        self.use_remote = use_remote
        self.location = location
        self.schema = schema
        self.verbosity = verbosity 

        # Print prefix
        self.print_prefix = "[pyimport] "
        
        # Create reader 
        self.reader = Reader(
            use_remote=self.use_remote,
            location=self.location,
            schema=self.schema,
            verbosity=self.verbosity 
        )
        
    def import_branches(self):
        """Internal function to open ROOT file and import specified branches
            
        Returns:
            Awkward array with imported data
        """
        
        try:
            # Get uproot object
            file = self.reader.read_file(self.file_name)

            # Access the tree
            if self.dir_name in file and self.tree_name in file[self.dir_name]:
                # Get tree
                tree = file[self.dir_name][self.tree_name]
                # Print tree info 
                if self.verbosity > 1:
                    print(f"{self.print_prefix} Accessing branches in tree:")
                    tree.show(filter_name=self.branches, interpretation_width=100)
                
                # Result container
                result = {}

                if self.branches is None: 
                    print(f"{self.print_prefix}❌ Please provide a list of branches, or self.branches='*' to import all") 
                    return None
        
                # Flat list
                elif isinstance(self.branches, list):
                    result = tree.arrays(filter_name=self.branches, library="ak")
        
                # Grouped dictionary
                elif isinstance(self.branches, dict):
                    data = {}
                    # Get arrays per field/group
                    for group, sub_branches in self.branches.items():
                        data[group] = tree.arrays(filter_name=sub_branches, library="ak")
                    # Zip them together 
                    result = ak.zip(data) 
        
                # If using "*" get all branches
                elif self.branches == "*":
                    self.branches = [branch for branch in tree.keys()] 
                    if self.verbosity > 0:
                        print(f"{self.print_prefix} Importing all branches")
                    # Return array 
                    result = tree.arrays(filter_name=self.ranches, library="ak")
                    
                else: 
                    print(f"{self.print_prefix}❌ Branches type {self.branches.type} not recognised") 
                    return None
                
                if result is not None:
                    if self.verbosity > 0:
                        print(f"{self.print_prefix}✅ Imported branches")
                    if self.verbosity > 1:
                        print(f"{self.print_prefix} Array structure:")
                        result.type.show()
                else:
                    print(f"{self.print_prefix}❌ Failed to import branches")                

                # Return
                return result
                
            else:
                print(f"{self.print_prefix}❌ Could not find tree {self.dir_name}/{self.tree_name} in file {file_name}")
                return None
    
        except Exception as e:
            print(f"{self.print_prefix}❌ Error getting branches in file {file_name}: {e}")
            return None

        finally:
            # Ensure the file is closed
            if hasattr(file, "close"):
                file.close()

    # def __call__(self, file_name):
    #     return self.import_branches(file_name)
    
    # def import_file(self, file_name, branches=None, quiet=False): 
    #     """Import branches from a single file 
        
    #     Args:
    #         file_name: Path to the file
    #         branches: Flat list or grouped dict of branches to import
    #         quiet: limit verbosity if calling from import_dataset
            
    #     Returns:
    #         Awkward array with imported data
    #     """
        
    #     # Initialise reader instance 
    #     # Sorry why here? Should this not be in _get_array? 
    #     self.reader = Reader(
    #         use_remote=self.use_remote,
    #         location=self.location,
    #         schema=self.schema,
    #         verbosity=0 # Reduce verbosity for multiprocess
    #     )

    #     # Result container
    #     result = {}

    #     # Get the branches 
    #     result = self._get_array(
    #         file = self.reader.read_file(file_name), 
    #         branches=branches,
    #         quiet=quiet # Reduce verbosity for multiprocess
    #     )

    #     # Close file
    #     file.close()
        
    #     if result is not None:
    #         if self.verbosity > 0 and not quiet:
    #             print(f"{self.print_prefix}✅ Imported branches")
    #         if self.verbosity > 1 and not quiet:
    #             print(f"{self.print_prefix} Array structure:")
    #             result.type.show()
    #     else:
    #         print(f"{self.print_prefix}❌ Failed to import branches")
            
    #     return result

    # >Note: I wonder if this would be better off being called "process_dataset" in the Processor class? 
    # This would increase the complexity of the init though. 
    # def import_dataset(self, defname=None, file_list_path=None, branches=None, max_workers=None, custom_process_func=None):
    #     """Import branches from a SAM definition or a file list
        
    #     Wraps import_file in a process function and sends it to Processor
        
    #     Args:
    #         defname: SAM definition name
    #         file_list: file list path
    #         branches: Flat list or grouped dict of branches to import
    #         max_workers: Maximum number of parallel workers
    #         custom_process_func: Optional custom processing function for files in worker threads
            
    #     Returns:
    #         - If custom_process_func is None: a concatenated awkward array with imported data from all files
    #         - If custom_process_func is not None: a list of outputs from the custom process
    #     """

    #     # Check inputs
    #     if bool(defname is None) == bool(file_list_path is None): # Both None or both have values
    #         print(f"{self.print_prefix}❌ Please provide exactly one of 'defname' or 'file_list'")
    #         return None

    #     # Validate custom_process_func if provided
    #     if custom_process_func is not None:
    #         # Check if it's callable
    #         if not callable(custom_process_func):
    #             print(f"{self.print_prefix}❌ custom_process_func is not callable")
    #             return None
                
    #     # Check function signature
    #     sig = inspect.signature(custom_process_func)
    #     if len(sig.parameters) != 1:
    #         print(f"{self.print_prefix}❌ custom_process_func must take exactly one argument (file_name)")
    #         return None
            
    #     # Initialise processor 
    #     processor = Processor(verbosity=self.verbosity) 
        
    #     # Prepare file list
    #     file_list = []
    #     if defname: 
    #         # Get file list from SAM definition
    #         file_list = processor.get_file_list(defname=defname)
    #     elif file_list_path: 
    #         # Get file list from file list path 
    #         file_list = processor.get_file_list(file_list_path=file_list_path)

    #     if custom_process is None: # Then use the default function
    #         def process_func(file_name):
    #             # Create a new importer instance for this thread with same config
    #             thread_importer = Importer(
    #                 dir_name=self.dir_name,
    #                 tree_name=self.tree_name,
    #                 use_remote=self.use_remote,
    #                 location=self.location,
    #                 schema=self.schema,
    #                 verbosity=0  # Reduce verbosity for worker instances
    #             )
    #             return thread_importer.import_file(
    #                 file_name=file_name,
    #                 branches=branches,
    #                 quiet=True
    #             )
    #     else: # Use the custom process function  
    #         process_func = custom_process_func

    #     # Get list of results 
    #     results = processor.process_files_parallel(
    #         file_list,
    #         process_func,
    #         max_workers=max_workers
    #     )

    #     if len(results) == 0:
    #         print(f"{self.print_prefix}⚠️ Results list has length zero")

    #     if custom_process is None:
    #         # Concatenate the arrays
    #         results = ak.concatenate(results)
    #         if results is not None:
    #             if self.verbosity > 0:
    #                 print(f"{self.print_prefix}✅ Returning concatenated array containing {len(result)} events")
    #             if self.verbosity > 1:
    #                 print(f"{self.print_prefix}Array structure:")
    #                 results.type.show()
    #         else:
    #             print(f"{self.print_prefix}❌ Concatenated array is None: failed to import branches")
    #     else: 
    #         if self.verbosity > 0:
    #             print(f"{self.print_prefix}✅ Returning list of results of {len(results)} from custom process function")

    #     return results


    # Should need this right? 
    # def process_file(self, file_name, branches=None, quiet=False): 
    #     """Process a single file 
        
    #     Args:
    #         file_name: Path to the file
    #         branches: Flat list or grouped dict of branches to import
    #         quiet: limit verbosity if calling from import_dataset
            
    #     Returns:
    #         Awkward array with imported data
    #     """

    #     # Get importer 
    #     importer = Importer(
            
    #     )
        
    #     # Initialise reader instance 
    #     # Sorry why here? Should this not be in _get_array? 
    #     self.reader = Reader(
    #         use_remote=self.use_remote,
    #         location=self.location,
    #         schema=self.schema,
    #         verbosity=0 # Reduce verbosity for multiprocess
    #     )

    #     # Result container
    #     result = {}

    #     # Get the branches 
    #     result = self._get_array(
    #         file = self.reader.read_file(file_name), 
    #         branches=branches,
    #         quiet=quiet # Reduce verbosity for multiprocess
    #     )

    #     # Close file
    #     file.close()
        
    #     if result is not None:
    #         if self.verbosity > 0 and not quiet:
    #             print(f"{self.print_prefix}✅ Imported branches")
    #         if self.verbosity > 1 and not quiet:
    #             print(f"{self.print_prefix} Array structure:")
    #             result.type.show()
    #     else:
    #         print(f"{self.print_prefix}❌ Failed to import branches")
            
    #     return result
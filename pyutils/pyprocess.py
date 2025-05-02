#! /usr/bin/env python
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import awkward as ak
import inspect
import tqdm
from pyimport import Importer # For importing branches

class Processor:
    """Interface for processing files or datasets"""
    
    # def __init__(self, verbosity=1):

    def __init__(self, dir_name="EventNtuple", tree_name="ntuple", use_remote=False, location="tape", schema="root", verbosity=1):
        """Initialise the processor

        Args:
            dir_name (str, optional): Ntuple directory in file 
            tree_name (str, optional): Ntuple name in file directory
            use_remote (bool, optional): Flag for reading remote files 
            location (str, optional): Remote files only. File location: tape (default), disk, scratch, nersc 
            schema (str, optional): Remote files only. Schema used when writing the URL: root (default), http, path, dcap, samFile
            verbosity (int, optional): Print detail level (0: minimal, 1: medium, 2: maximum) 
        """
        self.dir_name = dir_name
        self.tree_name = tree_name
        self.use_remote = use_remote
        self.location = location
        self.schema = schema
        self.verbosity = verbosity 
        self.print_prefix = "[pyprocess] "

        # Confirm init
        if verbosity > 0:
            # Print out optional args 
            confirm_str = f"{self.print_prefix}Initialised Processor:\n\tpath = '{self.dir_name}/{self.tree_name}'\n\tuse_remote = {self.use_remote}"
            if use_remote:
                confirm_str += f"\n\tlocation = {self.location}\n\tschema = {self.schema}"
            confirm_str += f"\n\tverbosity={self.verbosity}"
            print(confirm_str) 

    def get_file_list(self, defname=None, file_list_path=None):
        """Utility to get a list of files from a SAM definition OR a text file
        
        Args:
            defname: SAM definition name 
            file_list_path: Path to a plain text file containing file paths
            
        Returns:
            List of file paths
        """
        
        # Check if a file list path was provided
        if file_list_path:
            try:
                if not os.path.exists(file_list_path):
                    print(f"{self.print_prefix}❌ File list path does not exist: {file_list_path}")
                    return []

                if self.verbosity > 1:
                     print(f"{self.print_prefix}Loading file list from {file_list_path}") 
                    
                with open(file_list_path, "r") as file_list:
                    file_list = file_list.readlines()
                    
                file_list = [line.strip() for line in file_list if line.strip()]

                if file_list and self.verbosity > 0:
                    print(f"{self.print_prefix}✅ Successfully loaded file list\n\tPath: {file_list_path}\n\tCount: {len(file_list)} files")
                
                return file_list
                
            except Exception as e:
                print(f"{self.print_prefix}❌ Error reading file list from {file_list_path}: {e}")
                return []
        
        # Otherwise, try to use the SAM definition
        elif defname:
            if self.verbosity > 1:
                print(f"{self.print_prefix}Loading file list for SAM definition: {defname}")
            
            try:
                # Setup commands for SAM query
                commands = 'source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh; muse setup ops;'
                commands += f"samweb list-files 'defname: {defname} with availability anylocation' | sort -V"
                
                # Execute commands
                file_list_output = subprocess.check_output(commands, shell=True, universal_newlines=True)
                file_list = [line for line in file_list_output.splitlines() if line]

                if file_list and self.verbosity > 0:
                    print(f"{self.print_prefix}✅ Successfully loaded file list\n\tSAM definition: {defname}\n\tCount: {len(file_list)} files")
                
                # Return the file list
                return file_list
                
            except Exception as e:
                print(f"{self.print_prefix}❌ Exception while getting file list for {defname}: {e}")
                return []
        
        else:
            print(f"{self.print_prefix}❌ Error: Either 'defname' or 'file_list_path' must be provided")
            return []  

    def _process_files_parallel(self, file_list, process_func, max_workers=None):
        """Internal function to parallelise file operations with given a process function
        
        Args:
            file_list: List of files to process
            process_func: Function to call for each file (must accept file name as first argument)
            max_workers: Maximum number of worker threads
            
        Returns:
            List of results from each processed file
        """
        
        if not file_list:
            print(f"{self.print_prefix}❌ Warning: Empty file list provided")
            return None
            
        if max_workers is None:
            # Return a sensible default for max threads
            max_workers = min(len(file_list), 2*os.cpu_count() or 4) 

        print(f"{self.print_prefix}Starting processing on {len(file_list)} files with {max_workers} workers")

        # Store results in a list
        results = []  

        # For tracking progress
        total_files = len(file_list)
        completed_files = 0 
        failed_files = 0

        # Set up tqdm format and styling
        bar_format = "{desc}: {percentage:3.0f}%|{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        # bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}, Successful={postfix[successful]}, Failed={postfix[failed]}]"
        # bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}, Successful={postfix[successful]}, Failed={postfix[failed]}]"

        # Create progress bar with tqdm
        # with tqdm.tqdm(total=total_files, desc="Processor", unit="file") as pbar:
        with tqdm.tqdm(
            total=total_files, 
            desc="Processing",
            unit="file",
            bar_format=bar_format,
            colour="green",
            ncols=100  # Fixed width for better appearance
        ) as pbar:
            
            # Start thread pool executor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Create futures for each file processing task
                futures = {executor.submit(process_func, file_name): file_name for file_name in file_list}
                
                # Process results as they complete
                for future in as_completed(futures):
                    file_name = futures[future]
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                            completed_files += 1
                        else: 
                            failed_files += 1
                            
                        # percent_complete = (completed_files / total_files) * 100
                        
                        # Extract just the base filename for cleaner output
                        base_file_name = file_name.split('/')[-1]
                        
                        # if self.verbosity > 1:
                        #     print(f"{self.print_prefix}✅ {base_file_name}")
                        #     print(f"\tProgress: {completed_files}/{total_files} files ({percent_complete:.1f}%)\n")
                        
                    except Exception as e:
                        print(f"{self.print_prefix}❌ Error processing {file_name}:\n{e}")
                        # Redraw progress bar
                        pbar.refresh()

                    finally:
                        # Always update the progress bar, regardless of success or failure
                        pbar.update(1)
                        # Optionally update progress bar description with success/failure counts
                        # if self.verbosity > 0:
                        # Update postfix with stats
                        pbar.set_postfix({
                            "succesful": completed_files, 
                            "failed": failed_files #,
                            # "success rate": f"{(completed_files/max(1, completed_files+failed_files))*100:.1f}%"
                        })

        # Report completion status
        # print(f"{self.print_prefix}✅ Done: {completed_files}/{total_files} files processsed")
        
        # Return the results
        return results

    # custom_process_func -> process_func?
    def process_data(self, file_name=None, file_list_path=None, defname=None, branches=None, max_workers=None, custom_process_func=None):
        """Process the data 
        
        Args:
            file_name: File name 
            defname: SAM definition name
            file_list_path: Path to file list 
            branches: Flat list or grouped dict of branches to import
            max_workers: Maximum number of parallel workers
            custom_process_func: Optional custom processing function for each file 
            
        Returns:
            - If custom_process_func is None: a concatenated awkward array with imported data from all files
            - If custom_process_func is not None: a list of outputs from the custom process
        """

        # Check that we have one type of file argument 
        file_sources = sum(x is not None for x in [file_name, defname, file_list_path])
        if file_sources != 1: 
            print(f"{self.print_prefix}❌ Please provide exactly one of 'file_name', 'file_list_path', or defname'")
            return None

        # Validate custom_process_func if provided
        if custom_process_func is not None:
            # Check if it's callable
            if not callable(custom_process_func):
                print(f"{self.print_prefix}❌ custom_process_func is not callable")
                return None
                
            # Check function signature
            sig = inspect.signature(custom_process_func)
            if len(sig.parameters) != 1:
                print(f"{self.print_prefix}❌ custom_process_func must take exactly one argument (file_name)")
                return None        

        # Verbosity for worker threads is the same as Processor 
        worker_verbosity = self.verbosity 
        # Unless we have multiple files
        if file_name is None:
            worker_verbosity = 0
            
        # Set up process function
        if custom_process_func is None: # Then use the default function
            def process_func(file_name):
                # Create a unique importer instance for this thread with same config
                importer = Importer(
                    file_name=file_name,
                    branches=branches,
                    dir_name=self.dir_name,
                    tree_name=self.tree_name,
                    use_remote=self.use_remote,
                    location=self.location,
                    schema=self.schema,
                    verbosity=worker_verbosity
                )
                # Return result  
                return importer.import_branches()
        else: # Use the custom process function  
            process_func = custom_process_func

        # Handle a single file
        
        if file_name: 
            try: 
                result = process_func(file_name) # Run the process
                if self.verbosity > 0:
                    print(f"{self.print_prefix}✅ Returning result from process on {file_name}")
                return result 
            except Exception as e:
                print(f"{self.print_prefix}❌ Error processing {file_name}:\n{e}")
                return None
            
        # Now handle multiple files

        # Prepare file list
        file_list = []
        if file_list_path: # Get file list from file list path 
            file_list = self.get_file_list(file_list_path=file_list_path)
        elif defname: # Get file list from SAM definition
            file_list = self.get_file_list(defname=defname)

        # Get list of results 
        results = self._process_files_parallel(
            file_list,
            process_func,
            max_workers=max_workers
        )

        if len(results) == 0:
            print(f"{self.print_prefix}⚠️ Results list has length zero")

        if custom_process_func is None:
            # Concatenate the arrays
            results = ak.concatenate(results)
            if results is not None:
                if self.verbosity > 0:
                    print(f"{self.print_prefix}✅ Returning concatenated array containing {len(results)} events")
                if self.verbosity > 1:
                    print(f"{self.print_prefix}Array structure:")
                    results.type.show()
            else:
                print(f"{self.print_prefix}❌ Concatenated array is None: failed to import branches")
        else: 
            if self.verbosity > 0:
                print(f"{self.print_prefix}✅ Returning list of {len(results)} result from custom process function")

        return results

# Template for creating a custom processors with the Processor framework
# -----------------------------------------------------------------------

class Skeleton:
    """Template class for creating a custom analysis processor
    
    This template demonstrates how to create a class to run
    custom analysis jobs with the Processor framework 
    
    To use this skeleton:
    1. Either initilaise the entire class or pass it as an argument to your Processor class
    2. Customize the __init__ method with your configuration
    3. Implement your processing logic in the process method
    4. Add any additional helper methods you need
    5. Override methods as needed
    """
    
    def __init__(self):
        """Initialise your file processor with configuration parameters
        
        Customise this method to include parameters specific to your analysis.
        """
        # File source configuration
        self.file_list_path = None  # Path to a text file with file paths
        self.defname = None         # SAM definition name
        self.file_name = None       # Single file to process
        
        # Data import configuration
        self.branches = []          # List of branches to import
        self.dir_name = "EventNtuple"  # Directory in ROOT file
        self.tree_name = "ntuple"   # Tree name in directory
        self.use_remote = False     # Whether to use remote file access
        self.location = "tape"      # File location (tape, disk, scratch, nersc)
        self.schema = "root"        # URL schema for remote files
        
        # Processing configuration
        self.verbosity = 1          # Print detail level (0=minimal, 1=medium, 2=maximum)
        self.max_workers = None     # Number of parallel workers (None=auto)
        
        # Analysis-specific configuration
        # Add your own parameters here!
        # self.param1 = value1
        # self.param2 = value2
        
        # Printout marker
        self.print_prefix = "[Template] "

        if self.verbosity > 0:
            print(f"{self.print_prefix}✅ Template initialised")
        
        
    def process_file(self, file_name):
        """Process a single file
        
        This is the core method that will be called for each file.
        Implement your file processing logic here.
        
        Args:
            file_name: Name of the file to process
            
        Returns:
            Any data structure representing the processed result
        """
        try:
            # Create an Importer for this file
            importer = Importer(
                file_name=file_name,
                branches=self.branches,
                dir_name=self.dir_name,
                tree_name=self.tree_name,
                use_remote=self.use_remote,
                location=self.location,
                schema=self.schema,
                verbosity=0  # Reduce verbosity for worker threads
            )
            
            # Import the data
            data = importer.import_branches()
            
            # Check if import was successful
            if data is None:
                print(f"{self.print_prefix}Failed to import data from {file_name}")
                return None
                
            # Example processing - REPLACE WITH YOUR OWN LOGIC
            # This is just a placeholder that returns the file name and a count
            result = {
                "file_name": file_name,
                "event_count": len(data[self.branches[0]]) if self.branches else 0
            }
            
            return result
            
        except Exception as e:
            print(f"{self.print_prefix}Error processing {file_name}: {e}")
            return None
            
    def execute(self):
        """Run the processor on the configured files
        
        Returns:
            Combined results from all processed files
        """

        if self.verbosity > 0:
            print(f"{self.print_prefix}Starting analysis")
        
        # Input validation
        file_sources = sum(x is not None for x in [self.file_name, self.file_list_path, self.defname])
        if file_sources != 1:
            print(f"{self.print_prefix} Please provide exactly one of 'file_name', 'file_list_path', or defname'")
            return None
        elif file_sources > 1:
            print(f"{self.print_prefix}Error: Multiple file sources specified. Use only one of: file_name, file_list_path, or defname.")
            return None
            
        # Initialise the processor
        processor = Processor(
            dir_name=self.dir_name,
            tree_name=self.tree_name,
            use_remote=self.use_remote,
            location=self.location,
            schema=self.schema,
            verbosity=self.verbosity
        )
        
        # Process the data
        results = processor.process_data(
            file_name=self.file_name,
            file_list_path=self.file_list_path,
            defname=self.defname,
            branches=self.branches,
            max_workers=self.max_workers,
            custom_process_func=self.process_file
        )

        if self.verbosity > 0:
            print(f"{self.print_prefix}✅ Analysis complete")
            
        return results
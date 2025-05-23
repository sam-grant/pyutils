# Sam Grant
# May 2025
# Tests for pyutils modules 

# pyutils path
import sys
sys.path.append("..")

# pyutils classes
from pyread import Reader                  # Data reading 
from pyprocess import Processor, Skeleton  # Data processing
from pyimport import Importer              # TTree (EventNtuple) importing 
from pyplot import Plot                    # Plotting and visualisation 
from pyprint import Print                  # Array visualisation 
from pyselect import Select                # Data selection and cut management 
from pyvector import Vector                # Element wise vector operations
from pylogger import Logger                # Printout manager

class Tester:
    """ Tests for pyutils """
    
    def __init__(self):  
        # Max verbosity 
        self.verbosity = 2 
        
        # Error tracking
        self.error_count = 0
        self.test_count = 0
        self.failed_tests = []

        # Test files
        self.local_file_path = "/exp/mu2e/data/users/sgrant/pyutils-test/TestFiles/nts.mu2e.CeEndpointOnSpillTriggered.MDC2020aq_best_v1_3_v06_03_00.001210_00000699.root"
        self.remote_file_name = "nts.mu2e.CeEndpointOnSpillTriggered.MDC2020aq_best_v1_3_v06_03_00.001210_00000699.root"
        self.local_file_list = "/exp/mu2e/data/users/sgrant/pyutils-test/TestFileLists/local_file_list.txt"
        self.remote_file_list = "/exp/mu2e/data/users/sgrant/pyutils-test/TestFileLists/remote_file_list.txt"
        self.defname = "nts.mu2e.CeEndpointOnSpillTriggered.MDC2020aq_best_v1_3_v06_03_00.root"
        
        # Setup logger 
        self.logger = Logger(
            print_prefix="[pytest]", 
            verbosity=2  # max verbosity 
        )
        self.logger.log("Initialised", "success")
    
    def _safe_test(self, test_name, test_function, *args, **kwargs):
        """Wrapper to safely run tests and count errors"""
        self.test_count += 1
        try:
            self.logger.log(f"Running test: {test_name}", "test")
            result = test_function(*args, **kwargs)
            if result is None or (hasattr(result, '__len__') and len(result) == 0):
                self.logger.log(f"FAILED: {test_name}: returned no results", "error")
                self.error_count += 1
                self.failed_tests.append(test_name)
                return False
            else:
                self.logger.log(f"PASSED: {test_name}", "success")
                return True
        except Exception as e:
            self.logger.log(f"FAILED: {e}", "error")
            self.error_count += 1
            self.failed_tests.append(test_name)
            return False
    
    ###### pyread ######
    
    def _local_read(self):  
        self.logger.log("Local read", "test")  
        # Start reader
        reader = Reader(verbosity=self.verbosity)
        # Read
        return reader.read_file(file_path=self.local_file_path)  
    
    def _remote_read(self):  
        self.logger.log("Remote read", "test")  
        # Start reader
        reader = Reader(
            use_remote=True,
            location="tape",
            verbosity=self.verbosity
        )
        # Read
        return reader.read_file(file_path=self.remote_file_name)  
    
    def _test_reader(self, local_read=True, remote_read=True): 
        """Test pyread:Reader module"""
        self.logger.log("Testing pyread:Reader", "test")  
        
        if local_read: 
            self._safe_test("pyread:Reader:read_file (local)", self._local_read)
        
        if remote_read: 
            self._safe_test("pyread:Reader::read_file (remote)", self._remote_read)

    ###### pyimporter ######

    def _local_import_branch(self):
        importer = Importer(
            file_name = self.local_file_path,
            branches = ["event"],
            use_remote=False,
            verbosity = self.verbosity
        )

        return importer.import_branches()

    def _remote_import_branch(self):
        importer = Importer(
            file_name = self.local_file_path,
            branches = ["event"],
            use_remote=True,
            location="tape",
            verbosity = self.verbosity
        )

        return importer.import_branches()

    def _local_import_grouped_branches(self):
        importer = Importer(
            file_name = self.local_file_path,
            branches = {
                "evt" : ["event"],
                "crv" : ["crvcoincs.PEs", "crvcoincs.nhits"]
            },
            use_remote=False,
            verbosity = self.verbosity
        )

        return importer.import_branches()
        
    def _local_import_all_branches(self):
        importer = Importer(
            file_name = self.local_file_path,
            branches = "*",
            use_remote=False,
            verbosity = 1 # this one is loud! self.verbosity
        )

        return importer.import_branches()
    
    def _test_importer(
        self, 
        local_import_branch=True,
        remote_import_branch=True,
        local_import_grouped_branches=True,
        local_import_all_branches=True
        
    ):
        """Test pyimport:Importer module"""
        self.logger.log("Testing pyimport:Importer", "info")  

        if local_import_branch:
            self._safe_test("pyimport:Importer:import_branches (local, single branch)", self._local_import_branch)

        if local_import_branch:
            self._safe_test("pyimport:Importer:import_branches (remote, single branch)", self._remote_import_branch)
            
        if local_import_grouped_branches:
            self._safe_test("pyimport:Importer:import_branches (local, grouped branches)", self._local_import_grouped_branches)

        if local_import_all_branches:
            self._safe_test("pyimport:Importer:import_branches (local, all branches)", self._local_import_all_branches)
            
    ###### pyprocess ######
    
    def _local_process_file(self):
        processor = Processor(verbosity=self.verbosity)
        return processor.process_data(
            file_name=self.local_file_path,
            branches=["event"]
        )

    def _remote_process_file(self):
        processor = Processor(
            use_remote=True,
            verbosity=self.verbosity
        )
        return processor.process_data(
            file_name=self.remote_file_name,
            branches=["event"]
        )

    def _local_get_file_list(self):
        processor = Processor(verbosity=self.verbosity)
        return processor.get_file_list(file_list_path=self.local_file_list)

    def _remote_get_file_list(self):
        processor = Processor(
            use_remote=True,
            verbosity=self.verbosity
        )
        return processor.get_file_list(file_list_path=self.remote_file_list)

    def _sam_get_file_list(self):
        processor = Processor(
            use_remote=True,
            verbosity=self.verbosity
        )
        return processor.get_file_list(defname=self.defname)

    def _basic_multithread(self):
        processor = Processor(
            verbosity=self.verbosity
        )
        return processor.process_data(
            file_list_path=self.local_file_list,
            branches = ["event"]
        )

    def _basic_multiprocess(self):
        processor = Processor(
            verbosity=self.verbosity
        )
        return processor.process_data(
            file_list_path=self.local_file_list,
            branches = ["event"]
        )

    def _advanced_multithread(self):
        
        class MyProcessor(Skeleton):
            def __init__(processor_self):
                super().__init__()
                processor_self.file_list_path=self.local_file_list
            def process_file(self, file_name):
                return file_name # No need for anything interesting here

        my_processor = MyProcessor()
        return my_processor.execute()
        
    def _test_processor(
        self, 
        local_process_file=True,
        remote_process_file=True,
        get_file_list=True,
        basic_multifile=True,
        advanced_multifile=True
    ):
        """Test pyprocess module"""
        if local_process_file:
            self._safe_test("pyprocess:Processor:process_data (local, single file, single branch)", self._local_process_file)

        if remote_process_file:
            self._safe_test("pyprocess:Processor:process_data (remote, single file, single branch)", self._remote_process_file)

        if get_file_list:
            self._safe_test("pyprocess:Processor:get_file_list (local file list path)", self._local_get_file_list)
            self._safe_test("pyprocess:Processor:get_file_list (remote file list path)", self._remote_get_file_list)
            self._safe_test("pyprocess:Processor:get_file_list (SAM definition)", self._sam_get_file_list)

        if basic_multifile:
            self._safe_test("pyprocess:Processor:process_data (basic multithread)", self._basic_multithread)
            self._safe_test("pyprocess:Processor:process_data (basic multiprocess)", self._basic_multiprocess)

        if advanced_multifile:
            self._safe_test("pyprocess:Skeleton (advanced multithread)", self._advanced_multithread)
    
    # ###### Add more test methods for other modules ######
    
    def test_plot(self):
        pass

    def test_print(self):
        pass

    def test_select(self):
        pass

    def test_vector(self):
        pass
    
    ###### Test summary ######

    def print_summary(self):
       """Print test summary"""
       failed_tests_str = "\n".join([f"  - {test}" for test in self.failed_tests]) if self.failed_tests else ""
       final_status = "🎉 All tests passed!" if self.error_count == 0 else f"⚠️ {self.error_count} test(s) failed"
       
       summary = f"""
                {'=' * 50}
                TEST SUMMARY
                {'=' * 50}
                Total tests run: {self.test_count}
                Passed: {self.test_count - self.error_count}
                Failed: {self.error_count}
                {f'Failed tests:\n{failed_tests_str}' if self.failed_tests else ''}
                {final_status}"""
       
       self.logger.log(summary, "test")
    
    ###### run tests ######
    
    def run(self, 
           test_reader=True,
           test_processor=True, 
           test_importer=True,
           test_plot=False,
           test_print=False,
           test_select=False,
           test_vector=False
        ): 
        """Run all specified tests"""
        
        if test_reader:
            self.logger.log("************ Testing pyread ************", "test")
            self._test_reader()

        if test_importer:
            self.logger.log("************ Testing pyimport ************", "test")
            self._test_importer()

        if test_processor:
            self.logger.log("************ Testing pyprocess ************", "test")
            self._test_processor()            
    
        if test_plot:
            self.test_plot()
            
        if test_print:
            self.test_print()
            
        if test_select:
            self.test_select()
            
        if test_vector:
            self.test_vector()
        
        # Print final summary
        self.print_summary()
        
        return self.error_count == 0  # Return True if all tests passed

# tester = Tester()
# tester.run()  # Run all tests

# Or run specific tests:
# tester.run(test_reader=True, test_processor=False)
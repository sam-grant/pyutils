#! /usr/bin/env python
import uproot
import os
import subprocess
from . import _env_manager # Environment manager
from .pylogger import Logger # Messaging/logging

class Reader:
    """Unified interface for accessing files, either locally or remotely"""
    
    def __init__(self, use_remote=False, location="tape", schema="root", verbosity=1):
        """Initialise the reader
        
        Args:
            use_remote (bool, opt): Whether to use remote access methods
            location (str, opt): File location for remote files: tape (default), disk, scratch, nersc 
            schema (str, opt): Schema for remote file path: root (default), http, path , dcap, samFile
            verbosity (int, opt): Level of output detail (0: errors only, 1: info & warnings, 2: max)
        """
        self.use_remote = use_remote # access files on /pnfs from EAF
        self.location = location
        self.schema = schema

        # Start logger 
        self.logger = Logger( 
            print_prefix = "[pyread]", 
            verbosity = verbosity
        )

        # Setup and validation for remote reading
        if self.use_remote:
            #  Ensure mdh environment
            _env_manager.ensure_environment()  
            # Check arguments
            valid_locations = ["tape", "disk", "scratch", "best"]
            if self.location not in valid_locations:
                self.logger.log(f"Location '{location}' may not be valid. Expected one of {valid_locations}", "warning")
            valid_schemas = ["root", "http", "path", "dcap", "samFile"]
            if self.schema not in valid_schemas:
                self.logger.log(f"Schema '{schema}' may not be valid. Expected one of {valid_schemas}", "warning")

    def read_file(self, file_path):
        """Read a file using the appropriate method
        
        Args:
            file_path: Path to the file
            
        Returns:
            Uproot file object
        """
        if self.use_remote:
            return self._read_remote_file(file_path)
        else:
            return self._read_local_file(file_path)
    
    def _read_local_file(self, file_path):
        """Open a local file directly"""
        try: 
            file = uproot.open(file_path)
            self.logger.log(f"Opened {file_path}", "success")
            return file
        except Exception as e:
            self.logger.log(f"Exception while opening {file_path}: {e}", "warning")
            raise # propagate exception up

    def _check_file_location(self, file_path):
        """Fallback helper to find the file location the file
        """ 
        self.logger.log(f"Fallback: checking file location='{self.location}'", "info")
        try:
            # Locate the file
            commands = f"samweb locate-file {file_path}"
            sam_file_path = subprocess.check_output(commands, shell=True, text=True, stderr=subprocess.DEVNULL).strip() 
            # Run checks
            if "tape" in sam_file_path and self.location != "tape":
                self.logger.log(f"Files found on 'tape', retrying", "success")
                self.location = "tape"
            elif "persistent" in sam_file_path and self.location != "disk":
                self.logger.log(f"Files found on 'disk', retrying", "success")
                self.location = "disk"
            elif "scratch" in sam_file_path and self.location != "scratch":
                self.logger.log(f"Files found on 'scratch', retrying", "success")
                self.location = "scratch"
            else:
                self.logger.log(f"Files not found on 'tape', 'disk', or 'scratch'", "warning")
                
        except Exception as e:
            self.logger.log(f"Error checking file location: {e}", "error")
            raise
    
    def _read_remote_file(self, file_path):
        """Open a file from /pnfs via mdh"""
        self.logger.log(f"Opening remote file: {file_path}", "info")

        # Nested helper 
        def _get_file():
            # Setup commands
            commands = f"mdh print-url {file_path} -l {self.location} -s {self.schema}"
            # Execute commands
            this_file_path = subprocess.check_output(commands, shell=True, universal_newlines=True, stderr=subprocess.DEVNULL).strip() 
            # Log
            self.logger.log(f"Created file path: {this_file_path}", "info")
            # Read
            file = self._read_local_file(this_file_path)
            # Return 
            return file

        # Try opening the file
        try:
            file = _get_file()
            return file
        except: 
            # Fallback and check location
            self._check_file_location(file_path)
            try:
                file = _get_file()
                return file
            except Exception as e: # Fallback failed
                self.logger.log(f"Fallback failed... Exception while opening {file_path}: {e}", "warning")
                raise # propagate exception up
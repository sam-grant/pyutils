# Sam Grant 2025 
# Internal helper to set up paths needed for mdh file tools

#! /usr/bin/env python
import os
import subprocess

# Global variable to track if environment is set up
_ENV_IS_SETUP = False

def setup_environment():
    """Set up the environment variables once per process"""
    global _ENV_IS_SETUP

    print_prefix = "[pyutils] "

    
    if not _ENV_IS_SETUP:

        print(f"{print_prefix}Setting environment variables for this process...")

        try:
            
            # Run the setup commands and capture the resulting environment
            commands = "source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh 2>/dev/null; muse setup ops 2>/dev/null; env"
            with open(os.devnull, "w") as devnull: # Suppress error messages 
                result = subprocess.check_output(commands, shell=True, universal_newlines=True, stderr=devnull)
            
            # Parse the environment variables from the result
            for line in result.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
            
            _ENV_IS_SETUP = True
            print(f"{print_prefix}✅ Environment variables set")

        except subprocess.CalledProcessError as e:
            print(f"{print_prefix}❌ Failed to set environment variables: {e}")
            return False

def ensure_environment():
    """Ensure environment is set up before using mdh"""
    if not _ENV_IS_SETUP:
        setup_environment()
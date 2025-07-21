# 1. Setting up your environment

#First, we need to import the necessary external packages. Use the mu2e_env interactive kernel to make sure you have the packages you need, if not using a custom environment (see tutorial).

# Import external packages
import awkward as ak


#2. Processing data

#The pyprocess module handles this, using pyimport and pyread as dependencies. The Processor class is your main tool for processing data.

#Note that help information for all pyutils classes and functions can be accessed by running help(), e.g. help(Processor).

# Import the Procssor class
from pyutils.pyprocess import Processor 

# Initialise the Importer with increased verbosity 
# verbosity=0 will only show errors
processor = Processor(verbosity=2)

# Define the path to our example file
file_name = "/pnfs/mu2e/tape/phy-nts/nts/mu2e/MDS2ac-OnSpillTriggered/MDC2020aw_perfect_v1_3/root/8c/0b/nts.mu2e.MDS2ac-OnSpillTriggered.MDC2020aw_perfect_v1_3.0.root"

# Define the branches we want to access
# For a complete list of available branches, see:
# https://github.com/Mu2e/EventNtuple/blob/main/doc/branches.md
# Also refer to ntuplehelper, available after mu2e setup EventNtuple
branches = ["trksegs"]

# Import the branches from the file
# This loads the data into memory and returns an awkward array
data = processor.process_data(
    file_name=file_name,
    branches=branches
)


#3. Applying selection cuts

#Once data is loaded, you can filter you data with selection cuts. The Select class from pyselect provides tools for this purpose.

# Import the Select class
from pyutils.pyselect import Select 

# Initialise the selector with verbose output
selector = Select(verbosity=2)

# Create a mask to select track segments at the tracker entrance
# sid = 0 corresponds to the tracker entrance plane
at_trkent = selector.select_surface(
    data=data, 
    surface_name="TT_Front"  # Select the tracker entrance
)

# Optional: add the mask to the data array (useful for verification)
data["at_trkent"] = at_trkent

# Apply the mask to create a new array with only track segments at the tracker entrance
trkent = data[at_trkent]


#4. Inspecting Your Data

#After selecting your data, you can verify that the selection cuts are behaving as expected. The Print class from pyprint allows you to examine individual events before and after applying cuts.

# Import the Print class
from pyutils.pyprint import Print

# Initialise the printer
# verbose=False is default and prevents overwhelming output with large arrays
# verbose=True prevents array truncation, for detailed debugging
printer = Print(verbose=False)

# Compare data before and after cuts
print("Before selection cuts:")
printer.print_n_events(data, n_events=1)

print("\nAfter selection cuts:")
printer.print_n_events(trkent, n_events=1)


#5. Performing Vector Operations

# The Vector class from pyvector provides tools for common element wise vector operations on your array.

# Import the Vector class
from pyutils.pyvector import Vector

# Initialise the vector processor
vector = Vector(verbosity=2)

# Calculate the momentum magnitude from the momentum vector components
# This creates a new array with the magnitudes
mom_mag = vector.get_mag(
    branch=trkent["trksegs"],
    vector_name="mom" # either "mom" or "pos" in EventNtuple
)

#6. Plotting

#The Plot class from pyplot provides methods for creating publication-quality plots from flattened arrays.

#    Note: pyplot will be extended to allow plotting histogram objects directly.

#6.1 Creating a 1D Histogram

#First, let's create a 1D histogram of the time distribution for track segments at the tracker entrance (the t0):

# Import the Plot class
from pyutils.pyplot import Plot 

# Initialise the plotter
plotter = Plot()

# Flatten the array 
# ak.flatten with axis=None removes all nesting, so that the result is always a 1D array 
time_flat = ak.flatten(trkent["trksegs"]["time"], axis=None)

# Create a 1D histogram of track times
plotter.plot_1D(
    time_flat,               # Data to plot
    nbins=100,               # Number of bins
    xmin=450,                # Minimum x-axis value
    xmax=1695,               # Maximum x-axis value
    # title="Time at Tracker Entrance",
    xlabel="Time [ns]",
    ylabel="Tracks",
    out_path='h1_time.png',  # Output file path
    stat_box=True,           # Show statistics box
    error_bars=True          # Show error bars
)

# for help
help(plotter.plot_1D)


#6.2 Overlaying 1D histograms

#The plotter.plot_1D_overlay method allows you to overlay multiple 1D histograms.

#This take a dictionary as the first argument, where the key is the legend label and the value is a flattened array. You may also include custom styling for each histogram.

# Let's take the times at all track segments as our "other histogram
time_all_flat = ak.flatten(data["trksegs"]["time"], axis=None)

# Optional custom styles
styles = {
    "All": {
        "histtype": "bar",      # Filled bars 
        "alpha": 0.3,           # Semi-transparent
        "color": "blue"        # Override style file colour
    },
    "Tracker entrance": {
        "histtype": "step",     # Unfilled outline for "reco-like" data
        "linewidth": 2,         # Thicker line
        "color": "red"          # Override style file colour
    }
}

plotter.plot_1D_overlay(
    {
        "All" : time_all_flat, # First histogram
        "Tracker entrance" : time_flat,
    },
    styles=styles, # Optional tyles parameter
    nbins=100,
    xmin=450,
    xmax=1695,
    xlabel="Time [ns]",
    ylabel="Norm. track segments",
    out_path="h1o_time.png",
    norm_by_area=True # Optionally normalise the histograms by area
)


#6.3 Creating a 2D Histogram

#Now, let's create a 2D histogram to explore the relationship between momentum and time:

# Flatten the momentum magnitudes for plotting
mom_mag_flat = ak.flatten(mom_mag, axis=None)

# Create a 2D histogram of momentum vs. time
plotter.plot_2D(
    x=mom_mag_flat,           # x-axis data
    y=time_flat,              # y-axis data
    nbins_x=100,              # Number of x bins
    xmin=85,                  # Minimum x value
    xmax=115,                 # Maximum x value
    nbins_y=100,              # Number of y bins
    ymin=450,                 # Minimum y value
    ymax=1650,                # Maximum y value
    # title="Momentum vs. Time at Tracker Entrance",
    xlabel="Momentum [MeV/c]",
    ylabel="Time [ns]",
    out_path='h2_timevmom.png'
)












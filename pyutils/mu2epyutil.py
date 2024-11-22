import uproot
import awkward as ak
import matplotlib.pyplot as plt
import math
import numpy as np
import vector
from scipy import stats
from matplotlib.ticker import ScalarFormatter
import matplotlib.colors as colors

class Import:
  """ class to help users import a trkana tree and branch """
  def __init__(self, filename, treename="EventNtuple", branchname="ntuple"):
    self.filename= filename
    self.treename = treename
    self.branchname = branchname
    self.Array = ak.Array
  
  def ImportFileList(self, path): 
    """ Import list of files from a text file """
    with open(path, "r") as file_list_: # Open file
      lines_ = file_list_.readlines() # Read file
      lines_ = [line.strip() for line in lines_]  # Remove leading/trailing whitespace
    return lines_ # Return lines as a list

  def ImportFileListFromSAM(self):
    """ import list of files """
    #TODO
    pass
    
  def ImportTree(self):
    """ import root tree """
    input_file = uproot.open(self.filename)
    input_tree = input_file[self.treename][self.branchname]
    return input_tree
    
  def MakeAwkArray(self):
    """ import root tree and save it as an Awkward array """
    input_tree = self.ImportTree()
    self.Array = input_tree.arrays(library='ak')
    return self.Array

  def ImportBranches(self, tree, leafnames):
      """ import list of branches from trkana"""
      list_names = []
      for i, leafname  in enumerate(leafnames):
          list_names.append("/"+str(leafname)+"/")
      branches = tree.arrays(filter_name=list_names)
      return branches
      
  def EvtCut(self):
    #TODO
    pass
    
  def TrkCut(self):
    #TODO
    pass
  
  def TrkSegCut(self):
    #TODO
    pass
    
  def TrkCrvCoincsCut(self):
    #TODO
    pass

class Vector:
  
  # TODO vector functions (mag), track angle (into CRV)
  
  def GetVectorXYZ(self, leafname, vectorreq, sid=0):
    """ 
    imports a XYZ vector branch e.g. mom and turns it into something which can use funcitons are found in:
    https://vector.readthedocs.io/en/latest/api/vector._methods.html 
    """
    # import code and extract branch
    tree = self.ImportTree()
    branch = self.ImportBranches(tree, [leafname])

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

class Print:
  def __init__(self):
    ''' Placeholder init '''
    pass  

  def PrintEvent(self, event, prefix=''):
    ''' Print this event in human readable form '''
    for field in event.fields: # Loop through array elements in the event
      value = event[field] # Get the value
      full_field = f'{prefix}{field}' # Set full field using prefix provided in function call
      if hasattr(value, 'fields') and value.fields: # Check for subfields 
        self.PrintEvent(value, prefix=f"{full_field}.")  # Recurse into subfields
      else: # If no further subfields, print the full field and value
        print(f'{full_field}: {value}')
    return

  def PrintNEvents(self, array_, n=1):
    ''' Print n events human readable form '''
    print(f"\n---> Printing {n} event(s)...\n")
    for i, event in enumerate(array_, start=1): # Iterate event-by-event 
      print(f'-------------------------------------------------------------------------------------')
      self.PrintEvent(event) # Call self.print_event() 
      print(f'-------------------------------------------------------------------------------------\n')
      if i == n: # Return if 'n' is reached
        return 
                 
class Plot:
  def __init__(self):
    ''' Placeholder init '''
    pass  
    
  def PlotValueHist(self, leafname, vectorreq, sid, low, hi, xaxis_label, scale='linear'):
    """ make basic plot of magnitude of leafname value at tracker ent, mid or ext (specify sid) """
    
    # import code and extract branch
    tree = self.ImportTree()
    branch = self.ImportBranches(tree, [leafname])

    # take the chosen position to evaluate
    trk_mask = (branch[str(leafname)]['sid']==sid)

    # apply mask
    values = branch[(trk_mask)]
    
    fig, ax = plt.subplots(1,1)
    n, bins, patches = ax.hist(ak.flatten(values, axis=None), bins=100, range=(int(low), int(hi)), histtype='step',color='r')

    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    yerrs = []
    for i, j in enumerate(n):
      yerrs.append(math.sqrt(j))
    plt.errorbar(bin_centers, n, yerr=np.sqrt(n), fmt='r.')

    # add in style features:
    ax.set_yscale(str(scale))
    ax.set_xlabel(str(xaxis_label))
    ax.set_ylabel('# events per bin')
    ax.grid(True)
    #ax.legend()
    plt.show()
    
  def PlotMagValueHist(self, leafname, vectorreq, sid, low, hi, xaxis_label, scale='log'):
    """ make basic plot of magnitude of leafname value at tracker ent, mid or ext (specify sid) """
    
    vect = self.GetVectorXYZ(leafname, vectorreq, sid)

    fig, ax = plt.subplots(1,1)
    n, bins, patches = ax.hist(ak.flatten(vect.mag, axis=None), bins=100, range=(int(low), int(hi)), histtype='step',color='r')

    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    yerrs = []
    for i, j in enumerate(n):
      yerrs.append(math.sqrt(j))
    plt.errorbar(bin_centers, n, yerr=np.sqrt(n), fmt='r.')

    # add in style features:
    ax.set_yscale(str(scale))
    ax.set_xlabel(str(xaxis_label))
    ax.set_ylabel('# events per bin')
    ax.grid(True)
    #ax.legend()
    plt.show()

  ''' 
   Generic plotting utils below:
   * Formatting
   * Statitics
   * 1D histogram (includes weighting)
   * 1D histogram overlay hist
   * 2D histogram (includes weighting)
   * Graph with errors
   * Graph with errors overlay
  '''

  # Colours
  col_ = [
      (0., 0., 0.),                                                   # Black
      (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),  # Red
      (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),  # Blue
      (0.17254901960784313, 0.6274509803921569, 0.17254901960784313), # Green
      (1.0, 0.4980392156862745, 0.054901960784313725),                # Orange
      (0.5803921568627451, 0.403921568627451, 0.7411764705882353),    # Purple
      (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),  # Cyan
      (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),   # Pink
      (0.5490196078431373, 0.33725490196078434, 0.29411764705882354), # Brown
      (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),   # Gray 
      (0.7372549019607844, 0.7411764705882353, 0.13333333333333333)   # Yellow
  ]

  def RoundToSigFig(self, val, sf):
    ''' 
      Round a value to a specified number of significant figures 
    ''' 
    if val == 0 or math.isnan(val): # Edge cases
      return val
    else:
      # Determine the order of magnitude
      mag = math.floor(math.log10(abs(val))) 
      # Calculate the scale factor
      scale = 10 ** (sf - mag - 1)
      # Round to the nearest number of significant figures
      return round(val * scale) / scale

  def GetStats(self, array_, xmin, xmax): 
    ''' 
      Stats for 1D histograms
    '''
    array_ = ak.to_numpy(array_) # Convert to numpy array
    n_entries = len(array_) # Number of entries
    mean = np.mean(array_) # Mean
    mean_err = stats.sem(array_) # Mean error (standard error on the mean from scipy)
    std_dev = np.std(array_) # Standard deviation
    std_dev_err = np.sqrt(std_dev**2 / (2*n_entries)) # Standard deviation error assuming normal distribution
    underflows = len(array_[array_ < xmin]) # Number of underflows
    overflows = len(array_[array_ > xmax]) # Number of overflows
    return n_entries, mean, mean_err, std_dev, std_dev_err, underflows, overflows

  def ScientificNotation(self, ax, cbar=None):
    ''' 
      Set scientific notation on axes
      Condition: log scale is not used and the absolute limit is >= 1e4 or <= 1e-4 
    '''
    # Access the max values of the axes
    xmax, ymax = ax.get_xlim()[1], ax.get_ylim()[1]
    if ax.get_xscale() != 'log' and (abs(xmax) >= 1e4 or abs(xmax) <= 1e-4): # x-axis 
      ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True)) # Use math formatting 
      ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) # Set scientific notation
      ax.xaxis.offsetText.set_fontsize(13) # Set font size
    if ax.get_yscale() != 'log' and (abs(ymax) >= 1e4 or abs(ymax) <= 1e-4): # y-axis
      ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
      ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
      ax.yaxis.offsetText.set_fontsize(13)
    if cbar is not None: # Colour bar 
        # Access the max value of the cbar range
        cmax = cbar.norm.vmax
        if abs(cmax) >= 1e4 or abs(cmax) <= 1e-4:
          cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))  # Use math formatting
          cbar.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # Set scientific notation
          cbar.ax.yaxis.offsetText.set_fontsize(13)  # ''
    return

  def Plot1D(
    self, array_, weights_=None, nbins=100, xmin=-1.0, xmax=1.0, 
    title=None, xlabel=None, ylabel=None, col='black', leg_pos='best', fout='hist.png', NDPI=300,
    stats=True, log_x=False, log_y=False, under_over=False, stat_errors=False, error_bars=False, show=True
  ): 
    """ Plot a 1D histogram from a flat array """
    # Create figure and axes
    fig, ax = plt.subplots()
    # Create the histogram 
    counts_, bin_edges_, _ = ax.hist(array_, bins=int(nbins), range=(xmin, xmax), histtype='step', edgecolor=col, linewidth=1.0, fill=False, density=False, weights=weights_)
    bin_centres_ = (bin_edges_[:-1] + bin_edges_[1:]) / 2
    bin_errors_ = 0 * len(bin_centres_)
    # Calculate errors
    if weights_ is None:
        bin_errors_ = np.sqrt(counts_)  # Poisson errors for unweighted data
    else:
        # Weighted errors: sqrt(sum(weights^2)) for each bin
        weights_squared_, _ = np.histogram(array_, bins=int(nbins), range=(xmin, xmax), weights=np.square(weights_))
        bin_errors_ = np.sqrt(weights_squared_)
    # Plot the histogram 
    if error_bars:
        ax.errorbar(bin_centres_, counts_, yerr=bin_errors_, linestyle='None', linewidth=1.0, ecolor=col, color=col, markersize=4, capsize=2, elinewidth=1)
    else:
        ax.hist(array_, bins=int(nbins), range=(xmin, xmax), histtype='step', edgecolor=col, linewidth=1.0, fill=False, density=False, weights=weights_)
    # Set x-axis limits
    ax.set_xlim(xmin, xmax)
    # Log scale 
    if log_x: ax.set_xscale('log')
    if log_y: ax.set_yscale('log')
    # Statistics
    N, mean, mean_err, std_dev, std_dev_err, underflows, overflows = self.GetStats(array_, xmin, xmax)
    # Create legend text (roughly imitating the ROOT statbox)
    leg_txt = f'Entries: {N}\nMean: {self.RoundToSigFig(mean, 3)}\nStd Dev: {self.RoundToSigFig(std_dev, 3)}'
    if stat_errors: leg_txt = f'Entries: {N}\nMean: {self.RoundToSigFig(mean, 3)}' + rf'$\pm$' + f'{self.RoundToSigFig(mean_err, 1)}\nStd Dev: {self.RoundToSigFig(std_dev, 3)}' rf'$\pm$' + f'{self.RoundToSigFig(std_dev_err, 1)}'
    if under_over: leg_txt += f'\nUnderflows: {underflows}\nOverflows: {overflows}'
    # Add legend to the plot
    if stats: ax.legend([leg_txt], loc=leg_pos, frameon=False, fontsize=13)
    # Formatting 
    ax.set_title(title, fontsize=15, pad=10)
    ax.set_xlabel(xlabel, fontsize=13, labelpad=10) 
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10) 
    # Set font size of tick labels on x and y axes
    ax.tick_params(axis='x', labelsize=13)  # Set x-axis tick label font size
    ax.tick_params(axis='y', labelsize=13)  # Set y-axis tick label font size
    # Scientific notation 
    self.ScientificNotation(ax)
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches='tight')
    if show: # Show
      plt.show()
    # Save 
    print('\n---> Wrote:\n\t', fout)
    # Clear memory
    plt.close()
    return
    
  def Plot1DOverlay(
    self, hists_dict_, nbins=100, xmin=-1.0, xmax=1.0,
    title=None, xlabel=None, ylabel=None, fout='hist.png', leg_pos='best', NDPI=300,
    log_x=False, log_y=False, include_black=False, show=False
  ):
    '''
      Overlay many 1D histograms from a dictionary of flat arrays 
      hists_ = { label_0 : array_0, ..., label_n : array_n }
    ''' 
    # Create figure and axes
    fig, ax = plt.subplots()
    # Iterate over the hists and plot each one
    for i, (label, hist) in enumerate(hists_dict_.items()):
      if not include_black:
        col = self.col_[i+1]
      ax.hist(hist, bins=nbins, range=(xmin, xmax), histtype='step', edgecolor=col, linewidth=1.0, fill=False, density=False, color=col, label=label)
    # Log scale 
    if log_x: 
      ax.set_xscale('log')
    if log_y: 
      ax.set_yscale('log') 
    # Set x-axis limits
    ax.set_xlim(xmin, xmax)
    ax.set_title(title, fontsize=15, pad=10)
    ax.set_xlabel(xlabel, fontsize=13, labelpad=10) 
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10) 
    # Set font size of tick labels on x and y axes
    ax.tick_params(axis='x', labelsize=13)  # Set x-axis tick label font size
    ax.tick_params(axis='y', labelsize=13)  # Set y-axis tick label font size
    # Scientific notation
    self.ScientificNotation(ax)
    # Add legend to the plot
    ax.legend(loc=leg_pos, frameon=False, fontsize=12)
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches='tight')
    if show: # Show
      plt.show()
    # Clear memory
    plt.close()
    print('\n---> Wrote:\n\t', fout)
    return
  
  def Plot2D(
      self, x_, y_, weights_=None, nbins_x=100, xmin=-1.0, xmax=1.0, nbins_y=100, ymin=-1.0, ymax=1.0,
      title=None, xlabel=None, ylabel=None, zlabel=None, fout='hist.png', cmap='inferno', NDPI=300, 
      log_x=False, log_y=False, log_z=False, cb=True, show=True
  ):
    ''' 
      Plot a 2D histogram from two flat arrays of the same length 
    '''
    # Convert to numpy
    x_ = ak.to_numpy(x_)
    y_ = ak.to_numpy(y_)
    # Filter out empty entries
    valid_indices_ = [i for i in range(len(x_)) if np.any(x_[i]) and np.any(y_[i])]
    x_ = [x_[i] for i in valid_indices_]
    y_ = [y_[i] for i in valid_indices_]
    if weights_ is not None:
      weights_ = [weights_[i] for i in valid_indices_]
    # Check if the input arrays are not empty and have the same length
    if len(x_) == 0 or len(y_) == 0:
        raise ValueError("Input arrays are empty.")
    if len(x_) != len(y_):
        raise ValueError("Input arrays are of different length.")
    # Create 2D histogram
    hist, _, _ = np.histogram2d(x_, y_, bins=[int(nbins_x), int(nbins_y)], range=[[xmin, xmax], [ymin, ymax]], weights=weights_)
    # Set up the plot
    fig, ax = plt.subplots()
    # Setup normalisation
    norm = colors.Normalize(vmin=np.min(hist), vmax=np.max(hist))  
    # Log scale
    if log_x: 
      ax.set_xscale('log')
    if log_y: 
      ax.set_yscale('log') 
    if log_z:
        norm = colors.LogNorm(vmin=1, vmax=np.max(hist)) 
    # Plot the 2D histogram
    im = ax.imshow(hist.T, cmap=cmap, extent=[xmin, xmax, ymin, ymax], aspect='auto', origin='lower', norm=norm) 
    # Add colourbar and format it
    cbar=None
    if cb: 
     cbar = plt.colorbar(im)
     cbar.ax.tick_params(labelsize=13)  # Adjust font size  
     cbar.set_label(zlabel, fontsize=13, labelpad=10)
    # Format titles
    plt.title(title, fontsize=15, pad=10)
    plt.xlabel(xlabel, fontsize=13, labelpad=10)
    plt.ylabel(ylabel, fontsize=13, labelpad=10)
    # Set tick label font size
    ax.tick_params(axis='x', labelsize=13)  
    ax.tick_params(axis='y', labelsize=13) 
    # Scientific notation
    self.ScientificNotation(ax, cbar)
    # Draw 
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches="tight")
    if show: # Show
      plt.show()
    # Clear memory
    plt.close()
    print("\n---> Wrote:\n\t", fout)
    return
  
  def PlotGraph(
      self, x_, y_, xerr_=None, yerr_=None,
      xmin=None, xmax=None, ymin=None, ymax=None,
      title=None, xlabel=None, ylabel=None,
      col='black', linestyle='None', fout='graph.png', show=True, NDPI=300
    ):
    ''' 
    Plot a scatter graph with error bars (if included)
    ''' 
    # Create figure and axes
    fig, ax = plt.subplots()
    if xerr_ is None: # If only using yerr
      xerr_ = [0] * len(x_) 
    if yerr_ is None: # If only using xerr 
      yerr_ = [0] * len(y_) 
    ax.errorbar(x_, y_, xerr=xerr_, yerr=yerr_, fmt='o', color=col, markersize=4, ecolor=col, capsize=2, elinewidth=1, linestyle=linestyle, linewidth=1)
    # Set axis limits
    if xmin is not None or xmax is not None:
        ax.set_xlim(left=xmin, right=xmax)
    if ymin is not None or ymax is not None:
        ax.set_ylim(bottom=ymin, top=ymax)
    # Set title, xlabel, and ylabel
    ax.set_title(title, fontsize=15, pad=10)
    ax.set_xlabel(xlabel, fontsize=13, labelpad=10) 
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10) 
    # Set font size of tick labels on x and y axes
    ax.tick_params(axis='x', labelsize=13)  
    ax.tick_params(axis='y', labelsize=13)  
    # Scientific notation
    self.ScientificNotation(ax) 
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches="tight")
    if show:
      plt.show()
    print("\n---> Wrote:\n\t", fout)
    # Clear memory
    plt.close()
    return
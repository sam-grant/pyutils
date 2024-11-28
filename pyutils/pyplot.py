#! /usr/bin/env python
import awkward as ak
import matplotlib.pyplot as plt
import math
import numpy as np
import vector
from scipy import stats
from matplotlib.ticker import ScalarFormatter
import matplotlib.colors as colors

class Plot:
  def __init__(self):
    """  Placeholder init """
    plt.style.use('mu2e.mplstyle')
    pass  
    
  def RoundToSigFig(self, val, sf):
    """  
      Round a value to a specified number of significant figures 
    """  
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
    """  
      Stats for 1D histograms
    """ 
    array_ = ak.to_numpy(array_) # Convert to numpy array
    n_entries = len(array_) # Number of entries
    mean = np.mean(array_) # Mean
    mean_err = stats.sem(array_) # Mean error (standard error on the mean from scipy)
    std_dev = np.std(array_) # Standard deviation
    std_dev_err = np.sqrt(std_dev**2 / (2*n_entries)) # Standard deviation error assuming normal distribution
    underflows = len(array_[array_ < xmin]) # Number of underflows
    overflows = len(array_[array_ > xmax]) # Number of overflows
    return n_entries, mean, mean_err, std_dev, std_dev_err, underflows, overflows

  def ScientificNotation(self, ax, cbar=None): #FIXME - we might want to make the extreme ranges bigger
    """  
      Set scientific notation on axes
      Condition: log scale is not used and the absolute limit is >= 1e4 or <= 1e-4 
    """ 
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

  def Plot1D( self, array_, weights_=None, nbins=100, xmin=-1.0, xmax=1.0, 
    title=None, xlabel=None, ylabel=None, col='black', leg_pos='best', fout='hist.png', NDPI=300,
    stats=True, log_x=False, log_y=False, under_over=False, stat_errors=False, error_bars=False, show=True): 
    """ Plot a 1D histogram from a flat array """
    
    # Create figure and axes
    fig, ax = plt.subplots()
    
    # Create the histogram 
    counts_, bin_edges_, _ = ax.hist(array_, bins=int(nbins), range=(xmin, xmax), histtype='step', edgecolor=col,  fill=False, density=False, weights=weights_)
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
        ax.errorbar(bin_centres_, counts_, yerr=bin_errors_, ecolor=col, fmt='.', color=col, capsize=2, elinewidth=1)
    else:
        ax.hist(array_, bins=int(nbins), range=(xmin, xmax), histtype='step', edgecolor=col, fill=False, density=False, weights=weights_)
        
    # Set x-axis limits
    ax.set_xlim(xmin, xmax)
    
    # Log scale 
    if log_x: 
      ax.set_xscale('log')
    if log_y: 
      ax.set_yscale('log')
      
    # Statistics
    N, mean, mean_err, std_dev, std_dev_err, underflows, overflows = self.GetStats(array_, xmin, xmax)
    
    # Create legend text (roughly imitating the ROOT statbox)
    leg_txt = f'Entries: {N}\nMean: {self.RoundToSigFig(mean, 3)}\nStd Dev: {self.RoundToSigFig(std_dev, 3)}'
    
    # stats box
    if stat_errors: 
      leg_txt = f'Entries: {N}\nMean: {self.RoundToSigFig(mean, 3)}' + rf'$\pm$' + f'{self.RoundToSigFig(mean_err, 1)}\nStd Dev: {self.RoundToSigFig(std_dev, 3)}' rf'$\pm$' + f'{self.RoundToSigFig(std_dev_err, 1)}'
    if under_over: 
      leg_txt += f'\nUnderflows: {underflows}\nOverflows: {overflows}'
    
    # Add legend to the plot
    if stats: 
      ax.legend([leg_txt], loc=leg_pos)
    
    # Formatting 
    ax.set_title(title)
    ax.set_xlabel(xlabel) 
    ax.set_ylabel(ylabel) 

    # Scientific notation 
    self.ScientificNotation(ax)
    
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches='tight')
    
    # Show (for interactive use)
    if show: 
      plt.show()
      
    # Save 
    print('\n---> Wrote:\n\t', fout)
    
    # Clear memory
    plt.close()
    return
    
  def Plot1DOverlay( self, hists_dict_, nbins=100, xmin=-1.0, xmax=1.0, title=None, xlabel=None, ylabel=None, fout='hist.png', leg_pos='best', NDPI=300, log_x=False, log_y=False, show=False):
    """ 
      Overlay many 1D histograms from a dictionary of flat arrays 
      hists_ = { label_0 : array_0, ..., label_n : array_n }
    """
    
    # Create figure and axes
    fig, ax = plt.subplots()
    
    # Iterate over the hists and plot each one
    for i, (label, hist) in enumerate(hists_dict_.items()):
      ax.hist(hist, bins=nbins, range=(xmin, xmax), histtype='step', fill=False, density=False, label=label)
      
    # Log scale 
    if log_x: 
      ax.set_xscale('log')
    if log_y: 
      ax.set_yscale('log') 
      
    # Set x-axis limits
    ax.set_xlim(xmin, xmax)
    ax.set_title(title)
    ax.set_xlabel(xlabel) 
    ax.set_ylabel(ylabel) 
    
    # Scientific notation
    self.ScientificNotation(ax)
    # Add legend to the plot
    ax.legend(loc=leg_pos)
    
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches='tight')
    
    # Show
    if show:
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
    """  
      Plot a 2D histogram from two flat arrays of the same length 
    """ 
    
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
     cbar.set_label(zlabel)
     
    # Format titles
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
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
      title=None, xlabel=None, ylabel=None,
      xmin=None, xmax=None, ymin=None, ymax=None,
      col='black', linestyle='None', fout='graph.png',
      log_x=False, log_y=False, show=True, NDPI=300
    ):
    """  
    Plot a scatter graph with error bars (if included)
    """  
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
    if log_x: 
        ax.set_xscale("log")
    if log_y: 
        ax.set_yscale("log")
    # Set title, xlabel, and ylabel
    ax.set_title(title, fontsize=15, pad=10)
    ax.set_xlabel(xlabel, fontsize=13, labelpad=10) 
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10) 
    # Set font size of tick labels on x and y axes
    ax.tick_params(axis='x', labelsize=13)  
    ax.tick_params(axis='y', labelsize=13)  
    # TODO: scientific notation for graphs
    # self.ScientificNotation(ax) 
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches="tight")
    if show:
      plt.show()
    print("\n---> Wrote:\n\t", fout)
    # Clear memory
    plt.close()
    return
  
  def PlotGraphOverlay(
      self, graphs_, xerr_=None, yerr_=None,
      title=None, xlabel=None, ylabel=None,
      xmin=None, xmax=None, ymin=None, ymax=None,
      leg_pos='best', linestyle='None', fout='graph.png',
      log_x=False, log_y=False, show=True, NDPI=300
    ):
    """  
      Overlay many scatter graphs
    """  
    # Create figure and axes
    fig, ax = plt.subplots()
    # Loop through graphs and plot
    for i, (label, graph_) in enumerate(graphs_.items()):
      # Just to be explicit
      x_ = graph_[0]
      y_ = graph_[1]
      xerr_ = graph_[2]
      yerr_ = graph_[3]
      # Error bars
      if xerr_ is None: # If only using yerr
        xerr_ = [0] * len(x_) 
      if yerr_ is None: # If only using xerr 
        yerr_ = [0] * len(y_) 

      # Plot
      ax.errorbar(x_, y_, xerr=xerr_, yerr=yerr_, fmt='o',  label=label, markersize=4, capsize=2, elinewidth=1, linestyle=linestyle, linewidth=1)
    # Set axis limits
    if xmin is not None or xmax is not None:
        ax.set_xlim(left=xmin, right=xmax)
    if ymin is not None or ymax is not None:
        ax.set_ylim(bottom=ymin, top=ymax)
    if log_x: 
        ax.set_xscale("log")
    if log_y: 
        ax.set_yscale("log")
    # Set title, xlabel, and ylabel
    ax.set_title(title, fontsize=15, pad=10)
    ax.set_xlabel(xlabel, fontsize=13, labelpad=10) 
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10) 
    # Set font size of tick labels on x and y axes
    ax.tick_params(axis='x', labelsize=13)  
    ax.tick_params(axis='y', labelsize=13)  
    # TODO: scientific notation for graphs
    # self.ScientificNotation(ax) 
    # Legend
    ax.legend(loc=leg_pos, frameon=False, fontsize=13)
    # Draw
    plt.tight_layout()
    plt.savefig(fout, dpi=NDPI, bbox_inches="tight")
    if show:
      plt.show()
    print("\n---> Wrote:\n\t", fout)
    # Clear memory
    plt.close()
    return

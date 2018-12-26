# load magics
#%load_ext rpy2.ipython

# load python libraries
import pandas as pd
import numpy as np
import sys
import scipy as scipy

#add source directory to path
#sys.path.append('/ifs/devel/projects/proj030/src')

from IPython.core.display import HTML

def htmltab(df):
    display(HTML(df.to_html()))




# source R functions
#%R source("/ifs/devel/projects/proj030/src/ipython.R")

# setup database variables.



# set some useful variables

'''
  Greedy Weighted Set Cover
'''

import random
import sys
import subprocess
import mimetypes
import array as arr
import os
import numpy as np
import time
import datetime
from os import listdir
from os.path import join, isdir, realpath
from optparse import OptionParser
import helper
import greedy_sc

def main(inputdir, outputdir):
    
  ## the smaller the file relative to the maximum file size the better
  ## weight(S) = max{S' \in F}{S'.property}/S.property
  maxsize = max(helper.dict_sizes.values())
  weights = { f: size/maxsize for (f, size) in helper.dict_sizes.items()}
  # for example, for dict_sizes = {'a': 3, 'b': 4} the dictionary weights 
  # will be {'a': 0.75, 'b': 1.0}, which means the weight associate with 
  # file a will be bigger as we divide the term by the weight.

  ## used the same algorith as unweighted set cover
  greedy_sc.run(inputdir, outputdir, weights)

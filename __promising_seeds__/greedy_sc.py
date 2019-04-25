'''
  Greedy Set Cover
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

def main(inputdir, outputdir):
  run(inputdir, outputdir, weights=None)

def run(inputdir, outputdir, weights):
  ######################################
  #  Pseudo-code as per USENIX'14 paper:
  #
  #  U = X     <-- uncovered
  #  C = empty <-- selection
  #  while U not empty
  #    S = max{S \in F} |S \inter U|/w(S)
  #    C = C \union S
  #    U = U \ S
  #  return C
  ######################################
  uncovered = set(helper.dict_branches.values()) ## U (sequential ids of branches)
  selection = set()                              ## C
  while (len(uncovered) != 0):
    ## find file that covers more uncovered branches
    maxcov = 0
    max_file = None
    for f in helper.dict_id_filename.keys():
      tmp = len(set(helper.dict_coverage[f]).intersection(uncovered))
      if (not weights is None):
         tmp = tmp / weights[helper.dict_id_filename[f]]
      if (tmp > maxcov):
        maxcov = tmp
        max_file = f
    if (max_file == None):
      raise "fatal error!"
    ## update selection
    selection = selection.union({max_file})
    ## update set of uncovered branches
    uncovered = uncovered.difference(helper.dict_coverage[max_file])
    print("#uncovered {}, #selected: {}\r".format(len(uncovered), len(selection)), end='')

  ## saving files to the output
  print("saving files to the output...")
  for id in selection:
    filename = join(inputdir, helper.dict_id_filename[id])
    filename = filename[0:filename.find(".cov")]
    if (subprocess.call(["cp", filename, join(helper.this_dir_path, outputdir)])==1):
        raise Exception("fatal error!")
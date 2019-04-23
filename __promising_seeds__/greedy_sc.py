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

def main(inputdir, outputdir, pgmcall):
  helper.load_data(outputdir, inputdir, pgmcall)
  run(inputdir, outputdir, None)

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
    if (subprocess.call(["cp", filename, join(helper.this_dir_path, outputdir)])==1):
        raise Exception("fatal error!")


if __name__ == "__main__":
    ## reading command-line options
    (options, args) = helper.process_options()
    main(options.inputdir, options.outputdir, args[0].split())
    # pgmdir = "/home/damorim/Software/libpng-1.6.36/"
    # main(inputdir=join(pgmdir, "afl_in"), outputdir=join(helper.this_dir_path, "OUT"+datetime.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d-%H:%M:%S')), pgmcall=[join(pgmdir, "pngimage"), "@@"])
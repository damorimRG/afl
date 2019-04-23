import random
import sys
import subprocess
import mimetypes
import array as arr
import os
import numpy as np
import time
import datetime
import BitVector as bv
import helper

from os import listdir
from os.path import join, isdir, realpath
from optparse import OptionParser


def main(inputdir, outputdir, pgmcall):

    helper.load_data(outputdir, inputdir, pgmcall)

    print("optimizing...")
    (current_best, obj1, obj2) = optimize()

    print("generating files...")
    num = 0
    for val in current_best:
        if val == 1:
            filename = join(inputdir, helper.dict_id_filename[num])
            if (subprocess.call(["cp", filename, join(helper.this_dir_path, outputdir)])==1):
                raise Exception("fatal error!")
        num += 1

    print("Fitness ({},{}). {} files were selected.".format(obj1, obj2, current_best.count(1)))
    
## 
# MOSA (Multi-Objective Simulated Annealing) optimization
##

def optimize():
    random.seed(helper.seed)
    ## initial individual
    ind = [1] * helper.num_files
    a_orig, b_orig = eval(selection=ind, file_index=-1) # evaluate original fitness
    ## one round of optimization
    search_order = list(range(helper.num_files)) ## list 0..numFiles-1
    random.shuffle(search_order) ## shuffle elements in this list
    ## create best individual
    current_best = ind.copy()
    num = 0.0
    for x in search_order:
        print("  {}% completed\r".format(round(100*num/helper.num_files, 2)), end='')
        num += 1
        current_best[x] = 0 # set to 0
        a_mod, b_mod = eval(selection=current_best, file_index=x)
        # print("({},{})".format(a_mod, b_mod))
        if (a_orig == a_mod and b_mod < b_orig) :
            # local optimum
            a_orig = a_mod
            b_orig = b_mod
        else: # undo
            current_best[x] = 1
            increment_counters(x)    
    return (current_best, a_orig, b_orig)
        
######################## 
# evaluate fitness
########################

## caching results for efficiency!
branch_counters = None

def increment_counters(file_index):
    for b in helper.dict_coverage[file_index]:
        branch_counters[b] = branch_counters[b] + 1

def decrement_counters(file_index):
    for b in helper.dict_coverage[file_index]:
        branch_counters[b] = branch_counters[b] - 1

def eval(selection, file_index):
    global branch_counters
    if (branch_counters == None):
        branch_counters = [0] * helper.num_branches
        ## initialize counters
        for index in range(len(selection)):
            increment_counters(index)
    else:
        decrement_counters(file_index)

    # number of coverage branches is the same as number of non-zero counters 
    num_covered_branches = len(branch_counters) - branch_counters.count(0)
    # number of covered branches
    objective1 = 1 - num_covered_branches / helper.num_branches
    # number of tests selected
    objective2 = selection.count(1) / helper.num_files

    return (objective1, objective2)

if __name__ == "__main__":
    ## reading command-line options
    (options, args) = helper.process_options()
    main(options.inputdir, options.outputdir, args[0].split())

    # pgmdir = "/home/damorim/Software/libpng-1.6.36/"
    # main(inputdir=join(pgmdir, "afl_in"), outputdir=join(helper.this_dir_path, "OUT"+datetime.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d-%H:%M:%S')), pgmcall=[join(pgmdir, "pngimage"), "@@"])

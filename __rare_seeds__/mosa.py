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

from os import listdir
from os.path import join, isdir, realpath
from optparse import OptionParser

this_dir_path = os.path.dirname(os.path.realpath(__file__))
dict_branches = {} # real-id -> sequential-id
num_branches = 0
num_files = 0       # number of files
dict_coverage = {} # index of file -> coverage list (of sequential ids)
dict_sizes = {}    # filename -> size
dict_id_filename = {}
seed = 99  ## random number. TODO: should be parameter

def main(inputdir, outputdir, pgmcall):
    global dict_branches, num_branches, num_files, dict_coverage, dict_sizes, dict_id_filename

    outdirname = join(outputdir, '.traces')

    ##
    ## compute coverage using a simplified version of the afl-cmin script
    ##
    os.chdir("..")
    cmd = ["afl-mo-coverage", "-i", inputdir, "-o", outputdir, "--"] + pgmcall

    print("---> {}".format(cmd))
    if (subprocess.call(cmd)==1):
        raise Exception("fatal error!")
    print()
    os.chdir(this_dir_path)

    ##
    # compute branch-id map: dict_branches, num_branches
    ##
    p1 = subprocess.Popen(["cat " + outdirname + "/*"], shell=True, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sort", "-n"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["uniq"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p2.stdout.close()
    (output, err) = p3.communicate()
    if (err != None):
        raise Exception("fatal error!")
    dict_branches={}
    num = 0
    for id in output.decode(encoding='UTF-8').split():
        id = int(id)
        # update maps
        dict_branches[id] = num 
        num += 1
    num_branches=num
    
    ##
    # coverage matrix: dict_coverage
    ##
    dict_coverage = {}    
    # this_dir = os.path.dirname(os.path.realpath(__file__)) 
    # mosa_dir = join(this_dir, "mosa/")
    # inputs_dir = join(mosa_dir, "inputs/")
    dict_filename_id = {}
    dict_id_filename = {}
    num = 0
    ## process each trace file
    print("generating coverage matrix...")
    for filename in listdir(outdirname):
        print("  processing file {}\r".format(num+1), end='')
        fullpath = join(outdirname, filename)
        if (not filename.startswith("id:")): 
            continue
        dict_filename_id[filename] = num
        dict_id_filename[num] = filename
        ## generate coverage matrix
        # bitlist = [0] * num_branches
        branches = []
        ## read trace file and store (sequential ids of) branches in a list
        with open(fullpath, 'r', encoding="ISO-8859-1") as tracefile:
            for branch in tracefile.readlines():
                real_id = int(branch.rstrip())
                seq_id = dict_branches[real_id]
                branches.extend([seq_id])
        dict_coverage[num] = branches
        num+=1
    num_files = len(dict_coverage)
    
    ##
    # collect file sizes
    ##
    print("\ncollecting file sizes...")
    dict_sizes = {}
    for filename in listdir(inputdir):
        if (not filename.startswith("id:")):
            continue
        size = os.path.getsize(join(inputdir, filename))
        dict_sizes[filename] = int(size)


    print("optimizing...")
    solution = optimize()
    print("\nbest solution--> objective-1={}, objective-2={}, solution={}".format(solution[1], round(solution[2],2), solution[0]))

    
## 
# MOSA (Multi-Objective Simulated Annealing) optimization
##

def optimize():
    random.seed(seed)
    ## initial individual
    ind = [1] * num_files
    a_orig, b_orig = eval(selection=ind, file_index=-1) # evaluate original fitness
    ## one round of optimization
    search_order = list(range(num_files)) ## list 0..numFiles-1
    random.shuffle(search_order) ## shuffle elements in this list
    ## create best individual
    current_best = ind.copy()
    num = 0.0
    for x in search_order:
        print("  {}% completed\r".format(round(100*num/num_files, 2)), end='')
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
    for b in dict_coverage[file_index]:
        branch_counters[b] = branch_counters[b] + 1

def decrement_counters(file_index):
    for b in dict_coverage[file_index]:
        branch_counters[b] = branch_counters[b] - 1

def eval(selection, file_index):
    global branch_counters
    if (branch_counters == None):
        branch_counters = [0] * num_branches
        ## initialize counters
        for index in range(len(selection)):
            increment_counters(index)
    else:
        decrement_counters(file_index)

    # number of coverage branches is the same as number of non-zero counters 
    num_covered_branches = len(branch_counters) - branch_counters.count(0)
    # number of covered branches
    objective1 = 1 - num_covered_branches / num_branches
    # number of tests selected
    objective2 = selection.count(1) / num_files

    return (objective1, objective2)


def process_options():
    parser = OptionParser(usage = "afl-mo-selection [options] target", description="Multi-objective seed selection algorithm. It takes into account a number of factors to minimize the seed corpus. For example, seed coverage, number of seeds, and the seed size.")
    parser.add_option("-i", "--input", dest="inputdir", 
                    help="input directory where to read seed files", metavar="DIRECTORY")
    parser.add_option("-o", "--output", dest="outputdir", 
                    help="output directory where selected files will be stored", metavar="DIRECTORY")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments! For help, type:\n$> python afl-mo-selection --help\n")
    return (options, args)

if __name__ == "__main__":
    ## reading command-line options
    # (options, args) = process_options()
    # main(options.inputdir, options.outputdir, args[0].split())

    pgmdir = "/home/damorim/Software/libpng-1.6.36/"
    main(inputdir=join(pgmdir, "afl_in"), outputdir=join(this_dir_path, "OUT"+datetime.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d-%H:%M:%S')), pgmcall=[join(pgmdir, "pngimage"), "@@"])

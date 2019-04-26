import random
import sys
import subprocess
import mimetypes
import array as arr
import os
import numpy as np
import time
import datetime
import re 
import zlib

from os import listdir
from os.path import join, isdir, realpath
from optparse import OptionParser

this_dir_path = os.path.dirname(os.path.realpath(__file__))
dict_branches = {}    # real-id -> sequential-id
num_branches = 0
num_files = 0         # number of files
dict_coverage = {}    # index of file -> coverage list (of sequential ids)
dict_sizes = {}       # filename -> size
dict_id_filename = {} # seq-file -> file-name
seed = 99  ## random number. TODO: should be parameter

def load_data_afl(outputdir, inputdir, pgmcall):
    global dict_branches, num_branches, num_files, dict_coverage, dict_sizes, dict_id_filename

    outdirname = join(outputdir, '.traces')

    ##
    ## compute coverage using a simplified version of the afl-cmin script
    ##
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
    return dict_id_filename

def load_data_libfuzzer(cov_dirname):
    global dict_branches, num_branches, num_files, dict_coverage, dict_sizes, dict_id_filename
    seq_covid = 0
    seq_fileid = 0
    for filename in listdir(cov_dirname):
        all_items = []
        current_target = None
        with open(join(cov_dirname, filename), 'r', encoding="ISO-8859-1") as testfile:
            for line in testfile.readlines():
                line = line.strip()
                if (line.startswith("file size")):
                    x = line[line.find(":")+1:len(line)]
                    dict_sizes[filename] = int(x)
                elif line.endswith(".h") or line.endswith(".c"):
                    current_target = line
                elif current_target is not None: ## assuming it is a covered line in the format DA:x,y
                    x = line[line.find(":")+1: line.find(",")]
                    hashme = zlib.adler32(bytes(current_target + x, 'utf-8'))
                    try:
                        thisseq = dict_branches[hashme]
                    except KeyError:
                        thiseq = seq_covid
                        dict_branches[hashme] = seq_covid
                        seq_covid = seq_covid + 1 # unseen item, create new sequential for it 
                    finally:                       
                        all_items.append(thiseq)
        dict_id_filename[seq_fileid] = filename
        dict_coverage[seq_fileid] = all_items
        seq_fileid = seq_fileid + 1
    num_branches = len(dict_branches)
    num_files = len(dict_coverage)

def process_options():
    parser = OptionParser(usage = "<selection-algo> [options] target", description="Seed selection algorithm. It takes into account a number of factors to minimize the seed corpus. For example, seed coverage, number of seeds, and the seed size.")
    parser.add_option("-i", "--input", dest="inputdir", 
                    help="input directory where to read seed files", metavar="DIRECTORY")
    parser.add_option("-o", "--output", dest="outputdir", 
                    help="output directory where selected files will be stored", metavar="DIRECTORY")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments! For help, type:\n$> python afl-mo-selection --help\n")
    return (options, args)

if __name__ == '__main__':
    load_data_libfuzzer(None)
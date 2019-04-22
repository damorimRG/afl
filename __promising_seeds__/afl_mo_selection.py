import sys
import subprocess
import mimetypes
import array as arr
import os
import numpy as np

from os import listdir
from os.path import join, isdir, realpath
from optparse import OptionParser

def main(inputdir, outputdir, pgmcall):
    
    outdirname = join(outputdir, '.traces')
    
    ## compute coverage using a simplified version of the afl-cmin script
    cmd = ["afl-mo-coverage", "-i", inputdir, "-o", outputdir, "--"] + pgmcall

    print("---> {}".format(cmd))
    if (subprocess.call(cmd)==1):
        raise Exception("fatal error!")
    print()

    #########################################################################
    # Quick access to the data is important for the performance of the 
    # optimization algorithm. As such, we need to map branch ids (tuples?)
    # and file ids to sequential numbers. This enables the genetic algorithm
    # (see dir. nsga2) to quickly access the data using vectors.
    #########################################################################

    ##
    # - create file .cov-ids mapping the ids of the branches covered by the 
    # seed files with sequential numbers 0..numbranches-1
    ##
    ## "/.traces/*"
    p1 = subprocess.Popen(["cat " + outdirname + "/*"], shell=True, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sort", "-n"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["uniq"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p2.stdout.close()
    (output, err) = p3.communicate()
    if (err != None):
        raise Exception("fatal error!")
    filename = join(outdirname, '.cov-ids')
    dict_branches={}
    with open(filename, 'w') as fileIds:
        num = 0
        for id in output.decode(encoding='UTF-8').split():
            id = int(id)
            fileIds.write("{} {}\n".format(num, id))
            dict_branches[id] = num # update map
            num+=1
    maxBranchId=num

    print(".............................. {} \n".format(maxBranchId))

    ###
    # - create file with integer ids of seed files 0..numfiles-1
    # - create coverage-matrix file (nsga2/input/test_coverage.data)
    ##
    ##this directory
    this_dir = os.path.dirname(os.path.realpath(__file__))
    nsga2_dir = join(this_dir, "nsga2/")
    covfilename = join(nsga2_dir, join("input/", 'test_coverage.data'))
    num = 0
    mapFileNameId = {}
    mapIdFileName = {}
    with open(join(outdirname, '.file-ids'), 'w') as fileIds, open(covfilename, 'w') as fileCoverage:
        for filename in listdir(outdirname):
            fullpath = join(outdirname, filename)
            if (not filename.startswith("id:")): #isdir(fullpath)
                continue
            fileIds.write("{} {}\n".format(num, filename))
            mapFileNameId[filename] = num
            mapIdFileName[num] = filename
            num+=1
            ## generate coverage matrix
            covList = ["0"] * maxBranchId
            with open(fullpath, 'r', encoding="ISO-8859-1") as seefile:
                for branch in seefile.readlines():
                    realIndex = int(branch.rstrip())
                    modIndex = dict_branches[realIndex]
                    covList[modIndex] = "1"
            fileCoverage.write(",".join(covList)+"\n")
            # show progress
            sys.stdout.write("\r")
            sys.stdout.write("computing coverage matrix. progress {}".format(num))
            sys.stdout.flush()
    
    ## collect file sizes
    sizes = [0] * len(mapFileNameId)
    for filename in listdir(inputdir):
        if (not filename.startswith("id:")):
            continue
        size = os.path.getsize(join(inputdir, filename))
        sizes[mapFileNameId[filename]] = str(size)
    filesizesfile = join(nsga2_dir, join("input/", 'file_sizes.data'))
    with open(filesizesfile, 'w') as file:
        file.write("\n".join(sizes))

    ##
    # - run nsga2 optimizer
    ##
    basedir=os.getcwd()
    os.chdir(nsga2_dir)
    
    if (subprocess.call(["make", "clean", "all"])==1):
        raise Exception("fatal error!")
    if (subprocess.call(["./nsga2r"])==1):
        raise Exception("fatal error!")
    
    ##
    # pick one solution and copy files to the output directory.
    # we pick best solution according to the first objective
    ##
    numObjectives = 3
    with open(join(nsga2_dir, "best_pop.out"), 'r') as bestpop:
        matrix = None
        for line in bestpop:
            if line.startswith("#"): continue
            fields = line.split()
            fields = list(map(float, fields))
            if matrix is None:
                matrix = np.array(fields)
            else:
                matrix = np.vstack((matrix, np.array(fields)))
    
    # sort best candidates by first objective (typically, coverage)
    matrix = np.sort(matrix.view(",".join(["f8"] * matrix.shape[1])), order=['f1'], axis=0).view(np.float)
    # select top pick
    index = matrix.shape[0]-1 ## sorted in descending order
    selection = matrix[index].tolist()
    fields = selection[numObjectives:len(selection)-3]
    ## copy selected files to output dir
    num = 0
    for val in fields:
        if val == 1.0:
            filename = join(inputdir, mapIdFileName[num])
            if (subprocess.call(["cp", filename, join(this_dir, outputdir)])==1):
                raise Exception("fatal error!")
        num += 1

    os.chdir(this_dir)

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
    (options, args) = process_options()
    main(options.inputdir, options.outputdir, args[0].split())

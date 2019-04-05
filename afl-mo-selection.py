import sys
import subprocess
import mimetypes
import array as arr
import os

from os import listdir
from os.path import join, isdir, realpath
from optparse import OptionParser

def main():
    (options, args) = process_options()
    dirname = join(options.outputdir, '.traces')
    
    ## compute coverage using a simplified version of the afl-cmin script
    cmd = ["afl-mo-coverage"] + sys.argv[1:len(sys.argv)-1] + ["--"] + args[0].split()
    if (subprocess.call(cmd)==1):
        raise Exception("fatal error!")
    print()

    #########################################################################
    # Quick access to the data is important for the performance of the 
    # optimization algorithm. As such, we need to map branch ids (tuples?)
    # and files ids to sequential numbers. This enables the genetic algorithm
    # (see selection_nsga2) to quickly access the data using vectors.
    #########################################################################

    ##
    # - create file .cov-ids mapping the ids of the branches covered by the 
    # seed files with sequential numbers 0..numbranches-1
    ##
    p1 = subprocess.Popen(["cat OUT/.traces/*"], shell=True, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sort", "-n"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["uniq"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p2.stdout.close()
    (output, err) = p3.communicate()
    if (err != None):
        raise Exception("fatal error!")
    filename = join(dirname, '.cov-ids')
    dict_branches={}
    with open(filename, 'w') as fileIds:
        num = 0
        for id in output.decode(encoding='UTF-8').split():
            id = int(id)
            fileIds.write("{} {}\n".format(num, id))
            dict_branches[id] = num # update map
            num+=1
    maxBranchId=num

    ###
    # - create file with integer ids of seed files 0..numfiles-1
    # - create coverage-matrix file (selection_nsga2/input/test_coverage.data)
    ##
    ##this directory
    this_dir = os.path.dirname(os.path.realpath(__file__))
    nsga2_dir = join(this_dir, "selection_nsga2/")
    covfilename = join(nsga2_dir, join("input/", 'test_coverage.data'))
    num = 0
    with open(join(dirname, '.file-ids'), 'w') as fileIds, open(covfilename, 'w') as fileCoverage:
        for filename in listdir(dirname):
            fullpath = join(dirname, filename)
            if (not filename.startswith("id:")): #isdir(fullpath)
                continue                
            fileIds.write("{} {}\n".format(num, filename))
            num+=1
            ## generate coverage matrix
            array = arr.array('I', [0] * maxBranchId)
            with open(fullpath, 'r', encoding="ISO-8859-1") as seefile:
                for branch in seefile.readlines():
                    realIndex = int(branch.rstrip())
                    modIndex = dict_branches[realIndex]
                    array[modIndex] = 1
            fileCoverage.write(",".join([str(n) for n in array])+"\n")
            # show progress
            sys.stdout.write("\r")
            sys.stdout.write("computing coverage matrix. progress {}".format(num))
            sys.stdout.flush()

    ##
    # - run nsga2 optimizer
    ##
    os.chdir(nsga2_dir)
    print(os.getcwd())
    if (subprocess.call(["make", "clean", "all"])==1):
        raise Exception("fatal error!")
    if (subprocess.call(["./nsga2r"])==1):
        raise Exception("fatal error!")
    
    ##
    # - pick one paretto-optimal solution and copy files to the output directory 
    ##
    with open(join(nsga2_dir, "best_pop.out"), 'r') as bestpop:
        print(bestpop.readlines())

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
    main()
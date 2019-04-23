#!/usr/bin/env python

import os
import subprocess
import shutil
import time
import datetime
import afl_mo_selection
import sys
from enum import Enum
from os.path import join
import greedy_sc
import greedy_wsc
import mosa

SUBJECTS=["/home/damorim/Software/libpng-1.6.36/pngimage @@"]
#SUBJECTS=["/home/damorim/Software/oss-fuzz/build/out/libjpeg-turbo/libjpeg_turbo_fuzzer @@"]

class Techniques(Enum):
    AFL_BASIC = 1
    AFL_MO_SELECTION = 2
    AFL_CMIN = 3
    AFL_GREEDY_UWSC = 4
    AFL_GREEDY_WSC_SIZE = 5

inputDIRname = "afl_in"
#inputDIRname = "/home/damorim/Software/oss-fuzz/build/out/libjpeg-turbo/afl-testcases/jpeg_turbo/full/images"
outputDIRname = "afl_out"

def main():
    this_dir_path = os.path.dirname(os.path.realpath(__file__))
    for x in SUBJECTS:
        # parse options from subject's name
        dirname, pgmname, args = parseOptions(x)
        
        for technique in Techniques:
            ## timestamp for the name of the stats file
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d-%H:%M:%S')
            # temporary output directory
            minSeedsTEMPODir = join(this_dir_path, "OUT"+timestamp)

            ###############
            ## minimization
            ###############
            os.chdir(dirname)
            if technique == Techniques.AFL_BASIC:
                continue
                ## for the basic technique there is no reduction
                minSeedsTEMPODir = inputDIRname
            elif technique == Techniques.AFL_MO_SELECTION:
                continue
                mosa.main(inputdir=join(dirname, inputDIRname), outputdir=minSeedsTEMPODir, pgmcall=[pgmname] + args)
            elif technique == Techniques.AFL_CMIN:
                cmd = ["afl-cmin", "-i", join(dirname,inputDIRname), "-o", minSeedsTEMPODir, pgmname, "".join(args)]
                if (subprocess.call(cmd)==1):
                    raise Exception("fatal error")
            elif technique == Techniques.AFL_GREEDY_UWSC:
                greedy_sc.main(inputdir=join(dirname, inputDIRname), outputdir=minSeedsTEMPODir, pgmcall=[pgmname] + args)
            elif technique == Techniques.AFL_GREEDY_WSC_SIZE:
                greedy_wsc.main(inputdir=join(dirname, inputDIRname), outputdir=minSeedsTEMPODir, pgmcall=[pgmname] + args)                
            else:
                raise Exception("fatal error")

            ###############
            ## invoking AFL
            ###############
            # changing directory to the target home dir
            os.chdir(dirname) 
            ## delete the output directory
            shutil.rmtree(outputDIRname, ignore_errors=True, onerror=None)
            # building path to invoke the program. Note that the input directory 
            # is the one with the minimized set of seeds
            cmd = ["afl-fuzz", "-i", minSeedsTEMPODir, "-o", outputDIRname, pgmname] + args 
            if (subprocess.call(cmd)==1):
                ## write this to a log file!
                print("fatal error!")
                sys.exit(1)
            else:
                print("copying file...")
                fname = this_dir_path + "/" + pgmname + "-" + str(technique) + "-" + timestamp + ".data"
                ## copying stat file
                shutil.copy(outputDIRname + '/plot_data', fname)

            ## delete temporary directory for seeds
            if (technique != Techniques.AFL_BASIC):
                shutil.rmtree(minSeedsTEMPODir, ignore_errors=False, onerror=None)

def parseOptions(x):
    cmd = x.split()
    parts=cmd[0].split("/")
    dirname="/".join(parts[:-1])
    pgmname=parts[len(parts)-1]
    args=cmd[1:]
    return dirname, pgmname, args
        
            
if __name__ == '__main__':
    main()

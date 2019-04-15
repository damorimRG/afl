import os
import subprocess
import shutil
import time
import datetime
import aflMOselection
import sys
from enum import Enum
from os.path import join


SUBJECTS=["/home/damorim/Software/libpng-1.6.36/pngimage @@"]

class Techniques(Enum):
    AFL_BASIC = 1
    AFL_MO_SELECTION = 2
    AFL_CMIN = 3

inputDIRname = "afl_in"
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
            minSeedsTEMPODir="OUT"+timestamp

            ###############
            ## minimization
            ###############
            os.chdir(dirname)
            if technique == Techniques.AFL_BASIC:
                ## for the basic technique there is no reduction
                minSeedsTEMPODir = inputDIRname
                continue ## remove this!
            elif technique == Techniques.AFL_MO_SELECTION:
                aflMOselection.main(inputdir=join(dirname, inputDIRname), outputdir=minSeedsTEMPODir, pgmcall=[pgmname] + args)
                sys.exit() ## stop here!
            elif technique == Techniques.AFL_CMIN:
                cmd = ["afl-cmin", "-i", join(dirname,inputDIRname), "-o", minSeedsTEMPODir, pgmname, "".join(args)]
                if (subprocess.call(cmd)==1):
                    raise Exception("fatal error")
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

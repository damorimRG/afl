import helper
import mosa
import greedy_sc
import greedy_wsc
import sys
from optparse import OptionParser

def main(options, args):
    ## process coverage data
    helper.load_data_libfuzzer(options.cov_dir)
    if options.tech_name == "mosa":
        mosa.main(inputdir=options.input_dir, outputdir=options.output_dir)
    elif options.tech_name == "greedy-uwsc":
        greedy_sc.main(inputdir=options.input_dir, outputdir=options.output_dir)        
    elif options.tech_name == "greedy-wsc-size":
        greedy_wsc.main(inputdir=options.input_dir, outputdir=options.output_dir)
    else:
        raise Exception("fatal error")

def process_options():
    parser = OptionParser(usage = "<selection-algo> [options] target", description="Seed selection algorithm. It takes into account a number of factors to minimize the seed corpus. For example, seed coverage, number of seeds, and the seed size.")
    parser.add_option("-t", "--technique", dest="tech_name", 
                    help="technique name. options: mosa, wsc", metavar="NAME")
    parser.add_option("-c", "--coverage", dest="cov_dir", 
                    help="location where coverage files are located", metavar="DIRECTORY")
    parser.add_option("-i", "--input", dest="input_dir", 
                    help="location where seed files are located", metavar="DIRECTORY")                    
    parser.add_option("-o", "--output", dest="output_dir", 
                    help="location where minimized set will be located", metavar="DIRECTORY")

    (options, args) = parser.parse_args()
    return (options, args)

if __name__ == "__main__":
#    sys.argv = ["", 
#    "--technique", "greedy-uwsc", 
#    "--coverage", "/home/damorim/projects/afl/__promising_seeds__/output/libjpeg-turbo", 
#    "--input", "/home/damorim/Software/oss-fuzz/build/out/libjpeg-turbo/src/afl-testcases/jpeg_turbo/full/images", 
#    "--output", "/home/damorim/projects/afl/__promising_seeds__/MINDIR-greedy-uwsc-2019.04.25-18:19:11"]
    ## reading command-line options
    (options, args) = process_options()
    main(options, args)
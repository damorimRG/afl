This file explains the AFL multi-objective seed selection algorithm.

Relevant files:

afl-mo-selection.py - file that drives the selection. it calls
                      afl-mo-coverage (to collect metrics) and
                      selection_nsga2/nsga2r (to optimize).

afl-mo-coverage - a trimmed copy of the afl-cmin script. we used it to
                  collect coverage metrics just as the original
                  script.

** under selection_nsga2 **

nsga2r.c - the entrypoint of the nsga2 optimizer that we adapted for
           our purpose. The important part is where we load the data
           from the input directory (selection_nsga2/inputs) into the
           datastructures (defined in global.h).

problemdef.c - the file defining the objective function
               "test_problem". Each index of the "obj" array denotes a
               different optimization objective.

global.h - the file with global data structures. the important ones
           are highlighted with comments "/* marcelo */".


To run the seed selection:

 Usage: python afl-mo-selection --input=<input-dir> --output=<output-dir> target

 Example:
 
 $> python afl-mo-selection.py -i /home/damorim/Software/binutils-2.25/afl_out/queue \
    -o OUT "/home/damorim/Software/binutils-2.25/binutils/readelf -a @@"

#!/bin/bash

## should be global
OSS_FUZZ_HOME="${HOME}/Software/oss-fuzz"
TIMEOUT=60 # in seconds

## MODIFY THIS TO RUN ANOTHER SUBJECT
FUZZER_BINARY="libjpeg_turbo_fuzzer"
FUZZER_PROJECT="libjpeg-turbo"
PROJECT_DIR=${OSS_FUZZ_HOME}/build/out/${FUZZER_PROJECT}
ORIGINAL_SEEDS_DIR=${PROJECT_DIR}/src/afl-testcases/jpeg_turbo/full/images
FUZZER=${OSS_FUZZ_HOME}/build/out/${FUZZER_PROJECT}/${FUZZER_BINARY}

# DERIVED VARS
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
COVERAGE_OUTPUT_DIR=${DIR}/output/${FUZZER_PROJECT}

## compiling subject if needed
if [ ! -d "${PROJECT_DIR}" ]; then
    ./build-project.sh $OSS_FUZZ_HOME $FUZZER_PROJECT
fi

## computing coverage per project
if [ ! -d "${COVERAGE_OUTPUT_DIR}" ]; then
    mkdir -p ${COVERAGE_OUTPUT_DIR}
fi

(cd $PROJECT_DIR;
 # iterate through seed files
 numfiles=$(ls ${ORIGINAL_SEEDS_DIR} | wc -l)
 counter=0
 echo "computing coverage for each seed file; it can take a few minutes (be patient)"
 pwd
 for TEST in `ls ${ORIGINAL_SEEDS_DIR}`;
 do
     counter=$((counter+1))
     echo -ne "files processed by llvm-cov ${counter}/${numfiles}\r"
     COV_FILE=${COVERAGE_OUTPUT_DIR}/$TEST.cov     
     ## report size
     echo "file size in bytes: $(wc -c < ${ORIGINAL_SEEDS_DIR}/${TEST})" > $COV_FILE
     # generate .profraw
     ./libjpeg_turbo_fuzzer -print_coverage=1 ${ORIGINAL_SEEDS_DIR}/$TEST  >> $COV_FILE 2>&1
     # generate .profdata
     llvm-profdata-9 merge -sparse *.profraw -o default.profdata
     # generate coverage data
     llvm-cov-9 export -format=lcov ${FUZZER_BINARY} -instr-profile=default.profdata |  grep -E "SF|DA" | grep -vE "FNDA|,0" >> $COV_FILE
     rm *.profraw default.profdata
 done
 echo "processed $counter files"
)

echo "REBUILDING PROJECT FOR FUZZING. Unfortunately, --sanitizer=coverage does not work in fuzzing mode."
(cd ${OSS_FUZZ_HOME};
 python infra/helper.py build_fuzzers --engine=libfuzzer $FUZZER_PROJECT
)

####
## fuzzing with different minimization technique
####
options=( mosa greedy-uwsc greedy-wsc-size ) # no-min 
for x in "${options[@]}"
do
    ## running minimization
    TIMESTAMP=`date +%Y.%m.%d-%H:%M:%S`
    LOG_FILE=${FUZZER_PROJECT}-${x}-${TIMESTAMP}.log
    OUT_DIR=`pwd`/OUT-${TIMESTAMP}
    mkdir ${OUT_DIR}
    case $x in
        "no-min")
            IN_DIR=${ORIGINAL_SEEDS_DIR}
            echo "-----no minimization-----"
            ;;
        *)
            MIN_DIR=`pwd`/MINDIR-$x-${TIMESTAMP}
            mkdir ${MIN_DIR}
            echo "minimizer=${x}"
            echo "python minimize.py --technique ${x} --coverage ${COVERAGE_OUTPUT_DIR} --input ${ORIGINAL_SEEDS_DIR} --output ${MIN_DIR}"
            python minimize.py --technique ${x} --coverage ${COVERAGE_OUTPUT_DIR} --input ${ORIGINAL_SEEDS_DIR} --output ${MIN_DIR}
            IN_DIR=${MIN_DIR}
            ;;
    esac
    ## FUZZING!
    echo "fuzzing for ${TIMEOUT}s. output in ${LOG_FILE}"
    echo "${FUZZER} -max_total_time=${TIMEOUT} ${IN_DIR} ${OUT_DIR}) &> ${LOG_FILE}"
    
    (./time.sh ${TIMEOUT} 1 & ${FUZZER} -max_total_time=${TIMEOUT} ${IN_DIR} ${OUT_DIR}) &> ${LOG_FILE}
    # removing output directory
    rm -rf ${OUT_DIR}
    rm -rf ${MIN_DIR}

    echo "final coverage ${x}:" $(grep "cov" ${LOG_FILE} | awk '{print $4}' | sort -n  | uniq | tail -n 1)
done

echo "done!"

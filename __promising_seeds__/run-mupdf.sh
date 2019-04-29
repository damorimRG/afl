#!/bin/bash

## should be global
export OSS_FUZZ_HOME="${HOME}/Software/oss-fuzz"
#export TIMEOUT=60 # in seconds
export TIMEOUT=7200 # in seconds

## MODIFY THIS TO RUN ANOTHER SUBJECT
export FUZZER_BINARY="pdf_fuzzer"                                             ## change
export FUZZER_PROJECT="mupdf"                                                 ## change
export PROJECT_DIR=${OSS_FUZZ_HOME}/build/out/${FUZZER_PROJECT}
export PROJECT_WORK_DIR=${OSS_FUZZ_HOME}/build/work/${FUZZER_PROJECT}
export ORIGINAL_SEEDS_DIR=${PROJECT_DIR}/pdf.js/test/pdfs                     ## change
export ORIGINAL_SEEDS_ZIP=${PROJECT_DIR}/pdf_fuzzer_seed_corpus.zip           ## change
export FUZZER=${OSS_FUZZ_HOME}/build/out/${FUZZER_PROJECT}/${FUZZER_BINARY}

# DERIVED VARS
export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export COVERAGE_OUTPUT_DIR=${DIR}/output/${FUZZER_PROJECT}

./run-libfuzzer.sh

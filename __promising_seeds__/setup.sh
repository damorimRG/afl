# installing gsutil (will need this to compute coverage)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
gcloud components update

## once
OSSDIR=${HOME}/Software/oss-fuzz/
python infra/helper.py pull_images

## per project
python infra/helper.py build_image $project_name
python infra/helper.py build_fuzzers --sanitizer=coverage --engine=libfuzzer $project_name
sudo chown ${USER} -R ${OSSDIR}/build/

## coverage
./libjpeg_turbo_fuzzer -print_coverage=1  afl-testcases/jpeg_turbo/full/images/id:001230,sync:jpeg9,src:002706,+cov.jpg # generates file .profraw
llvm-profdata-9 merge -sparse *.profraw -o default.profdata
llvm-cov-9 export -format=lcov libjpeg_turbo_fuzzer -instr-profile=default.profdata > log
grep -E "SF|DA" log | grep -vE "FNDA" | grep -vE ",0"

#llvm-cov-9 report libjpeg_turbo_fuzzer -instr-profile=default.profdata   

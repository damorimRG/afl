#!/bin/bash

OSSDIR=$1          # oss-fuzz directory
project_name=$2    # project name

# # clone oss-fuzz project if was not done already
# if [ ! -d "$OSSDIR" ]; then
#     BASEDIR=$(dirname $OSSDIR)
#     (cd $BASEDIR;
#      git clone https://github.com/google/oss-fuzz
#     )
# fi

# (cd $OSSDIR;
#  ## build project image if was not done already
#  # if [ ! "$(ls -A .)" ]; then
#  #     python infra/helper.py build_image $project_name     
#  # fi

#  # build fuzzer for the project
#  if [ ! -d "build/out/${project_name}" ]; then
#      python infra/helper.py build_fuzzers --sanitizer=coverage --engine=libfuzzer $project_name     
#  fi

#  ## for some reason it creates directories as root
# )

echo here
sudo chown ${USER} -R ${OSSDIR}

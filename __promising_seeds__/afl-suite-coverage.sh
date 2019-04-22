#!/bin/bash

PROGRAMDIR="${HOME}/Software/libpng-1.6.36"
PROGRAM="${PROGRAMDIR}/pngimage"
INPUTDIR=${PROGRAMDIR}/afl_in
#ALGOS=("afl_out_cminselection" "afl_out_moselection")
ALGOS=("afl_out_moselection")
#ALGOS=("afl_out_cminselection")

for algo in "${ALGOS[@]}"
do
    
    if [ "$algo" = "afl_out_cminselection" ]; then
        ## afl-cmin
        MINDIR="afl_out_cminselection"
        rm -rf $MINDIR
        export AFL_KEEP_TRACES="true"
        afl-cmin -i ${INPUTDIR} -o ${MINDIR} ${PROGRAM} @@
    elif [ "$algo" = "afl_out_moselection" ]; then
        ## multi-objective minimization
        MINDIR="afl_out_moselection"
        rm -rf $MINDIR
        python3 afl_mo_selection.py -i ${INPUTDIR} -o ${MINDIR} "${PROGRAM} @@"
    else
        echo "Error"
        exit 1
    fi


    printf "\n\n\n\nnumber of branches covered ----> "

    (
        for f in ${MINDIR}/*; do
            if ! [ -f $f ];then
                continue
            fi
            name=$(basename $f)
            echo $name
            cat ${MINDIR}/.traces/${name}
        done
    ) | sort -n | uniq | wc -l
    
    
done

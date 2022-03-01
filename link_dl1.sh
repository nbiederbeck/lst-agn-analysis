#!/bin/bash
run_ids=(
[20210430]='4568 4569 4570 4571 4572'
)

base="/fefs/aswg/data/real/DL1/"

mkdir -p ./dl1

into_makefile="RUNS="

for night in "${!run_ids[@]}"; do
    for run in ${run_ids[${night}]}; do
        dl1_filename="${base}/${night}/v0.9/tailcut84/dl1_LST-1.Run0${run}.h5"
        dl1_local="./dl1/$(basename ${dl1_filename})"
        ln -s $dl1_filename $dl1_local 
        into_makefile="$into_makefile $run"
    done
done

echo $into_makefile > run_ids.mk

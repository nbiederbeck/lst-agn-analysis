#!/bin/bash
run_ids=(
[20210430]='4568 4569 4570 4571 4572'
)

base="/fefs/aswg/data/real/DL1/"
mc_path="/fefs/aswg/data/models/20200629_prod5_trans_80/zenith_20deg/south_pointing/20220215_v0.9.1_prod5_trans_80_local_tailcut_8_4/"

wd="/fefs/aswg/workspace/noah.biederbeck/agn/mrk421"

cmd="source /fefs/aswg/software/conda/etc/profile.d/conda.sh; "
cmd+="conda activate lstchain-v0.9.3; "

for night in "${!run_ids[@]}"; do
    for run in ${run_ids[${night}]}; do
        dl1_filename="${base}/${night}/v0.9/tailcut84/dl1_LST-1.Run0${run}.h5"
        if [ ! -f "${dl2_filename}" ]; then
            cmd+="lstchain_dl1_to_dl2 "
            cmd+=" --input-file ${dl1_filename} "
            cmd+=" --output-dir ${wd}/dl2 "
            cmd+=" --path-models ${mc_path} "
            cmd+=" --config ${wd}/lstchain.json "
            sbatch \
                --parsable \
                --mem=32G \
                -o build/${run}.stdout \
                -e build/${run}.stderr \
                --wrap="$cmd"
        fi
    done
done

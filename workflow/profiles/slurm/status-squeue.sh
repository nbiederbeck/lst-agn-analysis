#!/usr/bin/env bash

# Check status of Slurm job

jobid="$1"

if [[ "$jobid" == Submitted ]]
then
  echo smk-simple-slurm: Invalid job ID: "$jobid" >&2
  echo smk-simple-slurm: Did you remember to add the flag --parsable to your sbatch call? >&2
  exit 1
fi

output=`squeue --me -j "$jobid" -o '%T' -h`

# Failure is not an option
if [[ -n $output ]]
then
  echo running
else
  echo success
fi

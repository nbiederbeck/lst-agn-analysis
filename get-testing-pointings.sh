#!/bin/bash

usage() {
    echo "Usage:
./$0 <production-id>

Creates a csv file containing of the zenith and azimuth values
from the merged TestingDataset nodes of a DL1 production.
"
}

case $1 in
    -h|--help)
        usage
        exit 0
        ;;
    "")
        usage
        exit 1
        ;;
    *)
        ;;
esac


outfile="$1.csv"
echo "zenith/deg,azimuth/deg" > $outfile
ls "/fefs/aswg/data/mc/DL1/AllSky/$1/TestingDataset" \
    | grep 'theta.*merged.h5' -o \
    | grep 'theta.*merged' -o \
    | tr -d '[a-z]' \
    | sed 's/__/,/' \
    | tr -d '_' \
    >> $outfile

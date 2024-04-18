#!/bin/bash

raw_data_file=$1
analysis_filename=$2
histogram_filename=$3

# cal_file=$2

# --- source root & grsisort
source /software/root/bin/thisroot.sh
source /software/GRSISort/thisgrsi.sh

# --- run ntuple
cp /software/NTuple2EventTree/NoEnergySmear.dat .
/software/NTuple2EventTree/NTuple2EventTree -sf NoEnergySmear.dat -if $raw_data_file

if [[ ! -f analysis00000_000.root ]]; then
    echo "Analysis file not found, exiting"
    exit 1
fi

# --- change filename
mv analysis00000_000.root $analysis_filename

# --- sort data into histograms
grsiframe $analysis_filename AngularCorrelationHelper.cxx --max-workers=1

mv AngularCorrelation00000-00000.root $histogram_filename

exit 0
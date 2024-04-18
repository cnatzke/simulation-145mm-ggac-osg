#!/bin/bash

raw_data_file=$1
analysis_filename=$2
histogram_filename=$3
gate_centroid=$4
peak_centroid=$5
peak_area_filename=$6

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


# --- sort data into histograms
grsiframe analysis00000_000.root AngularCorrelationHelper.cxx --max-workers=1

# --- fit angular indices
grsisort -l -b -q "processSimulationOutputOSG.C($gate_centroid,$peak_centroid)"

# --- change filename
mv analysis00000_000.root $analysis_filename
mv AngularCorrelation00000-00000.root $histogram_filename
mv peak_areas.csv $peak_area_filename

exit 0
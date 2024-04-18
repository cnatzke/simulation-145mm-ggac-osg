#!/bin/bash

# source root
ROOT_VERSION="v6.14.06"
source /softwares/RootCern/${ROOT_VERSION}/bin/thisroot.sh

# run ntuple
if ! /softwares/NTuple/NTuple -sf Settings.dat -if $1 -of $2; then
    sleep 1m
    exit 1
fi

sleep 1m
exit 0


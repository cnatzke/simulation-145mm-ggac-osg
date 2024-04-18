#!/bin/bash

# source geant4
GEANT4_VERSION="geant4.10.01.p03"
source /softwares/${GEANT4_VERSION}/bin/geant4.sh

# run simulation
/softwares/simulation/bin/Griffinv10 $1

if [[ "$?" -eq "134" && -s g4out.root ]]; then
    echo "Caught exit code 134"
    echo "Uh, had a slight weapons malfunction. But, uh, everything's perfectly all right now. We're fine. We're all fine here, now, thank you. How are you?"

    if [[ ! -s g4out.root ]]; then
        echo "File g4out.root does not exist or is 0 bytes!"
        exit 1
    elif [[ -n "$(find ./ -name "g4out.root" -prune -size -10M)" ]]; then
        echo "File g4out.root is too small"
        exit 2
    else
        echo "Changed default root filename to $2"
        mv g4out.root $2
        exit 0
    fi 

else
    echo "Normal execution"

fi


# if [[ "$?" -eq "134" && -s g4out.root ]]; then
#     echo "Uh, had a slight weapons malfunction. But, uh, everything's perfectly all right now. We're fine. We're all fine here, now, thank you. How are you?"
#     mv g4out.root $2
#     exit 0
# elif [[ "$?" -eq "0" ]]; then
#     echo "All is good"
#     mv g4out.root $2
#     exit 0
# elif [[ ! -s g4out.root ]]; then
#     echo "File g4out.root does not exist or is 0 bytes!"
#     exit 1
# elif [[ -n "$(find ./ -name "g4out.root" -prune -size -10M)" ]]; then
#     echo "File g4out.root is too small"
#     exit 2
# else
#     echo "Something went wrong"
#     exit 3
# fi

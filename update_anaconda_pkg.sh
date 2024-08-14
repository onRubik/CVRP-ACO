#!/bin/bash

# Desired package and version
PACKAGE="tqdm==4.66.3"

# Loop through all conda environments and update the package
for env in $(conda env list | awk '{print $1}' | grep -v "#"); do
    echo "Updating $PACKAGE in environment: $env"
    conda activate $env
    conda install -y $PACKAGE
done

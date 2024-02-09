#!/bin/bash

DIRECTORY="/home/titi/Desktop/JONNATHAN/INPUTS"

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Directory $DIRECTORY does not exist."
    exit 1
fi

# Find and delete .xyz files containing "trj" in their filename within each folder
find "$DIRECTORY" -type f -name "*.xyz" -name "*trj*" -exec rm {} \;

echo "Deletion complete."

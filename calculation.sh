#!/bin/bash

INPUTS_DIR="/home/jorge316/Desktop/Yggdrasil/INPUTS"
ORCA_PATH="/home/jorge316/orca/orca"

# Check if INPUTS_DIR exists
if [ ! -d "$INPUTS_DIR" ]; then
    echo "Directory $INPUTS_DIR does not exist."
    exit 1
fi

# Store the current directory
current_dir=$(pwd)   # Store the current directory path in the variable "current_dir"

# Find only the top-level folders within INPUTS_DIR and sort them numerically
folders=$(find "$INPUTS_DIR" -mindepth 1 -maxdepth 1 -type d | sort -V)

# Loop through each found top-level folder
for folder in $folders; do
    # Extract just the folder name (without path)
    folder_number=$(basename "$folder")
    echo "**********Reaction Number $folder_number processing**********"

    # Change to the top-level folder directory
    cd "$folder" || continue

    # Find all subdirectories within the current folder (reactants, intermediates, products)
    subfolders=$(find . -mindepth 1 -maxdepth 1 -type d)

    # Loop through each found subfolder
    for subfolder in $subfolders; do
        # Change to the subfolder directory
        cd "$subfolder" || continue

        # Find all .inp files within the subfolder
        inp_files=$(find . -type f -name "*.inp")

        # Loop through each found .inp file
        for inp_file in $inp_files; do
            echo "Started calculation for $inp_file"
            $ORCA_PATH "$inp_file" > "${inp_file%.inp}.out"
            echo  "Control"
            echo "Finished calculation for $inp_file"

            # Check if the calculation was successful
            if grep -q "HURRAY" "${inp_file%.inp}.out"; then
                echo "The calculation was successful"
            else
                echo "The calculation failed"
            fi
        done

        # Return to the top-level folder
        cd ..
    done

    # Return to the original directory
    cd "$current_dir"
done

echo "Task completed."


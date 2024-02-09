#!/bin/bash

input_dir="/home/titi/Desktop/JONNATHAN/INPUTS"

# Get all directories within the input directory and sort them numerically
sorted_dirs=$(find "$input_dir" -maxdepth 1 -type d | sort -V)

# Loop over all sorted directories in the input directory
for dir in $sorted_dirs; do
    if [ "$dir" != "$input_dir" ]; then  # Skip the input directory itself
        # Extract the reaction ID from the directory path
        reaction_id=$(basename "$dir")
        
        # Loop over all subdirectories in the current directory
        for sub_dir in "$dir"/*; do
            if [ -d "$sub_dir" ]; then
                
                # Look for .out files
                out_files=$(find "$sub_dir" -type f -name "*sp.out")
                
                for file in $out_files; do
                    # Check for the phrase "Error : multiplicity" in the .out file
                    if grep -q "ORCA finished" "$file"; then
                        echo "Reaction number $reaction_id has 'Error : multiplicity' in file: $file"
                    fi
                done
                
            fi
        done
    fi
done

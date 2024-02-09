#!/bin/bash

# Define paths
XYZ_PATH="/home/jorge316/Desktop/Yggdrasil/moleculas"
MAIN_PATH="/home/jorge316/Desktop/Yggdrasil"
INPUTS_DIR="$MAIN_PATH/INPUTS"
CSV_FILE="/home/jorge316/Desktop/Yggdrasil/molecule_charges.csv"

# Check if XYZ_PATH is provided
if [ -z "$XYZ_PATH" ]; then
    echo "Please provide the path to the directory containing .xyz files."
    exit 1
fi

# Check if XYZ_PATH directory exists
if [ ! -d "$XYZ_PATH" ]; then
    echo "Directory $XYZ_PATH does not exist."
    exit 1
fi

# Create the INPUTS directory if it doesn't exist
mkdir -p "$INPUTS_DIR"

# Define a function to process each .xyz file
process_xyz_file() {
    xyz_file=$1
    inputs_dir=$2
    csv_file=$3

    reaction_folder=$(dirname "$xyz_file")
    reaction_id=$(basename "$reaction_folder")
    reaction_inputs_dir="$inputs_dir/$reaction_id"
    mkdir -p "$reaction_inputs_dir"

    filename=$(basename "$xyz_file")
    base_name="${filename%.*}"
    molecule_type=$(echo "$base_name" | sed 's/[0-9]*$//')
    molecule_idx=$(echo "$base_name" | sed 's/^[^0-9]*//')
    inp_folder="$reaction_inputs_dir/$base_name"
    inp_file="$inp_folder/$base_name.inp"
    mkdir -p "$inp_folder"

    charge=$(awk -F, -v id="$reaction_id" -v type="$molecule_type" -v idx="$molecule_idx" \
             '$1 == id && $2 == type && $3 == idx {print $4}' "$csv_file")
    if [ -z "$charge" ]; then
        echo "Warning: No charge found for $reaction_id, $molecule_type, $molecule_idx. Using default charge of 0."
        char
    fi

    {
        head -n 5 starting.inp
        echo "* xyz $charge 1"
        tail -n +3 "$xyz_file"
        tail -n 2 starting.inp
    } > "$inp_file"

    echo "Processed $filename with charge $charge"
}

export -f process_xyz_file

# Find all .xyz files and process them in parallel
find "$XYZ_PATH" -type f -name "*.xyz" | parallel -j 16 process_xyz_file {} "$INPUTS_DIR" "$CSV_FILE"
echo "Task completed."


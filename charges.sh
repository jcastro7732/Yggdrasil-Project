#!/bin/bash

# Define the root directory to start searching
root_directory="/home/titi/Desktop/JONNATHAN/INPUTS"

# Find all .out files recursively starting from the root directory
find "$root_directory" -type f -name "*sp.out" -print0 | while IFS= read -r -d $'\0' out_file; do
  # Extract the directory path and folder name
  directory_path=$(dirname "$out_file")
  folder_name=$(basename "$directory_path")

  # Generate the output .csv file name
  output_file="${directory_path}/${folder_name}_charges.csv"

  # Initialize variables
  atomic_charges=""
  overlap_charges=""
  within_atomic_section=false
  within_overlap_section=false
  skip_next_atomic_line=false
  skip_next_overlap_line=false

  # Read the .out file line by line
  while IFS= read -r line; do
    # Skip lines if flags are set
    if [[ $skip_next_atomic_line == true ]]; then
      skip_next_atomic_line=false
      continue
    fi

    if [[ $skip_next_overlap_line == true ]]; then
      skip_next_overlap_line=false
      continue
    fi

    # Check for the start of the atomic charges section
    if [[ $line == *"MULLIKEN ATOMIC CHARGES"* ]]; then
      within_atomic_section=true
      skip_next_atomic_line=true
      continue
    fi

    # Check for the start of the overlap charges section
    if [[ $line == *"MULLIKEN OVERLAP CHARGES"* ]]; then
      within_overlap_section=true
      skip_next_overlap_line=true
      continue
    fi

    # Check for the end of the atomic charges section
    if [[ $line == *"Sum of atomic charges:"* ]]; then
      within_atomic_section=false
      continue
    fi

    # Check for the end of the overlap charges section
    if [[ $line == *"LOEWDIN POPULATION ANALYSIS"* ]]; then
      within_overlap_section=false
      # Remove the last row of asterisks
      overlap_charges=${overlap_charges%"******************************* "}
      continue
    fi

    # Extract atomic charges
    if [[ $within_atomic_section == true ]]; then
      atomic_charges="${atomic_charges}${line} "
    fi

    # Extract overlap charges
    if [[ $within_overlap_section == true ]]; then
      overlap_charges="${overlap_charges}${line} "
    fi

  done < "$out_file"

  # Save the charges to the output CSV file
  echo "ATOMIC_CHARGES,OVERLAP_CHARGES" > "$output_file"
  echo "\"${atomic_charges}\",\"${overlap_charges}\"" >> "$output_file"
done

echo "Charges Extraction Completed"


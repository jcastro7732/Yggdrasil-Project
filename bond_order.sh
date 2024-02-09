#!/bin/bash

# Define the root directory to start searching
root_directory="/home/titi/Desktop/JONNATHAN/INPUTS"

# Find all .out files recursively starting from the root directory
find "$root_directory" -type f -name "*sp.out" -print0 | while IFS= read -r -d $'\0' out_file; do
  # Extract the directory path and folder name
  directory_path=$(dirname "$out_file")
  folder_name=$(basename "$directory_path")

  # Generate the output .csv file name
  output_file="${directory_path}/${folder_name}_bond_order.csv"

  # Initialize variables
  bond_orders=""
  within_bond_order_section=false

  # Read the .out file line by line
  while IFS= read -r line; do
    # Check for the start of the bond order section
    if [[ $line == *"Mayer bond orders larger than 0.100000"* ]]; then
      within_bond_order_section=true
      continue
    fi

    # Check for the end of the bond order section
    if [[ $line == *"-------"* ]]; then
      within_bond_order_section=false
      continue
    fi

    # Extract bond orders
    if [[ $within_bond_order_section == true ]]; then
      bond_orders="${bond_orders}${line} "
    fi
  done < "$out_file"

  # Save the bond orders to the output CSV file
  echo "BOND_ORDERS" > "$output_file"
  echo "\"${bond_orders}\"" >> "$output_file"
done

echo "Bond Order Extraction Completed"

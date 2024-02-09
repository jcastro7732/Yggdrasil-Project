#!/bin/bash

input_dir="/home/titi/Desktop/JONNATHAN/INPUTS"
template_file="/home/titi/Desktop/JONNATHAN/script/single.inp"
csv_file="/home/titi/Desktop/JONNATHAN/molecule_charges.csv"  # Path to the CSV file

# Save the head and tail of the template file
template_head=$(head -n 5 "$template_file")
template_tail=$(tail -n 6 "$template_file")
template_special_tail=$(tail -n 5 "$template_file")

# Get all directories within the input directory and sort them numerically
sorted_dirs=$(find "$input_dir" -maxdepth 1 -type d | sort -V)

# Loop over all sorted directories in the input directory
for dir in $sorted_dirs; do
    if [ "$dir" != "$input_dir" ]; then  # Skip the input directory itself
        # Extract the reaction ID from the directory path
        reaction_id=$(basename "$dir")
        
		if [ "$reaction_id" -ge 901 ]; then
		
        # Print the reaction number being processed
        echo "**********Reaction number $reaction_id processing**********"
        
        # Loop over all subdirectories in the current directory
        for sub_dir in "$dir"/*; do
            if [ -d "$sub_dir" ]; then
                # Extract the molecule type and index from the subdirectory path
                molecule_type=$(basename "$sub_dir")
                molecule_idx=$(basename "$sub_dir" | sed 's/^[^0-9]*//')
                
                # Create the new filename
                new_file="${molecule_type}_sp.inp"
                
                # Extract the 6th line from the existing .inp file
                sixth_line=$(sed -n '6p' "$sub_dir"/*.inp)
                
               # Check for .xyz files
                xyz_files=$(find "$sub_dir" -type f -name "*.xyz")
                if [ -n "$xyz_files" ]; then
                    for file in $xyz_files; do
                        # Extract the file content
                        file_content=$(tail -n +3 "$file")
                        # Create the new file content
                        new_file_content="${template_head}\n${sixth_line}\n${file_content}\n${template_tail}"
                        # Create the new file
                        echo -e "$new_file_content" > "$sub_dir/$new_file"
                        echo "New .inp file created: $new_file"
                        
                        # Execute orca command on the .inp file
                        echo "Started calculation for $new_file"
                        /home/titi/orca/orca "$sub_dir/$new_file" > "$sub_dir/${new_file%.inp}.out" 
                        echo "Finished calculation for $new_file"
                    done
                else
                    # Check for .inp files if no .xyz files are found
                    inp_files=$(find "$sub_dir" -type f -name "*.inp")
                    for file in $inp_files; do
                        # Extract the file content except the first 6 lines
                        file_content=$(tail -n +7 "$file")
                        # Create the new file content
                        new_file_content="${template_head}\n${sixth_line}\n${file_content}\n${template_special_tail}"
                        # Create the new file
                        echo -e "$new_file_content" > "$sub_dir/$new_file"
                        echo "New .inp file created from existing .inp: $new_file"
                        
                        # Execute orca command on the .inp file
                        echo "Started calculation for $new_file"
                        /home/titi/orca/orca  "$sub_dir/$new_file" > "$sub_dir/${new_file%.inp}.out" 
                        echo "Finished calculation for $new_file"
                    done
                fi
            fi
        done
		fi
    fi
done

echo "**********Task completed**********"








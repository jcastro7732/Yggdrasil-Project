#!/bin/bash

# Define the root directory and backup directory
root_dir="/home/titi/Desktop/JONNATHAN/INPUTS"
backup_dir="/home/titi/Desktop/JONNATHAN/moleculas"

# Iterate through each reaction folder in the root directory
for reaction_folder in "$root_dir"/*; do
    # Extract the reaction ID from the folder name
    reaction_id=$(basename "$reaction_folder")
    
    # Debug: Print the reaction folder and ID
    echo "Checking Reaction Folder: $reaction_folder, ID: $reaction_id"
    
    # Iterate through each molecule type folder (reactant, intermediate, product)
    for molecule_type_folder in "$reaction_folder"/*; do
        # Extract the full molecule type from the folder name (e.g., intermediate1)
        full_molecule_type=$(basename "$molecule_type_folder")
        
        # Debug: Print the molecule type folder and type
        echo "Checking Molecule Type Folder: $molecule_type_folder"
        
        # Check if .xyz files exist in the molecule_type_folder
        if [ -z "$(ls -A "$molecule_type_folder"/*.xyz 2>/dev/null)" ]; then
            # Debug: Print message indicating no .xyz files found
            echo "No .xyz files found in $molecule_type_folder. Checking backup directory."
            
            # Check if the corresponding folder exists in the backup directory
            backup_molecule_folder="$backup_dir/$reaction_id/$full_molecule_type"
            if [ -d "$backup_molecule_folder" ]; then
                # Check if .xyz files exist in the backup folder
                if [ -n "$(ls -A "$backup_molecule_folder"/*.xyz 2>/dev/null)" ]; then
                    # Copy the .xyz files from the backup folder to the root folder and rename them
                    for backup_xyz_file in "$backup_molecule_folder"/*.xyz; do
                        backup_xyz_filename=$(basename -- "$backup_xyz_file")
                        new_xyz_filename="${backup_xyz_filename%.xyz}_backup.xyz"
                        cp "$backup_xyz_file" "$molecule_type_folder/$new_xyz_filename"
                    done
                    echo "Copied and renamed .xyz files from $backup_molecule_folder to $molecule_type_folder."
                else
                    echo "No .xyz files found in backup folder $backup_molecule_folder."
                fi
            else
                echo "Backup folder $backup_molecule_folder does not exist."
            fi
        fi
    done
done

#!/bin/bash

# Initialize a temporary file for unsorted data.
temp_file="/tmp/temp_database(1500).csv"

# Initialize the CSV file by writing the header row.
echo "REACTION_ID,MOLECULE_TYPE,MOLECULE_INDEX,COORDINATES,NEAREST_NEIGHBORS,ATOMIC_CHARGES,OVERLAP_CHARGES,BOND_LENGTH,BOND_ORDERS,SMILES" > "$temp_file"

# Define the directories to be scanned.
root_dir="/home/titi/Desktop/JONNATHAN/INPUTS"
backup_dir="/home/titi/Desktop/JONNATHAN/moleculas"
smiles_file="/home/titi/Desktop/JONNATHAN/smiles(1500c).csv"

# Loop through each folder in the root directory.
for reaction_folder in "$root_dir"/*; do
    reaction_id=$(basename "$reaction_folder")
    echo "Reaction Folder: $reaction_folder, ID: $reaction_id"

    # Loop through each sub-folder in the current reaction folder.
    for molecule_type_folder in "$reaction_folder"/*; do
        full_molecule_type=$(basename "$molecule_type_folder")
        molecule_type="${full_molecule_type%%[0-9]*}"
        molecule_index="${full_molecule_type##$molecule_type}"
        echo "Molecule Type Folder: $molecule_type_folder, Type: $molecule_type, Index: $molecule_index"

        # Extract SMILES from the smiles file.
        smiles_column_name="${molecule_type^^}_${molecule_index}"
        smiles=$(awk -F, -v id="$reaction_id" -v col_name="$smiles_column_name" 'NR==1 {for(i=1;i<=NF;i++) {if ($i == col_name) col_idx=i}} NR>1 && $1 == id {print $col_idx}' "$smiles_file")

        # Search for .xyz files in the current molecule type folder.
        xyz_files=$(find "$molecule_type_folder" -name "*.xyz")
        if [ -z "$xyz_files" ]; then
            xyz_files=$(find "$backup_dir/$reaction_id" -name "$full_molecule_type*.xyz")
        fi

        # Loop through each .xyz file found.
        for xyz_file in $xyz_files; do
            coordinates=$(tail -n +3 "$xyz_file" | tr '\n' ' ')
            nn_file=$(find "$molecule_type_folder" -name "*_nn.txt")
            if [ -z "$nn_file" ]; then
                nearest_neighbors=""
            else
                nearest_neighbors=$(tail -n +2 "$nn_file" | tr '\n' ' ')
            fi

            charges_file=$(find "$molecule_type_folder" -name "*_charges.csv")
            if [ -z "$charges_file" ]; then
                atomic_charges=""
                overlap_charges=""
            else
                atomic_charges=$(awk -F, 'NR==2 {gsub(/"/, "", $1); gsub(/\n/, " ", $1); print $1}' "$charges_file")
                overlap_charges=$(awk 'BEGIN { FS = ","; OFS = "," } NR==2 { $1=""; gsub(/^,/, ""); gsub(/"/, "", $0); gsub(/\n/, " ", $0); print $0}' "$charges_file")
            fi

            if [ "$overlap_charges" == " " ]; then
                overlap_charges="- 0"
            fi

            # Search for the corresponding _bl.txt file in the current molecule type folder.
            bl_file=$(find "$molecule_type_folder" -name "*_bl.txt")
            if [ -z "$bl_file" ]; then
                bond_length=""
            else
                bond_length=$(awk 'NR>1 {printf "%s  ", $0}' "$bl_file")
            fi

            # Search for the corresponding _bond_order.csv file in the current molecule type folder.
            bond_order_file=$(find "$molecule_type_folder" -name "${full_molecule_type}_bond_order.csv")
            if [ -z "$bond_order_file" ]; then
                bond_orders=""
            else
                if grep -q "Warning" "$bond_order_file"; then
                    bond_orders="0"
                else
                    bond_orders=$(awk 'NR==2 {gsub(/"/, "", $0); gsub(/\n/, " ", $0); print $0}' "$bond_order_file")

                fi
            fi

            # Write the collected data to the temporary CSV file.
            echo "$reaction_id,$molecule_type,$molecule_index,\"$coordinates\",\"$nearest_neighbors\",\"$atomic_charges\",\"$overlap_charges\",\"$bond_length\",\"$bond_orders\",\"$smiles\"" >> "$temp_file"
        done
    done
done

# Sort the data based on the reaction ID and then write to the final CSV file.
sort -t, -k1,1n "$temp_file" > "/home/titi/Desktop/JONNATHAN/DATABASE/database(1500).csv"

# Remove the temporary file.
rm "$temp_file"





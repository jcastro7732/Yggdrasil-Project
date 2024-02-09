from openbabel import openbabel, pybel
import os

# Function to read the content of an XYZ file and return it as a string
def read_xyz(filename):
    # Open the file for reading
    with open(filename, 'r') as f:
        # Read all lines into a list
        lines = f.readlines()
        # Skip the first two lines (usually metadata)
        content = lines[2:]
    # Count the number of atoms based on the remaining lines
    num_atoms = len(content)
    # Return the content as a formatted string
    return str(num_atoms) + "\n\n" + "".join(content)

# Function to calculate the number of nearest neighbors for each atom in a molecule
def calculate_nearest_neighbors(mol):
    # Initialize an empty list to store the nearest neighbors data
    nearest_neighbors = []
    # Get the Open Babel molecule object from the Pybel molecule
    ob_mol = mol.OBMol
    # Iterate through each atom in the molecule
    for atom in openbabel.OBMolAtomIter(ob_mol):
        # Get the index and symbol of the atom
        atom_id = atom.GetIdx()
        atom_symbol = openbabel.GetSymbol(atom.GetAtomicNum())
        # Count the number of bonds for this atom
        num_neighbors = len([bond for bond in openbabel.OBAtomBondIter(atom)])
        # Append the atom symbol and number of nearest neighbors to the list
        nearest_neighbors.append((f"{atom_symbol}({atom_id})", num_neighbors))
    # Return the list of nearest neighbors
    return nearest_neighbors

# Function to write the nearest neighbors data to a text file
def write_to_file(nearest_neighbors, output_file):
    # Open the file for writing
    with open(output_file, 'w') as f:
        # Write the header line
        f.write("ATOM\tNEAREST_NEIGHBORS\n")
        # Write each atom and its number of nearest neighbors
        for atom, num_neighbors in nearest_neighbors:
            f.write(f"{atom}\t{num_neighbors}\n")

# Main function to execute the script
def main():
    # Define the main directory where the data is stored
    main_path = "/home/titi/Desktop/JONNATHAN/INPUTS"
    # List all numbered folders in the main directory
    numbered_folders = [dir for dir in os.listdir(main_path) if dir.isnumeric()]

    # Iterate through each numbered folder
    for numbered_folder in numbered_folders:
        folder_path = os.path.join(main_path, numbered_folder)
        molecule_folders = os.listdir(folder_path)

        # Iterate through each molecule folder within the numbered folder
        for molecule_folder in molecule_folders:
            molecule_path = os.path.join(folder_path, molecule_folder)
            # Find all .xyz files in the molecule folder
            xyz_files = [file for file in os.listdir(molecule_path) if file.endswith(".xyz")]

            # Define the name of the output text file
            output_file = os.path.join(molecule_path, molecule_folder + "_nn.txt")

            # Check if there are any .xyz files
            if xyz_files:
                # If yes, process each .xyz file
                for file in xyz_files:
                    input_file = os.path.join(molecule_path, file)
                    xyz_data = read_xyz(input_file)
                    ob_mol = pybel.readstring("xyz", xyz_data)
                    nearest_neighbors = calculate_nearest_neighbors(ob_mol)
                    write_to_file(nearest_neighbors, output_file)
            else:
                # If no .xyz files, write "-" and "0" to the output file
                with open(output_file, 'w') as f:
                    f.write("ATOM\tNEAREST_NEIGHBORS\n")
                    f.write("-\t0\n")

# Execute the main function when the script is run
if __name__ == "__main__":
    main()
    
print('The number of nearest neighbors was calculated')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the dataset
file_path = '/home/jc/Desktop/TESIS/DATABASE/data_featured_database(1500).csv'
data = pd.read_csv(file_path)

# Compute summary statistics for numerical features
summary_statistics = data.describe()

# Visualize distributions of numerical features
num_features = ['sum_atomic_charges', 'sum_bond_order_overlap', 'mean_atomic_charges', 
                'median_atomic_charges', 'std_atomic_charges', 'min_atomic_charges', 
                'max_atomic_charges', 'range_atomic_charges', 'mean_bond_order_overlap', 
                'std_bond_order_overlap', 'min_bond_order_overlap', 'max_bond_order_overlap', 
                'range_bond_order_overlap', 'atomic_basin_charge', 'weighted_average_bond_length', 
                'min_bond_length', 'max_bond_length', 'std_bond_length', 'var_bond_length', 
                'range_bond_length', 'iqr_bond_length']


# Plot histograms
data[num_features].hist(bins=15, figsize=(15, 15), layout=(7, 3))
plt.tight_layout()
plt.show()

# Examine outliers with boxplots
plt.figure(figsize=(15, 10))
sns.boxplot(data=data[num_features], orient="h")
plt.show()

# Generate and visualize a correlation matrix
correlation_matrix = data[num_features].corr()
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.show()



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, GaussianNoise, LeakyReLU
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.optimizers import Nadam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# Load data
data = pd.read_csv('/home/jorge316/Desktop/Yggdrasil/Vaticinor/data_featured_database(1500).csv')

# Define bit features for output
bit_features = [f'Bit_{i}' for i in range(1, 2049)]

# Define feature sets for experimentation
feature_sets = {
    'strong_correlation': ['mean_atomic_charges', 'max_bond_order_overlap', 'std_bond_order_overlap', 'std_bond_length'],
    'variability_based': ['std_atomic_charges', 'range_atomic_charges', 'std_bond_order_overlap', 'range_bond_order_overlap', 'std_bond_length', 'range_bond_length'],
    'balanced': ['sum_atomic_charges', 'range_bond_order_overlap', 'std_bond_length', 'iqr_bond_length'],
    'feeling': ['mean_atomic_charges', 'std_atomic_charges', 'range_atomic_charges', 'mean_bond_order_overlap', 'atomic_basin_charge', 'std_bond_length'],
    'all':['sum_atomic_charges', 'sum_bond_order_overlap', 'mean_atomic_charges', 
                'median_atomic_charges', 'std_atomic_charges', 'min_atomic_charges', 
                'max_atomic_charges', 'range_atomic_charges', 'mean_bond_order_overlap', 
                'std_bond_order_overlap', 'min_bond_order_overlap', 'max_bond_order_overlap', 
                'range_bond_order_overlap', 'atomic_basin_charge', 'weighted_average_bond_length', 
                'min_bond_length', 'max_bond_length', 'std_bond_length', 'var_bond_length', 
                'range_bond_length', 'iqr_bond_length']
}

# Choose a feature set to use
selected_features = feature_sets['all']

# Replace NaN values with an extreme value
extreme_value = 1e9  
data[selected_features + bit_features] = data[selected_features + bit_features].fillna(extreme_value)

# Function to concatenate features for reactants, intermediates, and products
def concatenate_molecule_features(group, max_reactants, mean_intermediates, max_products, selected_features):
    reactants = group[group['MOLECULE_TYPE_reactant'] == 1][selected_features].values[:max_reactants]
    intermediates = group[group['MOLECULE_TYPE_intermediate'] == 1][selected_features].values[:mean_intermediates]
    products = group[group['MOLECULE_TYPE_product'] == 1][selected_features].values[:max_products]

    reactants_padded = np.pad(reactants, [(0, max_reactants - len(reactants)), (0, 0)], 'constant', constant_values=0).flatten()
    intermediates_padded = np.pad(intermediates, [(0, mean_intermediates - len(intermediates)), (0, 0)], 'constant', constant_values=0).flatten()
    products_padded = np.pad(products, [(0, max_products - len(products)), (0, 0)], 'constant', constant_values=0).flatten()

    concatenated_features = np.concatenate([reactants_padded, intermediates_padded, products_padded])
    return concatenated_features

# Determine maximum number of reactants, intermediates, and products
max_reactants = data[data['MOLECULE_TYPE_reactant'] == 1].groupby('REACTION_ID').size().max()
mean_intermediates = math.ceil(data[data['MOLECULE_TYPE_intermediate'] == 1].groupby('REACTION_ID').size().mean())
max_products = data[data['MOLECULE_TYPE_product'] == 1].groupby('REACTION_ID').size().max()

# Calculate the input length for the neural network
input_length = (max_reactants + mean_intermediates + max_products) * len(selected_features)

# Group data by REACTION_ID and create features for each reaction
grouped_data = data.groupby('REACTION_ID').apply(lambda x: pd.Series({
    'features': concatenate_molecule_features(x, max_reactants, mean_intermediates, max_products, selected_features),
    'target_bits': x[x['MOLECULE_TYPE_product'] == 1][bit_features].max().values
})).reset_index()

# Prepare the dataset for training
X = np.stack(grouped_data['features'].values)
Y = np.stack(grouped_data['target_bits'].values)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data into a training set for cross-validation and a separate test set
X_train_scaled, X_test_scaled, Y_train, Y_test = train_test_split(X_scaled, Y, test_size=0.2, random_state=42)

# Neural network model definition
def build_model(input_length):
    model = Sequential()
    model.add(GaussianNoise(0.1, input_shape=(input_length,)))
    model.add(Dense(4096, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4), activation='relu'))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(2048, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1024, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(512, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(256, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(128, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.4))
    model.add(Dense(64, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(32, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)))
    model.add(LeakyReLU(alpha=0.1))
    model.add(BatchNormalization())
    model.add(Dense(2048, activation='sigmoid'))  # Output Layer
    model.compile(optimizer=Nadam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

# K-Fold Cross-Validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
fold_no = 1
acc_per_fold = []
loss_per_fold = []

for train, test in kf.split(X_scaled, Y):
    model = build_model(input_length)
    print(f'Training for fold {fold_no} ...')
    
    # Modify ModelCheckpoint to save the best model for each fold
    model_checkpoint = ModelCheckpoint(f'best_model_fold_{fold_no}_all.h5', monitor='accuracy', mode='max', save_best_only=True, verbose=1)

    # Define callbacks for early stopping and to save the best model
    callbacks_list = [
        EarlyStopping(monitor='val_loss', patience=10, mode='min'),
        ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5),
        ModelCheckpoint(f'best_model_fold_{fold_no}_all.h5', monitor='val_accuracy', mode='max', save_best_only=True)
    ]

    # Fit data to model
    history = model.fit(X_scaled[train], Y[train], batch_size=64, epochs=300, verbose=1, validation_split=0.1, callbacks=callbacks_list)

    # Generate generalization metrics
    scores = model.evaluate(X_scaled[test], Y[test], verbose=0)
    print(f'Score for fold {fold_no}: {model.metrics_names[0]} of {scores[0]}; {model.metrics_names[1]} of {scores[1]*100}%')
    acc_per_fold.append(scores[1] * 100)
    loss_per_fold.append(scores[0])

    fold_no += 1


# == Provide average scores ==
print('------------------------------------------------------------------------')
print('Score per fold')
for i in range(0, len(acc_per_fold)):
  print('------------------------------------------------------------------------')
  print(f'> Fold {i+1} - Loss: {loss_per_fold[i]} - Accuracy: {acc_per_fold[i]}%')
print('------------------------------------------------------------------------')
print('Average scores for all folds:')
print(f'> Accuracy: {np.mean(acc_per_fold)} (+- {np.std(acc_per_fold)})')
print(f'> Loss: {np.mean(loss_per_fold)}')
print('------------------------------------------------------------------------')

# Identify the fold with the highest accuracy
best_fold = np.argmax(acc_per_fold) + 1
best_model_path = f'best_model_fold_{best_fold}_all.h5'
best_model = load_model(best_model_path)

# Evaluate the best model on the separate test set
_, accuracy = best_model.evaluate(X_test_scaled, Y_test, verbose=1)
print(f"Test Accuracy of the best model (Fold {best_fold}): {accuracy * 100}%")


# Plot metrics function 
def plot_metrics(history):
    metrics = ['loss', 'accuracy', 'val_loss', 'val_accuracy']
    for metric in metrics:
        plt.plot(history.history[metric], label=metric)
    try:
       # This plots the learning rate if it's recorded in the history.
        # Not all Keras callbacks record learning rates, so it's in a try-except block.
        plt.plot(history.history['lr'], label='learning rate')
    except KeyError:
        pass
    plt.title('Training Metrics')
    plt.xlabel('Epoch')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()
    
# Call the function to plot metrics
plot_metrics(history)

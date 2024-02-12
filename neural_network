import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import pickle

#on fixe des graines d'aléatoire pour avoir une reproductibilité de nos résultats
torch.manual_seed(1234)
np.random.seed(1234)

collection_name = 'sandbar'

with open(f'{collection_name}_dist','rb') as file:
    dist_not_filtered = pickle.load(file)

with open(f'{collection_name}_price','rb') as file:
    price_not_filtered = pickle.load(file)

#on filtre les prix supérieurs à 11 sol
dist = dist_not_filtered[:259,:259]
price = price_not_filtered[:259]


#on supprime la diagonale de 0 pour éviter que les distances à lui même interfere dans la prédiction
mat_dist = dist[~np.eye(dist.shape[0],dtype=bool)].reshape(dist.shape[0],-1)

#on construit un matrice similaire avec les prix et on enlève la diagonale
price_ligne = price.T
mat_price_diag = np.tile(price_ligne, (price.size, 1))
mat_price = mat_price_diag[~np.eye(mat_price_diag.shape[0],dtype=bool)].reshape(mat_price_diag.shape[0],-1)


mat_dist_triee = np.empty_like(mat_dist)
mat_price_rearrangee = np.empty_like(mat_price)

#on trie ligne par ligne la matrice des distances pour avoir toujours les distances dans l'ordre croissant dans les neurones d'entrée
#on modifie la matrice des prix pour que les prix suivent encore leurs NFT sur les colonnes
for i in range(mat_dist.shape[0]):
    indices_tri = np.argsort(mat_dist[i])
    mat_dist_triee[i] = mat_dist[i, indices_tri]
    mat_price_rearrangee[i] = mat_price[i, indices_tri]

#on juxtapose les 2 matrices pour former les inputs
dist_price = np.hstack((mat_dist_triee,mat_price_rearrangee))

# Nombre total de NFTs, de données d'entrainement et de test
number_total = dist_price.shape[0]
number_training = 150
number_test = number_total - number_training

#on choisit de manière aléatoire les données d'entrainement et de test de manière à ce qu'elles soient disjointes
indices = np.arange(number_total)
np.random.shuffle(indices)

idx_train = indices[:number_training]
idx_test = indices[number_training:number_training+number_test]

# Créer les ensembles d'entraînement
train_dist_price = dist_price[idx_train, :]
train_target_price = price[idx_train]

# Créer les ensembles de test
test_dist_price = dist_price[idx_test, :]
test_target_price = price[idx_test]

# On normalise les données d'entrainement et les données de test avec les mêmes paramètres que l'entrainement, on sépare la normalisation des données de distance et de prix
scaler_distances = StandardScaler()
scaler_prices = StandardScaler()
scaler_distances.fit_transform(train_dist_price[:,:train_dist_price.shape[1]//2])
scaler_prices.fit_transform(train_dist_price[:,train_dist_price.shape[1]//2:])
scaler_distances.transform(test_dist_price[:,:train_dist_price.shape[1]//2])
scaler_prices.transform(test_dist_price[:,train_dist_price.shape[1]//2:])

# création de tenseurs pytorch
inputs = torch.tensor(train_dist_price, dtype=torch.float32)
targets = torch.tensor(train_target_price, dtype=torch.float32)

# création d'un dataset pour l'entrainement
dataset = TensorDataset(inputs, targets)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

class NFTPricePredictor(nn.Module):
    def __init__(self):
        super(NFTPricePredictor, self).__init__()
        # on choisit les couches cachées du réseau et le nombre de neurones par couche
        self.network = nn.Sequential(
            nn.Linear(dist_price.shape[1], 15),
            nn.ReLU(),
            nn.Linear(15, 15),
            nn.ReLU(),
            nn.Linear(15, 15),
            nn.ReLU(),
            nn.Linear(15, 1)
        )
    
    def forward(self, x):
        return self.network(x)

model = NFTPricePredictor()

# on choisit la fonction perte de l'erreur quadratique moyenne et l'optimiseur ici le learning rate est de 0.0001
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# on entraine le réseau sur les données d'entrainement avec l'algorithme de backpropagation
epochs = 1000
for epoch in range(epochs):
    for batch, (X, y) in enumerate(dataloader):
        # on calcul la prédiction et la perte
        pred = model(X)
        loss = loss_fn(pred.squeeze(), y)
        
        # on applique la backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    if epoch % 10 == 0:
        print(f'Epoch {epoch}, Loss: {loss.item()}')



# on crée les tenseurs des données de test
test_inputs = torch.tensor(test_dist_price, dtype=torch.float32)
test_targets = torch.tensor(test_target_price, dtype=torch.float32)

# on crée un dataset pour les données de test
test_dataset = TensorDataset(test_inputs, test_targets)
test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)  # Pas besoin de mélanger pour l'évaluation

# Passer le modèle en mode évaluation
model.eval()

# on stock les prédictions et les vraies cibles
predictions, actuals = [], []

with torch.no_grad():  # Pas besoin de calculer les gradients pour l'évaluation
    for inputs, targets in test_dataloader:
        # on fait les prédictions
        outputs = model(inputs)
        predictions.extend(outputs.view(-1).tolist())
        actuals.extend(targets.view(-1).tolist())

# on calcul la performance avec l'erreur absolue moyenne
mae = mean_absolute_error(actuals, predictions)
print(f'Erreur : {mae}')
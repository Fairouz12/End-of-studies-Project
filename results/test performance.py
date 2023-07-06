import numpy as np
import matplotlib.pyplot as plt

# Données d'exemple
categories = ['Accuracy', 'F1-score', 'Precision']
train_values = [1.0, 1.0, 1.0]
train_errors = [0.0, 0.0, 0.0]
test_values = [0.814, 0.795, 0.819]
test_errors = [0.013, 0.010, 0.014]

# Configuration des positions des barres
bar_width = 0.35
train_pos = np.arange(len(categories))
test_pos = train_pos + bar_width

# Création du graphique
plt.figure(figsize=(10, 6))

# Barres pour les métriques d'entraînement
plt.bar(train_pos, train_values, yerr=train_errors, width=bar_width, label='Entraînement', color='#FF5733')
for i, v in enumerate(train_values):
    plt.text(train_pos[i], v + 0.05, str(v), ha='center', va='bottom')

# Barres pour les métriques de test
plt.bar(test_pos, test_values, yerr=test_errors, width=bar_width, label='Test', color='blue')
for i, v in enumerate(test_values):
    plt.text(test_pos[i], v + 0.05, str(v), ha='center', va='bottom')

# Configuration du graphique
plt.ylim([0, 1.2])
plt.xlabel('Métriques')
plt.ylabel('Valeurs')
plt.title('Évaluation des performances après la validation croisée ')
plt.xticks(train_pos + bar_width/2, categories)
plt.legend()

# Affichage du graphique
plt.show()

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

def clean_price(price_str):
    """Nettoie et extrait le prix TTC d'une chaîne de caractères"""
    if pd.isna(price_str):
        return np.nan
        
    # Convertir en string si ce n'est pas déjà le cas
    price_str = str(price_str)
    
    # Supprimer les retours à la ligne et caractères spéciaux
    price_str = price_str.replace('\n', ' ').replace('\xa0', ' ')
    
    # Extraire le premier prix (TTC)
    if 'T.T.C.' in price_str:
        price_str = price_str.split('T.T.C.')[0]
    
    # Nettoyer le reste
    price_str = price_str.replace('€', '').strip()
    # Supprimer tous les espaces
    price_str = ''.join(price_str.split())
    
    try:
        return float(price_str)
    except ValueError:
        return np.nan

def clean_numeric(value_str):
    """Nettoie les valeurs numériques en gérant les espaces"""
    if pd.isna(value_str):
        return np.nan
        
    # Convertir en string
    value_str = str(value_str)
    
    # Supprimer les caractères spéciaux et les espaces
    value_str = value_str.replace('\xa0', '').replace(' ', '')
    
    try:
        return float(value_str)
    except ValueError:
        return np.nan

def clean_date(date_str):
    """Nettoie les dates en gérant les espaces"""
    if pd.isna(date_str):
        return np.nan
        
    # Nettoyer les espaces au début et à la fin
    date_str = str(date_str).strip()
    
    try:
        return pd.to_datetime(date_str, format='%d/%m/%Y')
    except ValueError:
        return np.nan

def clean_car_data(data_path='data/dataset.csv'):
    # Vérification de l'existence du fichier
    if not Path(data_path).exists():
      raise FileNotFoundError(f"Le fichier {data_path} n'existe pas. Assurez-vous que le dossier 'data' existe et contient le fichier dataset.csv")
    
    # Open dataframe
    df = pd.read_csv(data_path, encoding='utf-8', sep=',')
    
    # Suppression des doublons
    rows_initial = len(df)
    cols_for_check_dup = df.columns.difference(['publishedsince'])
    df = df.drop_duplicates(subset=cols_for_check_dup)
    rows_after = len(df)
    
    print(f"Lignes avant : {rows_initial}")
    print(f"Lignes après : {rows_after}")
    print(f"Doublons supprimés : {rows_initial - rows_after}")
    
    # Nettoyage des colonnes numériques
    # Prix: enlever le symbole € et les espaces, convertir en float
    df['price'] = df['price'].apply(clean_price)
    
    # Kilométrage: enlever 'Km' et convertir en float
    df['kilométragecompteur'] = df['kilométragecompteur'].str.replace(' Km', '').apply(clean_numeric)
    
    # Émissions CO2: extraire juste le nombre
    df['émissionsdeco2'] = df['émissionsdeco2'].str.extract('(\d+)').astype(float)
    
    # Consommation: convertir en float
    df['consommationmixte'] = df['consommationmixte'].str.extract('(\d+\.?\d*)').astype(float)
    
    # Nettoyage des dates
    df['miseencirculation'] = df['miseencirculation'].apply(clean_date)
    
    # Nettoyage des caractéristiques catégorielles
    # Convertir en catégories pour optimiser la mémoire
    categorical_cols = ['carmodel', 'énergie', 'boîtedevitesse', 'couleurextérieure']
    for col in categorical_cols:
        df[col] = df[col].astype('category')
    
    # Extraire la marque du modèle
    df['marque'] = df['carmodel'].str.split().str[0]
    
    # Nettoyer les valeurs booléennes
    bool_cols = ['premièremain(déclaratif)', 'vérifié&garanti', 'rechargeable']
    for col in bool_cols:
      df[col] = df[col].map({'oui': True, 'non': False})
    
    # Nettoyer les puissances
    # CV fiscaux
    df['puissancefiscale'] = df['puissancefiscale'].str.extract('(\d+)').astype(float)
    # Puissance DIN
    df['puissancedin'] = df['puissancedin'].str.extract('(\d+)').astype(float)
    
    # Convertir les options de string en liste
    df['options'] = df['options'].str.strip('[]').str.split(',')
    
    # Créer des features supplémentaires
    df['age_vehicule'] = (pd.Timestamp.now() - df['miseencirculation']).dt.days / 365.25
    df['prix_par_km'] = df['price'] / df['kilométragecompteur']
    
    # Gérer les valeurs manquantes
    numerical_cols = ['kilométragecompteur', 'émissionsdeco2', 'consommationmixte', 'puissancefiscale', 'puissancedin']
    df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].mean())
    
    # Supprimer les outliers extrêmes
    for col in numerical_cols:
      q1 = df[col].quantile(0.05)
      q3 = df[col].quantile(0.95)
      iqr = q3 - q1
      df = df[~((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr)))]
    return df

# Fonction pour générer des statistiques descriptives
def get_data_stats(df):
  stats = {
    'nombre_vehicules': len(df),
    'prix_moyen': df['price'].mean(),
    'prix_median': df['price'].median(),
    'km_moyen': df['kilométragecompteur'].mean(),
    'age_moyen': df['age_vehicule'].mean(),
    'marques_populaires': df['marque'].value_counts().head(),
    'energies_populaires': df['énergie'].value_counts(),
    'correlation_prix_km': float(df['price'].corr(df['kilométragecompteur']))
  }
  return stats

def print_stats(stats):
    """Affiche les statistiques de manière formatée"""
    print("\n=== Statistiques du dataset ===")
    print(f"\nNombre de véhicules: {stats['nombre_vehicules']}")
    print(f"Prix moyen: {stats['prix_moyen']:.2f} €")
    print(f"Prix médian: {stats['prix_median']:.2f} €")
    print(f"Kilométrage moyen: {stats['km_moyen']:.2f} km")
    print(f"Age moyen: {stats['age_moyen']:.1f} ans")
    
    print("\nMarques les plus représentées:")
    for marque, count in stats['marques_populaires'].items():
        print(f"  - {marque}: {count}")
    
    print("\nTypes d'énergie:")
    for energie, count in stats['energies_populaires'].items():
        print(f"  - {energie}: {count}")
    
    print(f"\nCorrélation prix/km: {stats['correlation_prix_km']:.3f}")

def plot_correlation(df):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='kilométragecompteur', y='price', alpha=0.5)
    plt.title('Prix en fonction du kilométrage')
    plt.xlabel('Kilométrage')
    plt.ylabel('Prix (€)')
    plt.show()

if __name__ == "__main__":
  try:
    data = clean_car_data()
    data.info()
    plot_correlation(data)
    stats = get_data_stats(data)
    print_stats(stats)
  except FileNotFoundError as e:
    print(f"Erreur: {str(e)}")
  except Exception as e:
    print(f"Une erreur inattendue s'est produite: {str(e)}")
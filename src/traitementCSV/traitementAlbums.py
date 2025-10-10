import csv

# Lire le fichier avec les erreurs
with open('data/raw_albums.csv', 'r', encoding='utf-8') as f:
    content = f.read()

# Afficher un aperçu pour voir le problème
print("Aperçu du contenu brut (500 premiers caractères):")
print(content[:500])
print("\n---\n")

# Corriger les sauts de ligne en trop
# Les lignes valides commencent généralement par un nombre (ID) ou sont l'en-tête
lines = content.split('\n')
corrected_lines = []
current_line = ""

for line in lines:
    # Si la ligne commence par un nombre suivi d'une virgule, c'est probablement une nouvelle entrée
    if line.strip() == "":
        continue
    elif (line and line[0].isdigit() and ',' in line[:10]) or line.startswith('id') or line.startswith('Id'):
        if current_line:
            corrected_lines.append(current_line)
        current_line = line
    else:
        # C'est probablement la suite de la ligne précédente
        current_line += " " + line.strip()

# Ajouter la dernière ligne
if current_line:
    corrected_lines.append(current_line)

# Sauvegarder le fichier corrigé
with open('src/traitementCSV/albums_corrected.csv', 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(corrected_lines))

print(f"Fichier corrigé créé : albums_corrected.csv")
print(f"Nombre de lignes originales : {len(lines)}")
print(f"Nombre de lignes corrigées : {len(corrected_lines)}")
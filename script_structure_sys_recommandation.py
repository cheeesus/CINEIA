import os

# Définition de la structure du projet
project_structure = {
    "recommender_system": [
        "data/load_data.py",
        "data/preprocess.py",
        "models/tfidf_recommender.py",
        "models/hybrid_recommender.py",
        "training/train_model.py",
        "training/evaluate.py",
        "api/recommender_api.py",
        "config/settings.py",
        "utils/helpers.py",
        "main.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
    ]
}

# Création des dossiers et fichiers
def create_project_structure(structure):
    for root, files in structure.items():
        os.makedirs(root, exist_ok=True)
        for file in files:
            file_path = os.path.join(root, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):  # Vérifie si le fichier existe déjà
                with open(file_path, "w") as f:
                    f.write("# " + file.split("/")[-1] + "\n")  # Ajoute un commentaire de base
                print(f"✅ Fichier créé : {file_path}")
            else:
                print(f"⚠️ Fichier déjà existant : {file_path}")

# Exécuter la création
if __name__ == "__main__":
    create_project_structure(project_structure)
    print("\n🎉 Structure du projet créée avec succès !")

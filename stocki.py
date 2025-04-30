import os
import psutil
import time
from datetime import datetime
import openai

# 👉 Mets ta clé API OpenAI ici
openai.api_key = "ta_clé_openai"

# 👉 Chemin de base à scanner
base_folder = os.path.join(os.path.expanduser("~"))

# 👉 Chemin du log
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
log_file_path = os.path.join(desktop, "nettoyage_log.txt")

# 📅 Vérifie si un fichier est vieux
def est_trop_vieux(file_path, jours=90):
    dernier_modif = os.path.getmtime(file_path)
    maintenant = time.time()
    age_jours = (maintenant - dernier_modif) / (60*60*24)
    return age_jours > jours

# 📦 Demander à OpenAI si un fichier est important ou inutile
def verifier_fichier_openai(file_path):
    prompt = f"""
Voici un fichier trouvé sur un PC :
- Chemin : {file_path}
Est-ce probablement un fichier critique pour un programme ou un fichier inutile pour l'utilisateur ?
Réponds uniquement par : "important" ou "inutile". Rien d'autre.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant système qui classe les fichiers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.1
        )
        decision = response.choices[0].message.content.strip().lower()
        return decision
    except Exception as e:
        print(f"Erreur OpenAI : {e}")
        return "important"  # par sécurité

# 🧹 Scan et nettoyage intelligent
def scan_and_clean(folder):
    fichiers_suspects = []
    fichiers_inutiles_confirmes = []
    extensions_inutiles = ['.tmp', '.log', '.bak', '.old']
    jours_vieux = 90

    print("🔎 Scan en cours...")

    # Scanner tout le dossier en profondeur
    for root, dirs, files in os.walk(folder):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file)
                    size = os.path.getsize(file_path)

                    if ext.lower() in extensions_inutiles or size == 0 or est_trop_vieux(file_path, jours=jours_vieux):
                        fichiers_suspects.append(file_path)
            except Exception:
                pass  # Ignore erreurs fichiers protégés

    if not fichiers_suspects:
        return "Aucun fichier suspect détecté."

    print(f"⚡ {len(fichiers_suspects)} fichiers suspects trouvés. Analyse avec OpenAI...")

    # Vérifier chaque fichier avec OpenAI
    for file_path in fichiers_suspects:
        decision = verifier_fichier_openai(file_path)
        if decision == "inutile":
            fichiers_inutiles_confirmes.append(file_path)

    if not fichiers_inutiles_confirmes:
        return "Aucun fichier inutile confirmé après analyse."

    # Afficher les fichiers à supprimer
    print("Fichiers validés comme inutiles :")
    for f in fichiers_inutiles_confirmes:
        print(f" - {f}")

    confirmation = input("Supprimer ces fichiers ? (oui/non) >>> ").strip().lower()

    if confirmation in ["oui", "yes", "y"]:
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n=== Nettoyage du {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            for f in fichiers_inutiles_confirmes:
                try:
                    os.remove(f)
                    log_file.write(f"Supprimé : {f}\n")
                except Exception as e:
                    log_file.write(f"Erreur suppression : {f} ({e})\n")
        return f"{len(fichiers_inutiles_confirmes)} fichiers supprimés et log mis à jour."
    else:
        return "Nettoyage annulé."

# 📦 Analyse simple de ta demande
def analyse_locale(texte):
    texte = texte.lower()
    if any(mot in texte for mot in ["stockage", "espace", "disque", "place", "mémoire"]):
        return "stockage"
    elif any(mot in texte for mot in ["scan", "nettoyage", "supprime", "efface", "vider"]):
        return "nettoyage"
    else:
        return "inconnu"

# 📋 Info stockage
def get_storage_info():
    usage = psutil.disk_usage(base_folder)
    total = usage.total / (1024**3)
    used = usage.used / (1024**3)
    free = usage.free / (1024**3)
    return f"Disque : {total:.2f} Go total, {used:.2f} Go utilisé, {free:.2f} Go libre."

# 🖥️ Boucle principale
print("Assistant de nettoyage IA prêt. Tape ta demande. (exit pour quitter)")

while True:
    user_input = input(">>> ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Fermeture de l'assistant.")
        break

    action = analyse_locale(user_input)

    if action == "stockage":
        print(get_storage_info())
    elif action == "nettoyage":
        print(scan_and_clean(base_folder))
    else:
        print("Commande non reconnue. Essaie : 'vérifie stockage' ou 'nettoyage'.")

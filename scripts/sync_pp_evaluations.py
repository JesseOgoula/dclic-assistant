"""
sync_pp_evaluations.py — Moteur de synchronisation incrémentale du Projet Professionnel

Scanne les dossiers Moodle dans PP/, associe les fichiers aux apprenants,
fusionne avec l'état existant des évaluations (V1 Entraînement et V2 Finale)
et produit le dataset consolidé pour DclicApp.
"""

import os
import sys
import re
import json
import unicodedata
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PP_DIR = os.path.join(PROJECT_ROOT, "PP")
STATE_FILE = os.path.join(PROJECT_ROOT, "pp_evaluations_state.json")
LEGACY_PARSED_FILE = os.path.join(PROJECT_ROOT, "parsed_learners.json")
FRONTEND_DATA_DIR = os.path.join(PROJECT_ROOT, "DclicApp", "frontend", "src", "data")
FRONTEND_TARGET_FILE = os.path.join(FRONTEND_DATA_DIR, "pp_evaluations.json")

DELIVERABLES_DEF = [
    {
        "id": "desc",
        "num": 1,
        "title": "Description du projet",
        "short": "Description",
        "icon": "📝",
        "max_score": 0,
        "keywords": ["description"]
    },
    {
        "id": "strat",
        "num": 2,
        "title": "Stratégie Marketing (PP1)",
        "short": "Stratégie (PP1)",
        "icon": "🎯",
        "max_score": 6,
        "keywords": ["stratégie", "strategie", "marketing"]
    },
    {
        "id": "gest",
        "num": 3,
        "title": "Gestion de Projet (Gantt & RH) (PP2)",
        "short": "Gantt & RH (PP2)",
        "icon": "📅",
        "max_score": 6,
        "keywords": ["gestion de projet", "gantt", "rh"]
    },
    {
        "id": "budget",
        "num": 4,
        "title": "Budget Prévisionnel par Tâches (PP2)",
        "short": "Budget (PP2)",
        "icon": "💰",
        "max_score": 6,
        "keywords": ["budget"]
    },
    {
        "id": "content",
        "num": 5,
        "title": "Création de Contenu (Flyer & Vidéo) (PP3)",
        "short": "Contenu (PP3)",
        "icon": "🎨",
        "max_score": 4,
        "keywords": ["contenu", "content", "flyer", "video"]
    },
    {
        "id": "tdb",
        "num": 6,
        "title": "Tableau de Bord d'Indicateurs (PP4)",
        "short": "Tableau de Bord (PP4)",
        "icon": "📊",
        "max_score": 4,
        "keywords": ["tableau de bord", "indicateur", "tdb"]
    }
]

def normalize_text(text: str) -> str:
    """Normalise une chaîne pour comparaison insensible à la casse et aux accents."""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[\'’\-]', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).lower()
    return ' '.join(text.split())

def match_learner_name(raw_folder_name: str, learners: list) -> dict:
    """Associe un dossier apprenant Moodle à un apprenant de la base."""
    clean_folder = raw_folder_name.split('_')[0].strip()
    norm_folder = normalize_text(clean_folder)
    folder_words = set(norm_folder.split())

    best_match = None
    max_overlap = 0

    for l in learners:
        norm_full = normalize_text(l['full_name'])
        full_words = set(norm_full.split())
        overlap = len(folder_words.intersection(full_words))
        
        if folder_words == full_words or (overlap >= 2 and overlap > max_overlap):
            best_match = l
            max_overlap = overlap

    return best_match

def detect_deliverable_and_phase(folder_name: str):
    """Détecte le livrable et la phase à partir du nom du dossier Moodle."""
    norm = normalize_text(folder_name)
    phase = "final" if any(w in norm for w in ["final", "restitution", "definitif"]) else "entrainement"

    deliv_id = None
    for d in DELIVERABLES_DEF:
        if any(normalize_text(kw) in norm for kw in d['keywords']):
            deliv_id = d['id']
            break

    return deliv_id, phase

def load_initial_data():
    """Charge l'état existant ou initialise depuis parsed_learners.json."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    if os.path.exists(LEGACY_PARSED_FILE):
        with open(LEGACY_PARSED_FILE, 'r', encoding='utf-8') as f:
            legacy = json.load(f)
            
        state_learners = []
        for item in legacy:
            learner_entry = {
                "id": item.get("id"),
                "num": item.get("num"),
                "nom": item.get("nom"),
                "prenom": item.get("prenom"),
                "full_name": item.get("full_name"),
                "projet": item.get("projet"),
                "category": item.get("category", "green" if item.get("sub_count", 0) >= 4 else "yellow"),
                "category_label": item.get("category_label", "Actif"),
                "status_priority": item.get("status_priority", ""),
                "synthesis": item.get("synthesis", {}),
                "deliverables": {}
            }

            deliv_map = {
                0: "desc",
                1: "strat",
                2: "gest",
                3: "budget",
                4: "content",
                5: "tdb"
            }
            
            raw_delivs = item.get("deliverables", [])
            for idx, d_id in deliv_map.items():
                existing = raw_delivs[idx] if idx < len(raw_delivs) else {}
                status_str = existing.get("status", "")
                is_submitted = "Soumis" in status_str or "Validé" in status_str
                
                learner_entry["deliverables"][d_id] = {
                    "id": d_id,
                    "entrainement": {
                        "submitted": is_submitted,
                        "status": status_str or ("Non soumis" if not is_submitted else "Soumis"),
                        "comment": existing.get("comment", ""),
                        "files": []
                    },
                    "final": {
                        "submitted": False,
                        "status": "En attente de remise finale",
                        "score": None,
                        "max_score": next((d["max_score"] for d in DELIVERABLES_DEF if d["id"] == d_id), 0),
                        "comment": "",
                        "audit_v1": "",
                        "files": []
                    }
                }

            state_learners.append(learner_entry)
        return state_learners
    return []

def scan_and_sync():
    """Scanne le dossier PP et synchronise avec l'état."""
    learners = load_initial_data()
    if not learners:
        print("Erreur: aucune donnée apprenant initiale trouvée.")
        return

    print(f"Indexation de {len(learners)} apprenants...")

    if not os.path.exists(PP_DIR):
        print(f"Dossier {PP_DIR} introuvable.")
        return

    for folder_name in os.listdir(PP_DIR):
        folder_path = os.path.join(PP_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        deliv_id, phase = detect_deliverable_and_phase(folder_name)
        if not deliv_id:
            print(f"⚠️ Livrable non reconnu pour le dossier : {folder_name}")
            continue

        print(f"Scan : {folder_name} -> Livrable: {deliv_id}, Phase: {phase}")

        for sub in os.listdir(folder_path):
            sub_path = os.path.join(folder_path, sub)
            if not os.path.isdir(sub_path):
                continue

            matched = match_learner_name(sub, learners)
            if not matched:
                print(f"  ❌ Apprenant non reconnu: {sub}")
                continue

            files = []
            for f in os.listdir(sub_path):
                f_path = os.path.join(sub_path, f)
                if os.path.isfile(f_path):
                    stat = os.stat(f_path)
                    files.append({
                        "name": f,
                        "size": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

            if not files:
                continue

            learner_deliv = matched["deliverables"].setdefault(deliv_id, {})
            phase_entry = learner_deliv.setdefault(phase, {})
            phase_entry["submitted"] = True
            phase_entry["files"] = files
            if not phase_entry.get("status") or "Non soumis" in phase_entry.get("status"):
                phase_entry["status"] = "✅ Soumis" if phase == "entrainement" else "📥 Restitution déposée"

    total_learners = len(learners)
    v1_full_count = 0
    v2_submitted_count = 0
    category_counts = {"green": 0, "yellow": 0, "red": 0}

    for l in learners:
        v1_count = sum(1 for d in l["deliverables"].values() if d.get("entrainement", {}).get("submitted"))
        v2_count = sum(1 for d in l["deliverables"].values() if d.get("final", {}).get("submitted"))
        
        if v1_count >= 4:
            l["category"] = "green"
            l["category_label"] = f"Complet ({v1_count}/4 livrables)"
            category_counts["green"] += 1
            v1_full_count += 1
        elif v1_count >= 3:
            l["category"] = "yellow"
            l["category_label"] = f"Partiel ({v1_count}/4 livrables)"
            category_counts["yellow"] += 1
        else:
            l["category"] = "red"
            l["category_label"] = f"En retard ({v1_count}/4 livrables)"
            category_counts["red"] += 1

        if v2_count > 0:
            v2_submitted_count += 1

    stats = {
        "total_learners": total_learners,
        "v1_completed": v1_full_count,
        "v1_rate": round((v1_full_count / total_learners) * 100, 1) if total_learners else 0,
        "v2_submitted": v2_submitted_count,
        "v2_rate": round((v2_submitted_count / total_learners) * 100, 1) if total_learners else 0,
        "categories": category_counts,
        "last_updated": datetime.now().isoformat()
    }

    output_data = {
        "stats": stats,
        "deliverables_def": DELIVERABLES_DEF,
        "learners": learners
    }

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(learners, f, ensure_ascii=False, indent=2)

    os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)
    with open(FRONTEND_TARGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Synchronisation terminée avec succès !")
    print(f"   - Apprenants traités : {total_learners}")
    print(f"   - Livrables V1 complets : {v1_full_count} ({stats['v1_rate']}%)")
    print(f"   - Données générées dans : {FRONTEND_TARGET_FILE}")

if __name__ == "__main__":
    scan_and_sync()

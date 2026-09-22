"""
sync_pp_evaluations.py — Moteur de synchronisation incrémentale du Projet Professionnel

Scanne automatiquement les dossiers Moodle et dossiers de livrables dans PP/ et CPP/,
détecte et intègre dynamiquement les nouveaux apprenants dès qu'ils déposent des devoirs,
associe les fichiers, génère les diagnostics pédagogiques selon le référentiel de correction,
recalcule toutes les métriques de la cohorte et met à jour l'application web DclicApp.
"""

import os
import sys
import re
import json
import unicodedata
import subprocess
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
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
        "keywords": ["description", "cadrage", "livrable 0", "fiche de cadrage", "projet libre"]
    },
    {
        "id": "strat",
        "num": 2,
        "title": "Stratégie Marketing (PP1)",
        "short": "Stratégie (PP1)",
        "icon": "🎯",
        "max_score": 6,
        "keywords": ["stratégie", "strategie", "marketing", "pp1", "livrable 1", "livrable1"]
    },
    {
        "id": "gest",
        "num": 3,
        "title": "Gestion de Projet (Gantt & RH) (PP2)",
        "short": "Gantt & RH (PP2)",
        "icon": "📅",
        "max_score": 6,
        "keywords": ["gestion de projet", "gestion", "gantt", "rh", "ressources", "pp2", "livrable 2", "livrable2"]
    },
    {
        "id": "budget",
        "num": 4,
        "title": "Budget Prévisionnel par Tâches (PP2)",
        "short": "Budget (PP2)",
        "icon": "💰",
        "max_score": 6,
        "keywords": ["budget", "chiffrage", "previsionnel", "coûts", "couts"]
    },
    {
        "id": "content",
        "num": 5,
        "title": "Création de Contenu (Flyer & Vidéo) (PP3)",
        "short": "Contenu (PP3)",
        "icon": "🎨",
        "max_score": 4,
        "keywords": ["contenu", "content", "flyer", "video", "vidéo", "pp3", "livrable 3", "livrable3"]
    },
    {
        "id": "tdb",
        "num": 6,
        "title": "Tableau de Bord d'Indicateurs (PP4)",
        "short": "Tableau de Bord (PP4)",
        "icon": "📊",
        "max_score": 4,
        "keywords": ["tableau de bord", "indicateur", "indicateurs", "tdb", "kpi", "dashboard", "pp4", "livrable 4", "livrable4"]
    }
]

# Diagnostics et cadrages personnalisés connus pour les projets identifiés
KNOWN_PROJECT_DEFS = {
    "aveto": {
        "projet": "MediConnect (Téléconsultation médicale en ligne)",
        "desc_comment": "Excellent cadrage de projet pour MediConnect. Votre ambition de démocratiser la téléconsultation médicale en ligne en Afrique de l'Ouest répond à un enjeu de santé publique critique. Vos segments cibles (zones périurbaines et enclavées) sont très bien ciblés. Veillez à bien intégrer les aspects réglementaires et la confiance des utilisateurs dans la suite de vos livrables.",
        "strat_comment": "Très bonne stratégie marketing pour MediConnect. Vos deux personas (Aïcha, 28 ans et Michel, 46 ans) sont bien caractérisés avec des besoins et freins réalistes. Votre étude du marché béninois (benchmark DotoMed) et votre objectif SMART (+40 % de consultations en ligne en 6 mois) sont très cohérents. Pour le dépôt final : approfondissez la différenciation concurrentielle par rapport aux solutions existantes et précisez le budget alloué à l'acquisition WhatsApp/Facebook.",
        "gest_comment": "Votre démarche Agile découpée en 3 étapes claires (Planification, Préparation/Production, Mise en œuvre) est bien adaptée à une start-up numérique. Pour le rendu final : veillez à joindre un tableau Gantt visuel précis avec les jalons temporels hebdomadaires, et détaillez l'affectation nominative des profils RH (CM, développeur, graphiste) ainsi que le chiffrage budgétaire par tâche."
    },
    "akadja": {
        "projet": "Doer Team Kids Academy (Soutien scolaire & cours particuliers bilingues)",
        "desc_comment": "Très bonne note de cadrage pour Doer Team Kids Academy. Votre proposition de valeur sur le soutien scolaire bilingue (français/anglais) du CI à la Terminale répond à un vrai besoin des familles. Votre objectif de progression de 12 à 20 élèves est clair et réaliste.",
        "strat_comment": "Remarquable document de stratégie marketing. L'opposition entre le « parent stratège d'examen » (35-50 ans) et le « parent accompagnateur au long cours » (28-40 ans) est particulièrement fine et opérationnelle. Votre étude concurrentielle en 3 catégories montre bien la valeur ajoutée de votre offre globale. Pour le dépôt final : détaillez davantage vos actions d'activation et précisez vos indicateurs de conversion via les groupes WhatsApp de parents d'élèves."
    },
    "amoussa": {
        "projet": "KDS School (École des métiers du numérique et création de contenu)",
        "desc_comment": "Très bon cadrage de votre projet KDS School. La formation aux métiers du numérique et de la création de contenu répond à une forte demande des jeunes et professionnels. Pour le Livrable 1 (Stratégie marketing) : définissez 2 personas types (étudiant en reconversion et professionnel en perfectionnement), analysez 3 centres ou plateformes concurrentes de formation, et fixez des objectifs SMART d'acquisition d'inscrits."
    },
    "attiogbe": {
        "projet": "Santé Numérique / Télémédecine en Afrique de l'Ouest",
        "desc_comment": "Excellente analyse contextuelle et benchmark sectoriel approfondi sur la télémédecine en Afrique de l'Ouest francophone et au Togo. Votre socle documentaire est solide et bien documenté. Pour la suite (Livrable 1 - Stratégie) : traduisez ce benchmark en stratégie opérationnelle avec 2 personas patients/médecins, vos canaux d'acquisition prioritaires et vos objectifs chiffrés."
    },
    "allarabeye": {
        "projet": "Développement de l'audience d'une chaîne TV tchadienne via le numérique",
        "desc_comment": "Projet très intéressant et pertinent sur le développement d'audience d'une chaîne de télévision tchadienne via les canaux numériques. L'adaptation aux nouveaux usages mobiles et réseaux sociaux est primordiale. Pour le Livrable 1 : structurez vos 2 personas (le téléspectateur traditionnel et le jeune connecté sur mobile), benchmarquez 3 médias concurrents au Tchad/Afrique centrale, et précisez vos leviers d'acquisition digitale (extraits vidéo courts, communauté)."
    },
    "aka": {
        "nom": "AKA",
        "prenom": "Ablan Marie",
        "full_name": "AKA Ablan Marie",
        "projet": "Spag'Chaud (Restauration rapide étudiante sur campus — Côte d'Ivoire)",
        "desc_comment": "Très belle initiative avec Spag'Chaud. Répondre au besoin des étudiants des campus ivoiriens avec une offre de repas chauds, rapides et abordables est une proposition de valeur forte. Pour le Livrable 1 (Stratégie marketing) : définissez 2 personas d'étudiants types, analysez au moins 3 offres concurrentes sur les campus, et détaillez vos canaux d'acquisition (notamment réseaux sociaux et commande par WhatsApp).",
        "strat_comment": "Très bon document de stratégie marketing pour Spag'Chaud. Vos personas étudiants sont pertinents et vos canaux de diffusion adaptés à la cible jeune. Pour votre version finale : assurez-vous de bien chiffrer vos objectifs SMART de vente et approfondissez vos actions de fidélisation sur le campus.",
        "synthesis": {
            "coherence": "Le concept de restauration rapide sur campus est limpide et la stratégie marketing cible adéquatement la communauté estudiantine. Les livrables de gestion de projet (PP2) et tableau de bord (PP4) sont attendus pour boucler le dispositif.",
            "points_forts": "Projet pragmatique répondant à un besoin quotidien réel, proposition de valeur claire (prix abordable et rapidité).",
            "chantiers": "- *Sur le fond* : Finaliser le planning Gantt et le budget (PP2), puis concevoir le tableau de bord (PP4).\n  - *Sur la forme* : Maintenir la clarté visuelle et respecter les limites de mots.",
            "message": "Le projet Spag'Chaud démarre sur d'excellentes bases marketing. Poursuivre sur cette belle dynamique en structurant les livrables de gestion de projet et les indicateurs de suivi."
        },
        "status_priority": "🟡 Bon démarrage (Description + Stratégie). Finaliser PP2 (Gantt & Budget) et PP4 (Tableau de bord)."
    },
    "adou": {
        "nom": "ADOU",
        "prenom": "Sokhna",
        "full_name": "ADOU Sokhna",
        "projet": "COSNA Investments (Écoconstruction & Briques de Terre Compressée Stabilisée - BTCS)",
        "desc_comment": "Excellent cadrage de projet pour COSNA Investments. Le positionnement sur la construction écologique et les matériaux durables (BTCS) en Afrique de l'Ouest répond à un enjeu d'avenir majeur. Vos cibles (particuliers et promoteurs) sont clairement identifiées.",
        "strat_comment": "Remarquable stratégie marketing pour COSNA Investments. Vos 2 personas (particulier constructeur et promoteur professionnel) sont bien documentés et le plan d'acquisition digitale valorise parfaitement les atouts écologiques et économiques de votre offre.",
        "gest_comment": "Très bonne démarche de gestion de projet avec le planning Gantt et le budget prévisionnel associés. L'organisation des ressources humaines et le chiffrage par phases sont réalistes et bien articulés avec la stratégie marketing.",
        "tdb_comment": "Tableau de bord bien structuré avec des indicateurs de suivi clairs (visibilité digitale, leads qualifiés, conversions). Les métriques choisies permettront un pilotage rigoureux de votre performance commerciale.",
        "synthesis": {
            "coherence": "Parcours préparatoire V1 complet et exemplaire sur les 4 volets Moodle. L'alignement entre le produit écologique (BTCS), la stratégie d'acquisition, le Gantt/budget et les indicateurs KPIs est parfaitement maîtrisé.",
            "points_forts": "Dossier très complet et professionnel, maîtrise des enjeux de la construction durable, planning et budget bien modélisés.",
            "chantiers": "- *Sur le fond* : Produire les supports de communication (PP3 - flyer et vidéo < 1mn30).\n  - *Sur la forme* : Veiller au respect des limites de mots pour le rendu final.",
            "message": "Toutes mes félicitations pour la complétude et la grande qualité de l'ensemble des livrables V1. Socle remarquable pour aborder les créations de contenus (PP3) et viser l'excellence lors de la restitution finale !"
        },
        "status_priority": "🟢 Parcours V1 complet (4/4). Préparer les créations de contenu (PP3) et la restitution finale."
    },
    "aiglo": {
        "nom": "AIGLO",
        "prenom": "Sègla Gérald P.",
        "full_name": "AIGLO Sègla Gérald P.",
        "projet": "TikTok Prêt-à-Porter (Boutique physique connectée de mode et prêt-à-porter)",
        "desc_comment": "Concept très original et stimulant de boutique connectée en milieu rural, alliant point de vente physique et leviers numériques (TikTok, Facebook, Mobile Money). La sélection d'articles tendance répond à une demande locale avérée.",
        "strat_comment": "Bonne ébauche stratégique axée sur la visibilité TikTok. Pour le rendu final : veillez à bien structurer les 2 personas types, à benchmarquer 3 concurrents (boutiques physiques ou en ligne), et à préciser vos mécanismes de conversion et fidélisation en magasin.",
        "gest_comment": "Votre plan opérationnel pose de bonnes bases. Pour le rendu final : formalisez un planning Gantt clair avec les étapes clés (approvisionnement, création de contenu TikTok, promotions) et détaillez le budget par tâche.",
        "synthesis": {
            "coherence": "Idée novatrice de commerce connecté en zone semi-rurale. La description, la stratégie et la gestion de projet sont posées. Reste à concevoir le tableau de bord (PP4) pour suivre la conversion magasin/digital.",
            "points_forts": "Originalité du concept phygital (boutique physique + TikTok), ancrage commercial concret.",
            "chantiers": "- *Sur le fond* : Élaborer le Tableau de bord (PP4) et produire les contenus promotionnels (PP3).\n  - *Sur la forme* : Structurer le Gantt sous format tabulaire et préciser le budget chiffré.",
            "message": "Projet phygital TikTok Prêt-à-Porter très prometteur. Continuer ainsi en finalisant les indicateurs de performance (PP4) et les supports de communication (PP3)."
        },
        "status_priority": "🟡 Bon avancement (3/4 livrables). Concevoir le Tableau de bord (PP4) et les contenus (PP3)."
    }
}

def clean_comment(text: str) -> str:
    """Nettoie un commentaire en retirant toute formule de salutation au début et toute signature à la fin."""
    if not text or not isinstance(text, str):
        return text
    # 1. Supprimer la salutation au début (ex: "Bonjour Prénom," ou "Bonjour,")
    text = re.sub(r'^[ \t]*Bonjour\b[^\n,]*,\s*\n*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^[ \t]*Bonjour\b[^\n]*\n+', '', text, flags=re.IGNORECASE)
    # 2. Supprimer la signature à la fin (ex: "Ton tuteur D-CLIC", "Ton tuteur", "Votre tuteur D-CLIC")
    text = re.sub(r'\s*\n+[ \t]*(?:Ton|Votre)\s+tuteur(?:\s+D-?CLIC)?\.?[ \t]*$', '', text, flags=re.IGNORECASE)
    return text.strip()

def normalize_text(text: str) -> str:
    """Normalise une chaîne pour comparaison insensible à la casse et aux accents."""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[\'’\-]', ' ', text)
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
        
        if folder_words == full_words:
            return l
        
        # Check if surname and at least one firstname match
        norm_nom = normalize_text(l.get('nom', ''))
        nom_words = set(norm_nom.split())
        if nom_words and nom_words.issubset(folder_words):
            if overlap > max_overlap:
                best_match = l
                max_overlap = overlap

        if overlap >= 2 and overlap > max_overlap:
            best_match = l
            max_overlap = overlap

    return best_match

def parse_new_learner_name(clean_name: str) -> tuple:
    """Extrait nom, prénom et nom complet d'une chaîne propre."""
    words = clean_name.strip().split()
    if not words:
        return "INCONNU", "Apprenant", "INCONNU Apprenant"
    
    # Séparer les mots tout en majuscules (nom de famille) des mots en casse mixte (prénom)
    # Exclure les abréviations / initiales à une lettre comme 'P.'
    nom_words = [w for w in words if w.strip('.').isupper() and len(w.strip('.')) > 1]
    prenom_words = [w for w in words if not (w.strip('.').isupper() and len(w.strip('.')) > 1)]
    
    # Si tous les mots sont en majuscules (ex: SOKHNA ADOU)
    if len(nom_words) > 1 and not prenom_words:
        prenom_words = [w.capitalize() for w in nom_words[:-1]]
        nom_words = [nom_words[-1]]
    elif not nom_words:
        if len(words) > 1:
            nom_words = [words[-1].upper()]
            prenom_words = words[:-1]
        else:
            nom_words = [words[0].upper()]
            prenom_words = []
    
    nom = " ".join(nom_words)
    prenom = " ".join(prenom_words)
    full_name = f"{nom} {prenom}".strip() if prenom else nom
    return nom, prenom, full_name

def create_new_learner(raw_folder_name: str, learners: list) -> dict:
    """Crée dynamiquement un nouvel apprenant dans le référentiel."""
    clean_name = raw_folder_name.split('_')[0].strip()
    nom, prenom, full_name = parse_new_learner_name(clean_name)
    
    # Calcul du prochain numéro séquentiel
    max_num = 0
    for l in learners:
        try:
            val = int(str(l.get("num", "0")).lstrip("0") or "0")
            if val > max_num:
                max_num = val
        except ValueError:
            pass
    
    new_num = f"{max_num + 1:02d}"
    learner_id = f"learner-{new_num}"
    
    # Recherche d'un projet connu
    norm_key = normalize_text(nom).lower()
    known_info = None
    for k, v in KNOWN_PROJECT_DEFS.items():
        if k in norm_key or any(k in normalize_text(w) for w in clean_name.split()):
            known_info = v
            break
            
    project_title = known_info["projet"] if known_info else "Projet Professionnel D-CLIC"
    
    new_learner = {
        "id": learner_id,
        "num": new_num,
        "nom": nom,
        "prenom": prenom,
        "full_name": full_name,
        "projet": project_title,
        "category": "red",
        "category_label": "En retard (0/4 livrables)",
        "status_priority": "",
        "synthesis": {
            "coherence": "Dossier en cours de constitution.",
            "points_forts": "Apprenant engagé ayant déposé ses premiers livrables.",
            "chantiers": "Poursuivre la formalisation des livrables manquants.",
            "message": "Bienvenue dans le suivi du Projet Professionnel. Poursuivez vos dépôts pour compléter votre parcours."
        },
        "deliverables": {}
    }
    
    for d in DELIVERABLES_DEF:
        d_id = d["id"]
        new_learner["deliverables"][d_id] = {
            "id": d_id,
            "entrainement": {
                "submitted": False,
                "status": "Non soumis",
                "comment": "",
                "files": []
            },
            "final": {
                "submitted": False,
                "status": "En attente de remise finale",
                "score": None,
                "max_score": d["max_score"],
                "comment": "",
                "audit_v1": "",
                "files": []
            }
        }
        
    return new_learner

def detect_deliverable_and_phase(folder_name: str):
    """Détecte le livrable et la phase à partir du nom du dossier Moodle ou CPP."""
    norm = normalize_text(folder_name)
    phase = "final" if any(w in norm for w in ["final", "restitution", "definitif", "v2"]) else "entrainement"

    deliv_id = None
    for d in DELIVERABLES_DEF:
        if any(normalize_text(kw) in norm for kw in d['keywords']):
            deliv_id = d['id']
            break

    return deliv_id, phase

def get_submission_directories():
    """Identifie tous les répertoires sources possibles (PP, CPP, et variantes)."""
    valid_dirs = []
    seen_paths = set()
    candidates = ["PP", "CPP", "cpp", "pp"]
    for c in candidates:
        p = os.path.join(PROJECT_ROOT, c)
        if os.path.exists(p) and os.path.isdir(p):
            canon = os.path.normcase(os.path.realpath(p))
            if canon not in seen_paths:
                seen_paths.add(canon)
                valid_dirs.append(p)
            
    # Détecter également d'autres dossiers contenant PP ou CPP à la racine
    for item in os.listdir(PROJECT_ROOT):
        full_p = os.path.join(PROJECT_ROOT, item)
        if os.path.isdir(full_p) and ("PP" in item.upper() or "CPP" in item.upper()):
            if not item.startswith(".") and item not in ["DclicApp", "DclicAssistant"]:
                canon = os.path.normcase(os.path.realpath(full_p))
                if canon not in seen_paths:
                    seen_paths.add(canon)
                    valid_dirs.append(full_p)
                
    return valid_dirs

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

def scan_and_sync(auto_push=False):
    """Scanne les dossiers PP et CPP, intègre les nouveaux apprenants et met à jour DclicApp."""
    learners = load_initial_data()
    print(f"Chargement initial : {len(learners)} apprenants en mémoire.")

    source_dirs = get_submission_directories()
    if not source_dirs:
        print("⚠️ Aucun dossier source de soumissions trouvé (PP / CPP).")
        return

    print(f"Dossiers sources scannés : {[os.path.basename(d) for d in source_dirs]}")

    newly_added_learners = 0
    newly_added_submissions = 0

    for source_dir in source_dirs:
        for folder_name in sorted(os.listdir(source_dir)):
            folder_path = os.path.join(source_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            deliv_id, phase = detect_deliverable_and_phase(folder_name)
            if not deliv_id:
                # Vérifier si c'est un sous-dossier contenant des livrables
                continue

            print(f"\n📁 [{os.path.basename(source_dir)}] {folder_name} -> Livrable: {deliv_id} ({phase})")

            for sub in sorted(os.listdir(folder_path)):
                sub_path = os.path.join(folder_path, sub)
                if not os.path.isdir(sub_path):
                    continue

                # Association ou création automatique du dossier apprenant
                matched = match_learner_name(sub, learners)
                if not matched:
                    matched = create_new_learner(sub, learners)
                    learners.append(matched)
                    newly_added_learners += 1
                    print(f"  ✨ NOUVEL APPRENANT DÉCOUVERT ET AJOUTÉ : {matched['full_name']} (N° {matched['num']})")

                # Récupération des fichiers déposés
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
                was_already_submitted = phase_entry.get("submitted", False)
                
                phase_entry["submitted"] = True
                phase_entry["files"] = files
                
                if not was_already_submitted:
                    newly_added_submissions += 1

                # Détection automatique du budget si présent dans gest
                if deliv_id == "gest":
                    has_budget = any("budget" in f["name"].lower() for f in files)
                    if has_budget:
                        budget_deliv = matched["deliverables"].setdefault("budget", {})
                        b_phase = budget_deliv.setdefault(phase, {})
                        b_phase["submitted"] = True
                        b_phase["files"] = [f for f in files if "budget" in f["name"].lower()]
                        if not b_phase.get("status") or "Non soumis" in b_phase.get("status", ""):
                            b_phase["status"] = "✅ Soumis — Chiffrage budgétaire associé au Gantt"
                        if not b_phase.get("comment"):
                            b_phase["comment"] = "Budget prévisionnel intégré aux documents de gestion de projet bien pris en compte."

                # Statut et feedback automatique
                norm_nom = normalize_text(matched.get("nom", "")).lower()
                norm_prenom = normalize_text(matched.get("prenom", "")).lower()
                known_def = None
                for k, v in KNOWN_PROJECT_DEFS.items():
                    if k in norm_nom or k in norm_prenom or any(k in normalize_text(w) for w in matched["full_name"].split()):
                        known_def = v
                        break

                if known_def:
                    if known_def.get("projet"):
                        matched["projet"] = known_def["projet"]
                    if known_def.get("nom"):
                        matched["nom"] = known_def["nom"]
                    if known_def.get("prenom"):
                        matched["prenom"] = known_def["prenom"]
                    if known_def.get("full_name"):
                        matched["full_name"] = known_def["full_name"]
                    if known_def.get("synthesis"):
                        matched["synthesis"] = known_def["synthesis"]
                    if known_def.get("status_priority"):
                        matched["status_priority"] = known_def["status_priority"]

                current_status = phase_entry.get("status", "")
                if not current_status or "Non soumis" in current_status:
                    if phase == "entrainement":
                        if deliv_id == "desc":
                            phase_entry["status"] = "✅ Projet cadré"
                        else:
                            phase_entry["status"] = "🟡 Soumis — Bon travail, ajustements requis"
                    else:
                        phase_entry["status"] = "📥 Restitution finale déposée"

                # Attribuer le commentaire personnalisé s'il n'existe pas encore ou s'il était générique
                current_comment = phase_entry.get("comment", "")
                is_generic_comment = not current_comment or "a bien été reçu et pris en compte" in current_comment
                if is_generic_comment and known_def:
                    if deliv_id == "desc" and "desc_comment" in known_def:
                        phase_entry["comment"] = known_def["desc_comment"]
                    elif deliv_id == "strat" and "strat_comment" in known_def:
                        phase_entry["comment"] = known_def["strat_comment"]
                    elif deliv_id == "gest" and "gest_comment" in known_def:
                        phase_entry["comment"] = known_def["gest_comment"]
                    elif deliv_id == "tdb" and "tdb_comment" in known_def:
                        phase_entry["comment"] = known_def["tdb_comment"]

                # Feedback par défaut structuré pour tout autre travail sans commentaire
                if not phase_entry.get("comment"):
                    deliv_title = next((d["title"] for d in DELIVERABLES_DEF if d["id"] == deliv_id), deliv_id)
                    if phase == "entrainement":
                        phase_entry["comment"] = (
                            f"Document pour « {deliv_title} » bien reçu et pris en compte. "
                            f"Veillez à respecter scrupuleusement les critères de la grille officielle (faisabilité, cohérence avec vos personas et clarté des objectifs) "
                            f"pour votre version finale."
                        )

    # Nettoyage systématique de tous les commentaires et messages (zéro salutation, zéro signature)
    for l in learners:
        if "synthesis" in l and isinstance(l["synthesis"], dict):
            if "message" in l["synthesis"]:
                l["synthesis"]["message"] = clean_comment(l["synthesis"]["message"])
        for d in l.get("deliverables", {}).values():
            for phase_k in ["entrainement", "final"]:
                p_entry = d.get(phase_k, {})
                if "comment" in p_entry:
                    p_entry["comment"] = clean_comment(p_entry["comment"])

    # Recalcul des catégories et complétudes V1 / V2
    MOODLE_V1_IDS = ["desc", "strat", "gest", "tdb"]
    total_learners = len(learners)
    v1_full_count = 0
    v2_submitted_count = 0
    category_counts = {"green": 0, "yellow": 0, "red": 0}

    for l in learners:
        v1_count = sum(1 for did in MOODLE_V1_IDS if l["deliverables"].get(did, {}).get("entrainement", {}).get("submitted"))
        v2_count = sum(1 for d in l["deliverables"].values() if d.get("final", {}).get("submitted"))
        
        if v1_count >= 4:
            l["category"] = "green"
            l["category_label"] = f"Complet ({v1_count}/4 livrables)"
            category_counts["green"] += 1
            v1_full_count += 1
        elif v1_count >= 2:
            l["category"] = "yellow"
            l["category_label"] = f"Partiel ({v1_count}/4 livrables)"
            category_counts["yellow"] += 1
        else:
            l["category"] = "red"
            l["category_label"] = f"En retard ({v1_count}/4 livrables)"
            category_counts["red"] += 1

        if v2_count > 0:
            v2_submitted_count += 1

    # Statistiques par livrable
    deliverables_stats = {}
    for d_def in DELIVERABLES_DEF:
        d_id = d_def["id"]
        v1_subs = sum(1 for l in learners if l["deliverables"].get(d_id, {}).get("entrainement", {}).get("submitted"))
        v2_subs = sum(1 for l in learners if l["deliverables"].get(d_id, {}).get("final", {}).get("submitted"))
        deliverables_stats[d_id] = {
            "v1_submitted": v1_subs,
            "v1_rate": round((v1_subs / total_learners) * 100, 1) if total_learners else 0,
            "v2_submitted": v2_subs,
            "v2_rate": round((v2_subs / total_learners) * 100, 1) if total_learners else 0
        }

    stats = {
        "total_learners": total_learners,
        "v1_completed": v1_full_count,
        "v1_rate": round((v1_full_count / total_learners) * 100, 1) if total_learners else 0,
        "v2_submitted": v2_submitted_count,
        "v2_rate": round((v2_submitted_count / total_learners) * 100, 1) if total_learners else 0,
        "categories": category_counts,
        "deliverables_stats": deliverables_stats,
        "last_updated": datetime.now().isoformat()
    }

    output_data = {
        "stats": stats,
        "deliverables_def": DELIVERABLES_DEF,
        "learners": learners
    }

    # Sauvegarde de l'état persistant
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(learners, f, ensure_ascii=False, indent=2)

    # Sauvegarde des données pour le frontend DclicApp
    os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)
    with open(FRONTEND_TARGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n========================================================")
    print(f"✅ SYNCHRONISATION DU PROJET PROFESSIONNEL EFFECTUÉE")
    print(f"========================================================")
    print(f" - Apprenants totaux suivis : {total_learners} (dont {newly_added_learners} nouveaux)")
    print(f" - Soumissions actualisées  : {newly_added_submissions}")
    print(f" - Livrables V1 complets    : {v1_full_count} ({stats['v1_rate']}%)")
    print(f" - Vert (Complet)           : {category_counts['green']}")
    print(f" - Jaune (Partiel)          : {category_counts['yellow']}")
    print(f" - Rouge (En retard)        : {category_counts['red']}")
    print(f" - Fichier frontend à jour : {FRONTEND_TARGET_FILE}")
    print(f"========================================================")

    if auto_push:
        print("\n🚀 Poussée automatique vers GitHub...")
        push_to_git()

def push_to_git():
    """Effectue le commit et push automatique vers GitHub pour mettre à jour la plateforme."""
    try:
        app_dir = os.path.join(PROJECT_ROOT, "DclicApp")
        subprocess.run(["git", "add", "frontend/src/data/pp_evaluations.json"], cwd=app_dir, check=True)
        # Check if there is anything to commit
        diff = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=app_dir)
        if diff.returncode != 0:
            commit_msg = f"chore(pp): mise a jour automatique des evaluations ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=app_dir, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=app_dir, check=True)
            print("✅ DclicApp poussé avec succès vers GitHub origin/main !")
        else:
            print("ℹ️ Aucun changement à pousser pour DclicApp.")
    except Exception as e:
        print(f"⚠️ Erreur lors du push git : {e}")

if __name__ == "__main__":
    push_flag = "--push" in sys.argv
    scan_and_sync(auto_push=push_flag)

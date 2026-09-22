"""
audit_and_regenerate_comments.py — Audit complet et régénération des commentaires du Projet Professionnel

Ce script :
1. Lit les fichiers PDF/DOCX réels de chaque apprenant dans les dossiers PP/
2. Extrait le vrai nom de projet et le contexte depuis le fichier de Description
3. Compare avec les données actuelles dans pp_evaluations_state.json
4. Identifie les incohérences (projet mal attribué, commentaire mentionnant un autre projet)
5. Régénère les commentaires et le titre de projet pour les cas erronés
6. Met à jour les fichiers de données
"""

import os
import sys
import re
import json
import unicodedata
import random
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_FILE = os.path.join(PROJECT_ROOT, "pp_evaluations_state.json")
LEGACY_FILE = os.path.join(PROJECT_ROOT, "parsed_learners.json")
FRONTEND_DATA_DIR = os.path.join(PROJECT_ROOT, "DclicApp", "frontend", "src", "data")
FRONTEND_TARGET_FILE = os.path.join(FRONTEND_DATA_DIR, "pp_evaluations.json")
PP_DIR = os.path.join(PROJECT_ROOT, "PP")

# Tentative d'import des librairies de lecture de fichiers
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def normalize_text(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r"['\'\-]", ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).lower()
    return ' '.join(text.split())


def read_file_content(filepath: str, max_pages: int = 3) -> str:
    """Extrait le texte d'un fichier PDF ou DOCX."""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.pdf' and HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(filepath)
            text = ''
            for page in reader.pages[:max_pages]:
                text += (page.extract_text() or '') + '\n'
            return text.strip()
        except Exception as e:
            return f"[Erreur lecture PDF: {e}]"
    
    elif ext == '.docx' and HAS_DOCX:
        try:
            doc = docx.Document(filepath)
            text = '\n'.join([p.text for p in doc.paragraphs[:50]])
            return text[:3000].strip()
        except Exception as e:
            return f"[Erreur lecture DOCX: {e}]"
    
    return ""


def extract_project_info(text: str) -> dict:
    """Extrait les informations du projet depuis le texte du fichier de description."""
    info = {
        "sujet": None,
        "project_name": None,
        "context": None,
        "activity": None,
        "target": None,
        "objective": None,
        "keywords": []
    }
    
    text_lower = text.lower()
    
    # Extraction du numéro de sujet
    sujet_match = re.search(r'sujet\s*(?:n[°o]?\s*)?(\d+|libre)', text_lower)
    if sujet_match:
        info["sujet"] = sujet_match.group(1)
    
    # Extraction du nom du projet (patterns courants)
    project_patterns = [
        r'(?:nom\s+du\s+projet|intitulé|titre\s+du\s+projet|projet\s*:)\s*[:\-–]?\s*[«""]?\s*(.+?)(?:[»""]|\n|$)',
        r'[«""]([^»""]{5,80})[»""]',  # Texte entre guillemets
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if len(name) > 5 and len(name) < 150:
                info["project_name"] = name
                break
    
    # Extraction du contexte
    context_match = re.search(r'(?:contexte|type\s+d.entreprise)\s*[:\-–]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if context_match:
        info["context"] = context_match.group(1).strip()[:200]
    
    # Extraction de l'activité
    activity_match = re.search(r'activit[ée]\s*(?:\(produit\s+ou\s+service\))?\s*[:\-–]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if activity_match:
        info["activity"] = activity_match.group(1).strip()[:200]
    
    # Extraction de la cible
    target_match = re.search(r'cible\s*[:\-–]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if target_match:
        info["target"] = target_match.group(1).strip()[:200]
    
    # Extraction de l'objectif
    obj_match = re.search(r'objectif\s*[:\-–]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if obj_match:
        info["objective"] = obj_match.group(1).strip()[:200]
    
    # Mots-clés du projet (termes distinctifs)
    distinctive_terms = [
        'téléconsultation', 'teleconsultation', 'télémédecine', 'telemedecine',
        'chaîne de télévision', 'chaine de television', 'télévision', 'television', 'tv',
        'e-commerce', 'ecommerce', 'boutique en ligne',
        'restauration', 'restaurant', 'fast food', 'cuisine',
        'beauté', 'cosmétique', 'cosmétiques', 'soins', 'crèmes', 'cremes',
        'soutien scolaire', 'formation', 'académie', 'école', 'ecole',
        'agroalimentaire', 'épices', 'épicerie',
        'énergie solaire', 'solaire', 'photovoltaïque',
        'immobilier', 'foncier', 'foncière',
        'assainissement', 'recyclage', 'déchet', 'déchets', 'écologie',
        'transfert d\'argent', 'services financiers',
        'tourisme', 'expériences', 'artisanat',
        'événementiel', 'événements',
        'média', 'media', 'contenu', 'content', 'copywriting',
        'prêt-à-porter', 'mode', 'vêtements', 'vetements',
        'élevage', 'agriculture', 'aquaculture',
        'boissons', 'jus',
        'marketplace', 'plateforme',
    ]
    
    for term in distinctive_terms:
        if term in text_lower:
            info["keywords"].append(term)
    
    return info


def check_comment_coherence(comment: str, project_name: str, project_keywords: list) -> dict:
    """Vérifie si un commentaire est cohérent avec le projet de l'apprenant."""
    result = {
        "coherent": True,
        "issues": []
    }
    
    if not comment or len(comment) < 30:
        return result
    
    comment_lower = comment.lower()
    
    # Liste des noms de projets connus pour vérifier les mentions croisées
    known_project_names = [
        ('écoclean', 'ÉcoClean Bénin'),
        ('ecoclean', 'ÉcoClean Bénin'),
        ('mediconnect', 'MediConnect'),
        ('doer team', 'Doer Team Kids Academy'),
        ('kds school', 'KDS School'),
        ("spag'chaud", "Spag'Chaud"),
        ('spagchaud', "Spag'Chaud"),
        ('cosna', 'COSNA Investments'),
        ('tiktok prêt', 'TikTok Prêt-à-Porter'),
        ('clap famille', 'Clap Famille 360°'),
        ('yonwa', 'Yonwa'),
        ('kola épicerie', 'Kola Épicerie'),
        ('kola cube', 'Kola Cube'),
        ('aura', 'AURA Boissons'),
        ('nkina', 'NKINA'),
        ('solaris', 'SOLARIS'),
        ('allo doc', 'Allo Doc 237'),
        ('bariba', 'Bariba Startup Academy'),
        ('altitude', 'ALTITUDE'),
        ('afrifam', 'AFRIFAM TV'),
        ('digital empire', 'Digital Empire'),
        ('ak espace', 'AK Espace Numérique'),
        ('immobilier haho', 'Immobilier Haho'),
        ('mediproche', 'MédiProche'),
        ('eventure', 'EVENTURE MANAGEMENT'),
        ('agence express', 'Agence Express Union'),
        ('bella\'care', "BELLA'CARE"),
        ('nayaskin', 'NayaSkin'),
        ('skin\'tech', "Skin'Tech"),
        ('agro-aqua', 'AGRO-AQUA BORGOU'),
    ]
    
    project_name_lower = (project_name or '').lower()
    
    for search_term, display_name in known_project_names:
        if search_term in comment_lower and search_term not in project_name_lower:
            result["coherent"] = False
            result["issues"].append(f"Commentaire mentionne '{display_name}' alors que le projet est '{project_name}'")
    
    # Vérification par mots-clés sectoriels
    sector_keywords = {
        'assainissement': ['recyclage', 'déchet', 'collecte', 'tri'],
        'téléconsultation': ['médecin', 'santé', 'patient', 'consultation'],
        'restauration': ['repas', 'menu', 'cuisine', 'restaurant'],
        'chaîne de télévision': ['audience', 'téléspectateur', 'diffusion', 'émission'],
        'e-commerce beauté': ['crèmes', 'beauté', 'soins', 'peau'],
        'soutien scolaire': ['élèves', 'cours', 'scolaire', 'bilingue'],
    }
    
    return result


def generate_desc_comment(project_info: dict, learner_name: str) -> str:
    """Génère un commentaire de description basé sur les infos réelles du projet."""
    project_name = project_info.get("project_name", "")
    activity = project_info.get("activity", "")
    context = project_info.get("context", "")
    target = project_info.get("target", "")
    objective = project_info.get("objective", "")
    sujet = project_info.get("sujet", "")
    keywords = project_info.get("keywords", [])
    
    # Construction d'un commentaire formatif adapté
    parts = []
    
    if project_name:
        parts.append(f"Votre note de cadrage pour {project_name} est bien structurée.")
    else:
        parts.append("Votre note de cadrage est bien structurée.")
    
    if activity:
        parts.append(f"L'activité choisie ({activity}) est clairement présentée.")
    
    if target:
        parts.append(f"Le ciblage ({target}) est pertinent et bien identifié.")
    
    if objective:
        parts.append(f"L'objectif de {objective.lower()} est bien formulé.")
    
    # Recommandations pour le livrable 1
    parts.append("Pour le Livrable 1 (Stratégie marketing) : définissez 2 personas types détaillés, analysez au moins 3 offres concurrentes, et fixez des objectifs SMART chiffrés d'acquisition.")
    
    return " ".join(parts)


def generate_strat_comment(project_info: dict, file_text: str) -> str:
    """Génère un commentaire de stratégie marketing basé sur le contenu réel."""
    project_name = project_info.get("project_name", "")
    text_lower = file_text.lower()
    
    parts = []
    
    if project_name:
        parts.append(f"Votre document de stratégie marketing pour {project_name} a bien été analysé.")
    else:
        parts.append("Votre document de stratégie marketing a bien été analysé.")
    
    # Vérification des éléments présents
    has_personas = any(w in text_lower for w in ['persona', 'profil type', 'cible 1', 'cible 2'])
    has_competitors = any(w in text_lower for w in ['concurrent', 'benchmark', 'concurrence', 'analyse concurrentielle'])
    has_smart = any(w in text_lower for w in ['smart', 'objectif chiffré', 'objectifs chiffrés'])
    
    if has_personas:
        parts.append("Vos personas sont présents et identifiés.")
    else:
        parts.append("Veillez à bien définir 2 personas types détaillés pour le rendu final.")
    
    if has_competitors:
        parts.append("L'analyse concurrentielle est amorcée.")
    else:
        parts.append("Pensez à intégrer une analyse d'au moins 3 concurrents directs ou indirects.")
    
    if has_smart:
        parts.append("Les objectifs SMART sont abordés.")
    else:
        parts.append("Précisez des objectifs SMART chiffrés et mesurables pour le dépôt final.")
    
    parts.append("Veillez à ce que votre texte reste sous le plafond de 1000 mots pour le rendu final.")
    
    return " ".join(parts)


def generate_gest_comment(project_info: dict, file_text: str) -> str:
    """Génère un commentaire de gestion de projet basé sur le contenu réel."""
    project_name = project_info.get("project_name", "")
    text_lower = file_text.lower()
    
    parts = []
    
    if project_name:
        parts.append(f"Votre document de gestion de projet pour {project_name} a été examiné.")
    else:
        parts.append("Votre document de gestion de projet a été examiné.")
    
    has_gantt = any(w in text_lower for w in ['gantt', 'planning', 'chronogramme', 'diagramme'])
    has_rh = any(w in text_lower for w in ['ressources humaines', 'équipe', 'profils', 'compétences', 'collaborateur'])
    has_budget = any(w in text_lower for w in ['budget', 'coût', 'cout', 'chiffrage', 'fcfa', 'cfa'])
    
    if has_gantt:
        parts.append("Le planning/Gantt est présent et structuré.")
    else:
        parts.append("Veillez à formaliser un planning Gantt clair avec les jalons clés pour le dépôt final.")
    
    if has_rh:
        parts.append("L'affectation des ressources humaines est abordée.")
    else:
        parts.append("Détaillez l'affectation nominative des profils RH nécessaires.")
    
    if has_budget:
        parts.append("Le volet budgétaire est mentionné.")
    else:
        parts.append("N'oubliez pas d'intégrer le chiffrage budgétaire par tâche.")
    
    return " ".join(parts)


def generate_tdb_comment(project_info: dict, file_text: str) -> str:
    """Génère un commentaire de tableau de bord basé sur le contenu réel."""
    project_name = project_info.get("project_name", "")
    text_lower = file_text.lower()
    
    parts = []
    
    if project_name:
        parts.append(f"Votre tableau de bord d'indicateurs pour {project_name} a été examiné.")
    else:
        parts.append("Votre tableau de bord d'indicateurs a été examiné.")
    
    has_kpis = any(w in text_lower for w in ['kpi', 'indicateur', 'métrique', 'metrique', 'taux'])
    has_channels = any(w in text_lower for w in ['facebook', 'instagram', 'whatsapp', 'tiktok', 'youtube', 'google'])
    
    if has_kpis:
        parts.append("Les indicateurs de performance sont identifiés.")
    else:
        parts.append("Précisez des KPIs clairs et mesurables par canal.")
    
    if has_channels:
        parts.append("Les canaux de suivi sont bien présents.")
    
    parts.append("Veillez scrupuleusement à ce que votre texte d'accompagnement justifiant le choix des métriques compte strictement moins de 100 mots pour respecter la consigne officielle.")
    
    return " ".join(parts)


def generate_budget_comment(project_info: dict, file_text: str) -> str:
    """Génère un commentaire de budget basé sur le contenu réel."""
    project_name = project_info.get("project_name", "")
    
    if project_name:
        return f"Budget prévisionnel pour {project_name} bien reçu et pris en compte. Veillez à détailler le chiffrage par tâche et par phase pour le rendu final, avec une ventilation claire en FCFA."
    return "Budget prévisionnel bien reçu et pris en compte. Veillez à détailler le chiffrage par tâche et par phase pour le rendu final, avec une ventilation claire en FCFA."


def run_full_audit():
    """Exécute l'audit complet de tous les apprenants."""
    
    # Charger les données actuelles
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            learners = json.load(f)
    elif os.path.exists(LEGACY_FILE):
        with open(LEGACY_FILE, 'r', encoding='utf-8') as f:
            learners = json.load(f)
    else:
        print("❌ Aucun fichier de données trouvé.")
        return
    
    print(f"📊 Audit de {len(learners)} apprenants...")
    print()
    
    # Identifier les dossiers de livrables dans PP/
    livrable_dirs = {}
    if os.path.exists(PP_DIR):
        for folder_name in sorted(os.listdir(PP_DIR)):
            folder_path = os.path.join(PP_DIR, folder_name)
            if not os.path.isdir(folder_path):
                continue
            folder_lower = folder_name.lower()
            if 'description' in folder_lower:
                livrable_dirs['desc'] = folder_path
            elif 'stratégie' in folder_lower or 'strategie' in folder_lower or 'marketing' in folder_lower:
                livrable_dirs['strat'] = folder_path
            elif 'gestion' in folder_lower:
                livrable_dirs['gest'] = folder_path
            elif 'tableau de bord' in folder_lower or 'tableau' in folder_lower:
                livrable_dirs['tdb'] = folder_path
    
    print(f"📁 Dossiers de livrables détectés : {list(livrable_dirs.keys())}")
    
    mismatches = []
    corrections = []
    total_checked = 0
    total_corrected = 0
    
    for learner in learners:
        full_name = learner.get('full_name', '')
        nom = learner.get('nom', '')
        projet_actuel = learner.get('projet', '')
        
        # Trouver le dossier de l'apprenant dans chaque livrable
        learner_files = {}  # {livrable_id: {folder_path, files, text}}
        
        for livrable_id, livrable_path in livrable_dirs.items():
            for sub in os.listdir(livrable_path):
                sub_path = os.path.join(livrable_path, sub)
                if not os.path.isdir(sub_path):
                    continue
                
                # Matching par nom
                clean_sub = sub.split('_')[0].strip()
                norm_sub = normalize_text(clean_sub)
                norm_full = normalize_text(full_name)
                norm_nom = normalize_text(nom)
                
                sub_words = set(norm_sub.split())
                full_words = set(norm_full.split())
                nom_words = set(norm_nom.split())
                
                # Match exact ou forte intersection
                if sub_words == full_words or (nom_words and nom_words.issubset(sub_words) and len(sub_words.intersection(full_words)) >= 2):
                    files = [f for f in os.listdir(sub_path) if os.path.isfile(os.path.join(sub_path, f))]
                    learner_files[livrable_id] = {
                        "folder": sub_path,
                        "files": files,
                        "text": ""
                    }
                    # Lire le premier fichier
                    for f in files:
                        fpath = os.path.join(sub_path, f)
                        text = read_file_content(fpath)
                        if text and len(text) > 50:
                            learner_files[livrable_id]["text"] = text
                            break
                    break
        
        if not learner_files:
            continue
        
        total_checked += 1
        
        # Extraire les infos du projet depuis la description
        project_info = {"project_name": None, "sujet": None, "keywords": []}
        if 'desc' in learner_files and learner_files['desc']['text']:
            project_info = extract_project_info(learner_files['desc']['text'])
        
        # Vérifier la cohérence du projet
        real_project = project_info.get("project_name")
        needs_correction = False
        correction_reasons = []
        
        # 1. Vérifier si le nom de projet actuel correspond au fichier
        if real_project and projet_actuel:
            # Normaliser pour comparaison
            norm_real = normalize_text(real_project)
            norm_actual = normalize_text(projet_actuel)
            
            # Vérifier si au moins un mot significatif du projet réel est dans le projet actuel
            real_words = set(w for w in norm_real.split() if len(w) > 3)
            actual_words = set(w for w in norm_actual.split() if len(w) > 3)
            
            overlap = real_words.intersection(actual_words)
            if len(overlap) < 1 and len(real_words) > 0:
                needs_correction = True
                correction_reasons.append(f"Projet JSON: '{projet_actuel}' ≠ Projet fichier: '{real_project}'")
        
        # 2. Vérifier la cohérence des commentaires
        for did in ['desc', 'strat', 'gest', 'tdb']:
            deliv = learner.get('deliverables', {}).get(did, {})
            comment = deliv.get('entrainement', {}).get('comment', '')
            if comment:
                coherence = check_comment_coherence(comment, projet_actuel, project_info.get('keywords', []))
                if not coherence["coherent"]:
                    needs_correction = True
                    for issue in coherence["issues"]:
                        correction_reasons.append(f"[{did}] {issue}")
        
        if needs_correction:
            mismatches.append({
                "learner": full_name,
                "num": learner.get("num"),
                "current_project": projet_actuel,
                "real_project": real_project,
                "reasons": correction_reasons
            })
            
            print(f"  ❌ MISMATCH: {full_name} (N°{learner.get('num')})")
            for reason in correction_reasons:
                print(f"      → {reason}")
            
            # Appliquer les corrections
            if real_project:
                # Mettre à jour le titre du projet
                learner["projet"] = real_project
                
                # Régénérer la synthèse
                activity = project_info.get("activity", "")
                target = project_info.get("target", "")
                objective = project_info.get("objective", "")
                
                v1_count = sum(1 for did in ['desc', 'strat', 'gest', 'tdb'] 
                              if learner.get('deliverables', {}).get(did, {}).get('entrainement', {}).get('submitted'))
                
                synth_parts = []
                if activity:
                    synth_parts.append(f"Le projet porte sur : {activity}.")
                if target:
                    synth_parts.append(f"Cible identifiée : {target}.")
                if objective:
                    synth_parts.append(f"Objectif : {objective}.")
                
                coherence_text = " ".join(synth_parts) if synth_parts else f"Projet {real_project} en cours de développement."
                
                if v1_count >= 4:
                    coherence_text += f" Parcours V1 complet ({v1_count}/4 livrables déposés)."
                    message = f"Le dossier pour {real_project} est bien avancé avec tous les livrables V1 déposés. Poursuivre la structuration pour la restitution finale."
                elif v1_count >= 2:
                    coherence_text += f" Parcours en bonne voie ({v1_count}/4 livrables déposés)."
                    message = f"Bon démarrage pour {real_project}. Poursuivre les dépôts de livrables manquants pour compléter le parcours V1."
                else:
                    coherence_text += f" Début de parcours ({v1_count}/4 livrables déposés)."
                    message = f"Le projet {real_project} est amorcé. Accélérer les dépôts de livrables pour rattraper le retard."
                
                learner["synthesis"] = {
                    "coherence": coherence_text,
                    "points_forts": f"Projet {real_project} identifié et cadré.",
                    "chantiers": f"Finaliser les livrables manquants et préparer la restitution finale.",
                    "message": message
                }
            
            # Régénérer les commentaires de chaque livrable
            for did in ['desc', 'strat', 'gest', 'tdb', 'budget']:
                deliv = learner.get('deliverables', {}).get(did, {})
                ent = deliv.get('entrainement', {})
                
                if not ent.get('submitted'):
                    continue
                
                file_text = learner_files.get(did, {}).get("text", "")
                
                if did == 'desc':
                    new_comment = generate_desc_comment(project_info, full_name)
                elif did == 'strat':
                    new_comment = generate_strat_comment(project_info, file_text)
                elif did == 'gest':
                    new_comment = generate_gest_comment(project_info, file_text)
                elif did == 'tdb':
                    new_comment = generate_tdb_comment(project_info, file_text)
                elif did == 'budget':
                    new_comment = generate_budget_comment(project_info, file_text)
                else:
                    continue
                
                old_comment = ent.get('comment', '')
                if old_comment != new_comment:
                    ent['comment'] = new_comment
                    corrections.append({
                        "learner": full_name,
                        "deliverable": did,
                        "old_comment_preview": old_comment[:80] + "..." if len(old_comment) > 80 else old_comment,
                        "new_comment_preview": new_comment[:80] + "..." if len(new_comment) > 80 else new_comment
                    })
            
            total_corrected += 1
        else:
            # Vérifier quand même que les commentaires ne contiennent pas de salutations/signatures
            for did in ['desc', 'strat', 'gest', 'tdb', 'budget']:
                deliv = learner.get('deliverables', {}).get(did, {})
                for phase_k in ['entrainement', 'final']:
                    p = deliv.get(phase_k, {})
                    comment = p.get('comment', '')
                    if comment:
                        # Nettoyage salutations et signatures
                        cleaned = re.sub(r'^[ \t]*Bonjour\b[^\n,]*,\s*\n*', '', comment, flags=re.IGNORECASE)
                        cleaned = re.sub(r'^[ \t]*Bonjour\b[^\n]*\n+', '', cleaned, flags=re.IGNORECASE)
                        cleaned = re.sub(r'\s*\n+[ \t]*(?:Ton|Votre)\s+tuteur(?:\s+D-?CLIC)?\.?[ \t]*$', '', cleaned, flags=re.IGNORECASE)
                        cleaned = cleaned.strip()
                        if cleaned != comment:
                            p['comment'] = cleaned
    
    # Sauvegarder les corrections
    print()
    print("=" * 80)
    print(f"📊 RÉSULTATS DE L'AUDIT")
    print("=" * 80)
    print(f"  Apprenants vérifiés : {total_checked}")
    print(f"  Incohérences détectées : {len(mismatches)}")
    print(f"  Apprenants corrigés : {total_corrected}")
    print(f"  Commentaires régénérés : {len(corrections)}")
    
    if mismatches:
        print()
        print("📋 DÉTAIL DES INCOHÉRENCES :")
        for m in mismatches:
            print(f"  • {m['learner']} (N°{m['num']})")
            print(f"    Projet JSON : {m['current_project']}")
            print(f"    Projet réel : {m['real_project']}")
            for r in m['reasons']:
                print(f"    → {r}")
    
    # Sauvegarder
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(learners, f, ensure_ascii=False, indent=2)
    
    # Mettre à jour aussi parsed_learners.json (legacy)
    if os.path.exists(LEGACY_FILE):
        legacy = json.load(open(LEGACY_FILE, 'r', encoding='utf-8'))
        # Appliquer les mêmes corrections au fichier legacy
        for learner in learners:
            for legacy_l in legacy:
                if normalize_text(legacy_l.get('full_name', '')) == normalize_text(learner.get('full_name', '')):
                    legacy_l['projet'] = learner['projet']
                    if 'synthesis' in learner:
                        legacy_l['synthesis'] = learner['synthesis']
                    # Mettre à jour les commentaires dans le format legacy
                    deliv_map = {0: 'desc', 1: 'strat', 2: 'gest', 3: 'budget', 4: 'content', 5: 'tdb'}
                    for idx, did in deliv_map.items():
                        if idx < len(legacy_l.get('deliverables', [])):
                            new_comment = learner.get('deliverables', {}).get(did, {}).get('entrainement', {}).get('comment', '')
                            if new_comment:
                                legacy_l['deliverables'][idx]['comment'] = new_comment
                    break
        
        with open(LEGACY_FILE, 'w', encoding='utf-8') as f:
            json.dump(legacy, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ État sauvegardé dans {STATE_FILE}")
    print(f"✅ Fichier legacy mis à jour : {LEGACY_FILE}")
    
    return learners, mismatches, corrections


if __name__ == "__main__":
    run_full_audit()

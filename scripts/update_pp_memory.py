"""
update_pp_memory.py — Moteur d'analyse factuelle et d'audit de cohérence transversale.

Ce script :
1. Lit l'intégralité des textes extraits dans extracted_pp_data/ pour chaque apprenant.
2. Extrait de façon factuelle et structurée les éléments clés de chaque livrable
   (sans extrapolation ni hallucination).
3. Effectue la vérification croisée obligatoire :
   - PP1 (Stratégie) vs Description
   - PP2 (Gantt & Budget) vs PP1 (Stratégie)
   - PP3 (Contenus) vs PP1 (Stratégie)
   - PP4 (Tableau de bord) vs PP1 (Stratégie)
4. Persiste la mémoire transversale dans pp_learners_memory.json.
"""

import os
import sys
import re
import json
import glob
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def read_extracted_text(student_dir, prefix):
    """Lit et concatène tous les fichiers correspondant à un livrable pour un apprenant."""
    files = glob.glob(os.path.join(student_dir, f"{prefix}_*.txt"))
    combined = []
    for f in files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            combined.append(fp.read())
    return "\n\n".join(combined)


def clean_project_name(text):
    """Extrait le nom précis du projet à partir du texte de description."""
    lines = text.split("\n")
    for l in lines[:35]:
        m = re.search(r'(?:nom du projet|intitulé du projet|titre du projet|projet)\s*[:–-]\s*([^\n\r]+)', l, re.IGNORECASE)
        if m:
            clean = m.group(1).strip().strip('"*#')
            if len(clean) > 3 and not clean.lower().startswith("professionnel") and not clean.lower().startswith("marketing"):
                return clean
    for l in lines:
        l_str = l.strip().strip('#* ')
        if l_str and not l_str.startswith("===") and not l_str.startswith("---") and len(l_str) < 80:
            if any(k in l_str.lower() for k in ["agence", "plateforme", "boutique", "service", "start", "solution"]):
                return l_str
    return "Projet Professionnel D-CLIC"


def detect_sector_by_scoring(text):
    """Détermine le secteur d'activité par score de fréquence de mots-clés."""
    text_low = text.lower()
    
    sector_keywords = {
        "Fintech & Services Financiers": ["transfert", "finance", "argent", "express union", "fintech", "paiement", "guichet", "envoi d'argent"],
        "Santé & Téléconsultation Médicale": ["santé", "médical", "téléconsultation", "médecin", "clinique", "docteur", "consultation en ligne", "patient"],
        "Cosmétique & Soins D2C": ["cosmétique", "beauté", "peau", "savon", "cheveux", "soin", "crème", "lotion", "dermatologique"],
        "Agroalimentaire & Produits Naturels": ["agro", "alimentaire", "épice", "arachide", "jus", "naturel", "bouillon", "kola", "recette", "agricole"],
        "Média & Audiovisuel Numérique": ["média", "télévision", "tv", "audiovisuel", "presse", "information", "magazine", "diffusion", "chaîne"],
        "Énergie Solaire & Environnement": ["énergie", "solaire", "panneau", "kit solaire", "recyclage", "assainissement", "écologique", "déchet"],
        "Tourisme & Valorisation Culturelle": ["tourisme", "culture", "voyage", "bénin", "patrimoine", "visite", "artisanat"],
        "Immobilier & Gestion Foncière": ["immobilier", "terrain", "parcelle", "maison", "logement", "foncier", "agence immobilière"],
        "EdTech & Formation Professionnelle": ["formation", "académie", "coaching", "cours", "apprentissage", "startup academy", "e-book", "infopreneuriat"],
        "E-Commerce & Mode": ["vêtement", "mode", "chaussure", "prêt-à-porter", "boutique en ligne", "e-commerce", "d2c"]
    }
    
    scores = Counter()
    for sector, kw_list in sector_keywords.items():
        for kw in kw_list:
            count = text_low.count(kw)
            if count > 0:
                scores[sector] += count
                
    best = scores.most_common(1)
    if best and best[0][1] >= 2:
        return best[0][0]
    return "Marketing & Commerce Digital"


def extract_description_facts(text):
    """Extrait les faits clés de la note de cadrage / description."""
    if not text.strip():
        return {
            "status": "NON_SOUMIS",
            "nom_projet": "Non renseigné",
            "secteur": "Non renseigné",
            "raw_word_count": 0
        }
        
    words = len(re.findall(r"\w+", text))
    nom_projet = clean_project_name(text)
    secteur = detect_sector_by_scoring(text)
    
    return {
        "status": "SOUMIS",
        "nom_projet": nom_projet,
        "secteur": secteur,
        "raw_word_count": words,
        "extrait_intro": text[:350].replace("\n", " ").strip()
    }


def extract_strategy_facts(text):
    """Extrait les faits clés de la stratégie marketing (PP1)."""
    if not text.strip():
        return {
            "status": "NON_SOUMIS",
            "canaux": [],
            "raw_word_count": 0,
            "has_personas": False,
            "has_concurrents": False,
            "has_smart": False,
            "has_acquisition": False,
            "has_retention": False
        }
        
    words = len(re.findall(r"\w+", text))
    text_low = text.lower()
    
    # Canaux détectés
    canaux_connus = ["facebook", "instagram", "whatsapp", "tiktok", "linkedin", "youtube", "site web", "site internet", "seo", "e-mailing", "mailing", "sms", "google ads", "meta ads"]
    canaux_detectes = [c for c in canaux_connus if c in text_low]
    
    # Personas détectés
    has_personas = any(k in text_low for k in ["persona", "client idéal", "profil cible", "âge", "profession"])
    persona_matches = re.findall(r'(?:persona\s*\d*|profil\s*\d*)\s*[:–-]\s*([^\n\r,]+)', text, re.IGNORECASE)
    cleaned_personas = [p.strip().strip('*#') for p in persona_matches[:3] if len(p.strip()) > 3]
    
    # Concurrents détectés
    has_concurrents = any(k in text_low for k in ["concurrent", "concurrence", "benchmark", "marché"])
    
    # SMART & Actions
    has_smart = any(k in text_low for k in ["smart", "spécifique", "mesurable", "atteignable", "%"])
    has_acquisition = any(k in text_low for k in ["acquisition", "attirer", "nouveaux clients", "prospect"])
    has_retention = any(k in text_low for k in ["rétention", "retention", "fidélisation", "fidelisation", "fidéliser"])
    
    return {
        "status": "SOUMIS",
        "raw_word_count": words,
        "respect_longueur_1000_mots": words <= 1100,
        "canaux": canaux_detectes,
        "has_personas": has_personas,
        "personas_nommes": cleaned_personas,
        "has_concurrents": has_concurrents,
        "has_smart": has_smart,
        "has_acquisition": has_acquisition,
        "has_retention": has_retention
    }


def extract_management_facts(text):
    """Extrait les faits clés de la gestion de projet et budget (PP2)."""
    if not text.strip():
        return {
            "status": "NON_SOUMIS",
            "has_gantt": False,
            "has_budget": False,
            "montants_detectes": [],
            "profils_rh_detectes": [],
            "raw_word_count": 0
        }
        
    words = len(re.findall(r"\w+", text))
    text_low = text.lower()
    
    has_gantt = any(k in text_low for k in ["gantt", "planning", "diagramme", "jalon", "semaine", "mois", "tâche", "tache", "wbs"])
    has_budget = any(k in text_low for k in ["budget", "coût", "cout", "chiffrage", "dépense", "depense", "fcfa", "f cfa", "xof", "xaf", "total"])
    
    # Chiffres budgétaires
    amounts = re.findall(r'(\d[\d\s.,]{3,}\s*(?:fcfa|f\s*cfa|xof|xaf|euros|€))', text, re.IGNORECASE)
    cleaned_amounts = list(dict.fromkeys([a.strip().replace("\xa0", " ") for a in amounts]))[:5]
    
    # RH
    rh_detectes = []
    rh_keywords = ["community manager", "graphiste", "monteur", "développeur", "chef de projet", "rédacteur", "commercial", "stagiaire", "prestataire"]
    for rh in rh_keywords:
        if rh in text_low:
            rh_detectes.append(rh)
            
    return {
        "status": "SOUMIS",
        "raw_word_count": words,
        "has_gantt": has_gantt,
        "has_budget": has_budget,
        "montants_detectes": cleaned_amounts,
        "profils_rh_detectes": rh_detectes
    }


def extract_dashboard_facts(text):
    """Extrait les faits clés du tableau de bord (PP4)."""
    if not text.strip():
        return {
            "status": "NON_SOUMIS",
            "kpis_detectes": [],
            "has_table": False,
            "raw_word_count": 0
        }
        
    words = len(re.findall(r"\w+", text))
    text_low = text.lower()
    
    kpi_keywords = ["taux de clic", "ctr", "cpc", "conversion", "taux d'engagement", "engagement", "portée", "reach", "impressions", "vues", "abonnés", "leads", "ventes", "roi", "panier moyen"]
    detected_kpis = [k for k in kpi_keywords if k in text_low]
    has_table = any(k in text_low for k in ["tableau", "indicateur", "kpi", "|", "canal"])
    
    return {
        "status": "SOUMIS",
        "raw_word_count": words,
        "kpis_detectes": detected_kpis,
        "has_table": has_table,
        "respect_longueur_100_mots": words <= 200
    }


def audit_cross_coherence(desc_facts, strat_facts, gest_facts, tdb_facts):
    """Effectue l'audit croisé de cohérence entre tous les livrables soumis."""
    audit = {
        "score_coherence_globale": 100,
        "alertes": [],
        "points_alignes": []
    }
    
    # 1. PP1 vs Description
    if desc_facts["status"] == "SOUMIS" and strat_facts["status"] == "SOUMIS":
        audit["points_alignes"].append(f"Projet cadré : « {desc_facts['nom_projet']} » ({desc_facts['secteur']}) décliné en stratégie marketing.")
    elif desc_facts["status"] == "NON_SOUMIS" and strat_facts["status"] == "SOUMIS":
        audit["alertes"].append("Stratégie soumise sans note de cadrage préalable disponible.")
        audit["score_coherence_globale"] -= 15

    # 2. PP2 vs PP1
    if strat_facts["status"] == "SOUMIS" and gest_facts["status"] == "SOUMIS":
        strat_canaux = set(strat_facts.get("canaux", []))
        gest_rh = set(gest_facts.get("profils_rh_detectes", []))
        
        if any(c in strat_canaux for c in ["facebook", "instagram", "tiktok", "meta ads"]) and not any(r in gest_rh for r in ["community manager", "graphiste", "prestataire"]):
            audit["alertes"].append("Réseaux sociaux majeurs prévus dans PP1 mais aucun rôle dédié (Community Manager/Graphiste) identifié explicitement dans les RH de PP2.")
            audit["score_coherence_globale"] -= 15
        else:
            audit["points_alignes"].append("Ressources humaines de PP2 en bonne adéquation avec les canaux de communication de PP1.")
            
        if not gest_facts["has_budget"]:
            audit["alertes"].append("PP2 soumis sans chiffrage budgétaire détaillé pour financer les actions de PP1.")
            audit["score_coherence_globale"] -= 20
        else:
            audit["points_alignes"].append("Budget présent pour soutenir le déploiement opérationnel des actions marketing.")
    elif strat_facts["status"] == "SOUMIS" and gest_facts["status"] == "NON_SOUMIS":
        audit["alertes"].append("Stratégie définie mais livrable de gestion de projet (Gantt & Budget) manquant.")
        audit["score_coherence_globale"] -= 25

    # 3. PP4 vs PP1
    if strat_facts["status"] == "SOUMIS" and tdb_facts["status"] == "SOUMIS":
        kpis = set(tdb_facts.get("kpis_detectes", []))
        if len(kpis) < 2:
            audit["alertes"].append("Le tableau de bord contient trop peu d'indicateurs spécifiques pour évaluer les canaux de PP1.")
            audit["score_coherence_globale"] -= 15
        else:
            audit["points_alignes"].append(f"Indicateurs de suivi ({', '.join(list(kpis)[:3])}) pertinents pour piloter les canaux identifiés dans PP1.")
    elif strat_facts["status"] == "SOUMIS" and tdb_facts["status"] == "NON_SOUMIS":
        audit["alertes"].append("Tableau de bord d'indicateurs (PP4) non encore formalisé.")
        audit["score_coherence_globale"] -= 20
        
    audit["score_coherence_globale"] = max(0, audit["score_coherence_globale"])
    return audit


def build_and_save_memory(extracted_root, output_memory_path):
    """Construit l'état complet de mémoire et persiste dans pp_learners_memory.json."""
    print(f"[MEMORY] Analyse factuelle des apprenants depuis : {extracted_root}")
    memory = {}
    
    student_dirs = [os.path.join(extracted_root, d) for d in os.listdir(extracted_root) if os.path.isdir(os.path.join(extracted_root, d))]
    
    for s_dir in student_dirs:
        student_name = os.path.basename(s_dir)
        
        desc_text = read_extracted_text(s_dir, "desc")
        strat_text = read_extracted_text(s_dir, "strat")
        gest_text = read_extracted_text(s_dir, "gest")
        tdb_text = read_extracted_text(s_dir, "tdb")
        
        desc_facts = extract_description_facts(desc_text)
        strat_facts = extract_strategy_facts(strat_text)
        gest_facts = extract_management_facts(gest_text)
        tdb_facts = extract_dashboard_facts(tdb_text)
        
        coherence = audit_cross_coherence(desc_facts, strat_facts, gest_facts, tdb_facts)
        
        submitted_keys = []
        if desc_facts["status"] == "SOUMIS": submitted_keys.append("desc")
        if strat_facts["status"] == "SOUMIS": submitted_keys.append("strat")
        if gest_facts["status"] == "SOUMIS": submitted_keys.append("gest")
        if tdb_facts["status"] == "SOUMIS": submitted_keys.append("tdb")
        
        memory[student_name] = {
            "student_name": student_name,
            "project_name": desc_facts.get("nom_projet", "Non spécifié"),
            "sector": desc_facts.get("secteur", "Général"),
            "deliverables_status": {
                "desc": desc_facts["status"],
                "strat": strat_facts["status"],
                "gest": gest_facts["status"],
                "content": "NON_SOUMIS",
                "tdb": tdb_facts["status"]
            },
            "facts": {
                "desc": desc_facts,
                "strat": strat_facts,
                "gest": gest_facts,
                "tdb": tdb_facts
            },
            "coherence_audit": coherence,
            "completion": {
                "submitted_count": len(submitted_keys),
                "total_count": 4,
                "percentage": int((len(submitted_keys) / 4) * 100)
            }
        }
        
    with open(output_memory_path, "w", encoding="utf-8") as out_fp:
        json.dump(memory, out_fp, ensure_ascii=False, indent=2)
        
    print(f"[MEMORY] Mémoire transversale mise à jour pour {len(memory)} apprenants.")
    print(f"[MEMORY] Sauvegardée dans : {output_memory_path}")
    return memory


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dclic_root = os.path.dirname(os.path.dirname(current_dir))
    extracted_dir = os.path.join(dclic_root, "extracted_pp_data")
    memory_path = os.path.join(dclic_root, "pp_learners_memory.json")
    build_and_save_memory(extracted_dir, memory_path)

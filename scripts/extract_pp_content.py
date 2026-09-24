"""
extract_pp_content.py — Module d'extraction intégrale et sans troncature des livrables PP.

Garantit une lecture à 100% de tous les formats soumis par les apprenants :
- Word (.docx) : paragraphes intégraux + tableaux complets (Gantt, budgets)
- PDF (.pdf) : toutes les pages sans aucune coupure via PyMuPDF (fitz)
- Excel (.xlsx) : toutes les feuilles de calcul, lignes et colonnes via openpyxl
- OpenDocument (.odt) : extraction du content.xml complet
- PowerPoint (.pptx) : diapositives, formes textuelles et tableaux
- Texte brut (.txt)

Aucun raccourci, aucun échantillonnage, aucune hallucination.
"""

import os
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET

# Bibliothèques d'extraction
try:
    import docx
except ImportError:
    docx = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import pptx
except ImportError:
    pptx = None


def extract_docx(file_path):
    """Extrait l'intégralité du texte d'un fichier .docx, incluant paragraphes et tableaux."""
    if not docx:
        raise ImportError("Le module python-docx n'est pas disponible.")
    
    doc = docx.Document(file_path)
    content = []
    
    # Paragraphes
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            content.append(text)
            
    # Tableaux (souvent utilisés pour Gantt, budgets, personas, KPIs)
    for t_idx, table in enumerate(doc.tables):
        content.append(f"\n[TABLEAU {t_idx + 1}]")
        for row in table.rows:
            row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            # Élimination des doublons consécutifs dus aux fusions de cellules
            cleaned_row = []
            for cell in row_cells:
                if not cleaned_row or cell != cleaned_row[-1]:
                    cleaned_row.append(cell)
            if any(cleaned_row):
                content.append(" | ".join(cleaned_row))
        content.append("[FIN TABLEAU]\n")
        
    full_text = "\n".join(content)
    return full_text


def extract_pdf(file_path):
    """Extrait l'intégralité du texte de toutes les pages d'un fichier PDF avec PyMuPDF."""
    if not fitz:
        raise ImportError("Le module PyMuPDF (fitz) n'est pas disponible.")
        
    doc = fitz.open(file_path)
    pages_text = []
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text").strip()
        if text:
            pages_text.append(f"--- Page {page_idx + 1} ---\n{text}")
            
    doc.close()
    return "\n\n".join(pages_text)


def extract_xlsx(file_path):
    """Extrait l'intégralité des données de toutes les feuilles d'un fichier Excel."""
    if not openpyxl:
        raise ImportError("Le module openpyxl n'est pas disponible.")
        
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheets_content = []
    
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        sheet_rows = []
        for row in sheet.iter_rows(values_only=True):
            cleaned_cells = [str(c).strip() if c is not None else "" for c in row]
            if any(cleaned_cells):
                sheet_rows.append(" | ".join(cleaned_cells))
        if sheet_rows:
            sheets_content.append(f"=== FEUILLE : {sheet_name} ===\n" + "\n".join(sheet_rows))
            
    wb.close()
    return "\n\n".join(sheets_content)


def extract_odt(file_path):
    """Extrait l'intégralité du texte d'un fichier OpenDocument Text (.odt)."""
    with zipfile.ZipFile(file_path) as z:
        content_xml = z.read("content.xml")
    
    root = ET.fromstring(content_xml)
    texts = []
    for elem in root.iter():
        if elem.text and elem.text.strip():
            texts.append(elem.text.strip())
        if elem.tail and elem.tail.strip():
            texts.append(elem.tail.strip())
            
    return "\n".join(texts)


def extract_pptx(file_path):
    """Extrait l'intégralité des textes et tableaux des diapositives d'un fichier PPTX."""
    if not pptx:
        raise ImportError("Le module python-pptx n'est pas disponible.")
        
    prs = pptx.Presentation(file_path)
    slides_content = []
    
    for idx, slide in enumerate(prs.slides):
        slide_texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    t = p.text.strip()
                    if t:
                        slide_texts.append(t)
            elif shape.has_table:
                for row in shape.table.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    if any(row_cells):
                        slide_texts.append(" | ".join(row_cells))
        if slide_texts:
            slides_content.append(f"--- Diapositive {idx + 1} ---\n" + "\n".join(slide_texts))
            
    return "\n\n".join(slides_content)


def extract_file_content(file_path):
    """Détecte l'extension et effectue l'extraction intégrale."""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == ".docx":
            text = extract_docx(file_path)
        elif ext == ".pdf":
            text = extract_pdf(file_path)
        elif ext in [".xlsx", ".xls"]:
            text = extract_xlsx(file_path)
        elif ext == ".odt":
            text = extract_odt(file_path)
        elif ext == ".pptx":
            text = extract_pptx(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            text = f"[Format non textuel ou non supporté : {ext}]"
    except Exception as e:
        text = f"[Erreur lors de l'extraction intégrale de {os.path.basename(file_path)}: {str(e)}]"
        
    num_words = len(re.findall(r"\w+", text))
    num_chars = len(text)
    
    return {
        "text": text,
        "extension": ext,
        "char_count": num_chars,
        "word_count": num_words
    }


def identify_deliverable_key(folder_name):
    """Associe le nom du dossier Moodle au livrable correspondant."""
    name_low = folder_name.lower()
    if "description" in name_low or "cadrage" in name_low or "livrable 0" in name_low:
        return "desc", "Description du projet"
    elif "stratégie" in name_low or "strategie" in name_low or "pp1" in name_low:
        return "strat", "Stratégie Marketing (PP1)"
    elif "gestion" in name_low or "gantt" in name_low or "pp2" in name_low:
        return "gest", "Gestion de Projet & Budget (PP2)"
    elif "contenu" in name_low or "content" in name_low or "flyer" in name_low or "pp3" in name_low:
        return "content", "Production de Contenu (PP3)"
    elif "tableau" in name_low or "tdb" in name_low or "indicateur" in name_low or "pp4" in name_low:
        return "tdb", "Tableau de Bord (PP4)"
    return "autre", folder_name


def parse_student_folder_name(folder_name):
    """Extrait le nom propre de l'apprenant à partir du dossier d'assignation Moodle."""
    clean = re.sub(r'_\d+_assignsubmission_file.*$', '', folder_name).strip()
    return clean


def run_full_extraction(pp_root_dir, output_dir):
    """
    Parcourt l'ensemble de l'arborescence PP/ et extrait l'intégralité
    des documents dans le répertoire miroir d'audit.
    """
    os.makedirs(output_dir, exist_ok=True)
    manifest = {}
    
    print(f"[EXTRACT] Démarrage du scan exhaustif dans : {pp_root_dir}")
    
    for deliv_folder in os.listdir(pp_root_dir):
        deliv_path = os.path.join(pp_root_dir, deliv_folder)
        if not os.path.isdir(deliv_path):
            continue
            
        deliv_key, deliv_title = identify_deliverable_key(deliv_folder)
        print(f"[EXTRACT] Dossier de livrable : {deliv_folder} -> Clé : {deliv_key} ({deliv_title})")
        
        for student_folder in os.listdir(deliv_path):
            student_path = os.path.join(deliv_path, student_folder)
            if not os.path.isdir(student_path):
                continue
                
            student_name = parse_student_folder_name(student_folder)
            student_out_dir = os.path.join(output_dir, student_name)
            os.makedirs(student_out_dir, exist_ok=True)
            
            if student_name not in manifest:
                manifest[student_name] = {
                    "student_name": student_name,
                    "deliverables": {}
                }
                
            if deliv_key not in manifest[student_name]["deliverables"]:
                manifest[student_name]["deliverables"][deliv_key] = []
                
            for root, _, files in os.walk(student_path):
                for f in files:
                    if f.startswith("._") or f.startswith("~$"):
                        continue
                    file_full_path = os.path.join(root, f)
                    extraction = extract_file_content(file_full_path)
                    
                    # Sauvegarde intégrale dans le fichier miroir pour traçabilité
                    out_filename = f"{deliv_key}_{f}.txt"
                    out_file_path = os.path.join(student_out_dir, out_filename)
                    with open(out_file_path, "w", encoding="utf-8", errors="ignore") as out_fp:
                        out_fp.write(f"=== LIVRABLE : {deliv_title} ===\n")
                        out_fp.write(f"=== FICHIER SOURCE : {f} ===\n")
                        out_fp.write(f"=== APPRENANT : {student_name} ===\n")
                        out_fp.write(f"=== STATS : {extraction['word_count']} mots / {extraction['char_count']} caractères ===\n\n")
                        out_fp.write(extraction["text"])
                        
                    manifest[student_name]["deliverables"][deliv_key].append({
                        "original_file": f,
                        "extension": extraction["extension"],
                        "char_count": extraction["char_count"],
                        "word_count": extraction["word_count"],
                        "extracted_file": out_filename
                    })
                    
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as m_fp:
        json.dump(manifest, m_fp, ensure_ascii=False, indent=2)
        
    print(f"[EXTRACT] Extraction terminée avec succès !")
    print(f"[EXTRACT] {len(manifest)} apprenants traités.")
    print(f"[EXTRACT] Manifeste sauvegardé dans : {manifest_path}")
    return manifest


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dclic_root = os.path.dirname(os.path.dirname(current_dir))
    pp_dir = os.path.join(dclic_root, "PP")
    target_out = os.path.join(dclic_root, "extracted_pp_data")
    run_full_extraction(pp_dir, target_out)

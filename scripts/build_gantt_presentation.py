"""
Générateur de la présentation PowerPoint (PPTX) pour la session Visio :
"Maîtriser le Diagramme de Gantt & le Budget de Projet"
Programme D-CLIC (OIF) - Marketing Numérique
Tuteur : Jesse Adirigno OGOULA
Format : 16:9 Widescreen (13.333" x 7.5") - 22 Diapositives
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 1. Charte Graphique D-CLIC
NAVY = RGBColor(26, 58, 92)          # #1A3A5C (Primaire)
ORANGE = RGBColor(232, 145, 45)       # #E8912D (Accent chaleureux)
DARK_SLATE = RGBColor(44, 62, 80)     # #2C3E50 (Texte foncé)
LIGHT_SLATE = RGBColor(90, 106, 122)  # #5A6A7A (Texte secondaire)
BG_LIGHT = RGBColor(245, 247, 250)    # #F5F7FA (Fond cartes)
BG_WHITE = RGBColor(255, 255, 255)    # Blanc pur
BORDER_COLOR = RGBColor(220, 227, 234)# Bordure douce
TEAL = RGBColor(13, 148, 136)         # #0D9488 (Accent vert d'eau)
BLUE_ACCENT = RGBColor(30, 136, 229)  # #1E88E5 (Bleu tech)
RED_ACCENT = RGBColor(217, 83, 79)    # #D9534F (Alerte / Chemin critique)
GOLD = RGBColor(212, 160, 23)         # #D4A017 (Jalons)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(PROJECT_DIR, "Logo.jpg")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "Presentation_Gantt_Budget_DCLIC.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

TOTAL_SLIDES = 22

def add_header(slide, title_text, category_text="D-CLIC • MARKETING NUMÉRIQUE • GESTION DE PROJET (C5 & PP2)"):
    """Ajoute le bandeau d'en-tête supérieur harmonisé."""
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = NAVY
    top_bar.line.fill.background()
    
    orange_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
    orange_line.fill.solid()
    orange_line.fill.fore_color.rgb = ORANGE
    orange_line.line.fill.background()
    
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(9.8), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ORANGE
    p_cat.font.name = "Segoe UI"
    
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(9.8), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = BG_WHITE
    p_title.font.name = "Segoe UI"
    
    if os.path.exists(LOGO_PATH):
        try:
            slide.shapes.add_picture(LOGO_PATH, Inches(11.0), Inches(0.18), width=Inches(1.6))
        except Exception:
            pass

def add_footer(slide, slide_num):
    """Ajoute le pied de page institutionnel."""
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(11.733), Inches(0.32))
    tf = footer_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"Formation D-CLIC (OIF) — Marketing Numérique | Tuteur : Jesse Adirigno OGOULA                       Diapositive {slide_num}/{TOTAL_SLIDES}"
    p.font.size = Pt(9.5)
    p.font.color.rgb = LIGHT_SLATE
    p.font.name = "Segoe UI"

def create_card(slide, left, top, width, height, bg_color=BG_LIGHT, border_color=BORDER_COLOR, border_width=1.5):
    """Crée une carte visuelle conteneur."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

def set_notes(slide, notes_text):
    """Ajoute les notes du présentateur sur la diapositive."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

# ==============================================================================
# SLIDE 1 : COUVERTURE
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = NAVY
bg1.line.fill.background()

bande = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
bande.fill.solid()
bande.fill.fore_color.rgb = ORANGE
bande.line.fill.background()

if os.path.exists(LOGO_PATH):
    s1.shapes.add_picture(LOGO_PATH, Inches(1.2), Inches(0.7), width=Inches(3.2))

badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(2.0), Inches(4.8), Inches(0.42))
badge1.fill.solid()
badge1.fill.fore_color.rgb = ORANGE
badge1.line.fill.background()
tf_b1 = badge1.text_frame
tf_b1.vertical_anchor = MSO_ANCHOR.MIDDLE
p_b1 = tf_b1.paragraphs[0]
p_b1.text = "🎯 FORMATION D-CLIC (OIF) • SÉQUENCE 3 & PP2"
p_b1.alignment = PP_ALIGN.CENTER
p_b1.font.size = Pt(11)
p_b1.font.bold = True
p_b1.font.color.rgb = BG_WHITE
p_b1.font.name = "Segoe UI"

t_box1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.6), Inches(11.0), Inches(2.2))
tf1 = t_box1.text_frame
tf1.word_wrap = True
p1_1 = tf1.paragraphs[0]
p1_1.text = "Maîtriser le Diagramme de Gantt\n& le Budget de Projet"
p1_1.font.size = Pt(36)
p1_1.font.bold = True
p1_1.font.color.rgb = BG_WHITE
p1_1.font.name = "Segoe UI"

p1_2 = tf1.add_paragraph()
p1_2.text = "De la stratégie marketing au pilotage opérationnel : Structurer son temps, ses ressources et son budget"
p1_2.font.size = Pt(18)
p1_2.font.color.rgb = RGBColor(205, 225, 250)
p1_2.font.name = "Segoe UI"
p1_2.space_before = Pt(10)

c_info1 = create_card(s1, Inches(1.2), Inches(5.1), Inches(11.0), Inches(1.6), bg_color=RGBColor(36, 75, 115), border_color=ORANGE)
tf_c1 = c_info1.text_frame
tf_c1.margin_left = Inches(0.4)
tf_c1.margin_top = Inches(0.25)
p_c1a = tf_c1.paragraphs[0]
p_c1a.text = "👨‍🏫 Tuteur Référent : Jesse Adirigno OGOULA"
p_c1a.font.size = Pt(15)
p_c1a.font.bold = True
p_c1a.font.color.rgb = BG_WHITE
p_c1a.font.name = "Segoe UI"

p_c1b = tf_c1.add_paragraph()
p_c1b.text = "📅 Visioconférence Thématique Interactive | Durée : 1h30 | Objectif : Réussir le Livrable PP2 (/6 pts)"
p_c1b.font.size = Pt(13)
p_c1b.font.color.rgb = RGBColor(220, 235, 255)
p_c1b.font.name = "Segoe UI"
p_c1b.space_before = Pt(6)

set_notes(s1, "SLIDE 1 - ACCUEIL (00:00 - 05:00)\nAccueillir chaleureusement les apprenants dès leur connexion. Vérifier que tout le monde entend bien. Annoncer le thème de la soirée : maîtriser le Gantt et le budget, pour transformer le Projet Professionnel en réussite concrète.")

# ==============================================================================
# SLIDE 2 : POURQUOI CETTE SESSION ?
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Pourquoi cette session est le tournant de votre formation ?")
add_footer(s2, 2)

c2_1 = create_card(s2, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.2), bg_color=BG_WHITE)
tf2_1 = c2_1.text_frame
tf2_1.margin_left = tf2_1.margin_right = Inches(0.25)
tf2_1.margin_top = Inches(0.3)
p = tf2_1.paragraphs[0]
p.text = "🌉 Le Pont Indispensable"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf2_1.add_paragraph()
p.text = "• Une idée sans calendrier reste un souhait.\n• Vous avez conçu une belle stratégie marketing en PP1 (Personas, USP, Canaux).\n• Le Gantt et le Budget sont le moteur qui transforme cette vision en réalité terrain."
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(12)

c2_2 = create_card(s2, Inches(4.866), Inches(1.5), Inches(3.6), Inches(5.2), bg_color=BG_WHITE, border_color=ORANGE)
tf2_2 = c2_2.text_frame
tf2_2.margin_left = tf2_2.margin_right = Inches(0.25)
tf2_2.margin_top = Inches(0.3)
p = tf2_2.paragraphs[0]
p.text = "🎯 L'Enjeu du Livrable PP2"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf2_2.add_paragraph()
p.text = "• Le Livrable 2 compte pour 6 points sur 20 dans votre note finale D-CLIC (30% du projet !).\n• Consigne officielle : remettre un planning Gantt et un budget par tâches réaliste.\n• Les tuteurs attendent de la rigueur opérationnelle, pas de l'improvisation."
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(12)

c2_3 = create_card(s2, Inches(8.933), Inches(1.5), Inches(3.6), Inches(5.2), bg_color=BG_WHITE)
tf2_3 = c2_3.text_frame
tf2_3.margin_left = tf2_3.margin_right = Inches(0.25)
tf2_3.margin_top = Inches(0.3)
p = tf2_3.paragraphs[0]
p.text = "💼 La Compétence Métier"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL
p = tf2_3.add_paragraph()
p.text = "• En entreprise ou en freelance, un client ou une direction demande toujours 2 choses :\n  1. « Quand est-ce que c'est prêt ? »\n  2. « Combien ça va coûter ? »\n• Ce soir, vous apprenez à répondre à ces deux questions avec précision chirurgicale."
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(12)

set_notes(s2, "SLIDE 2 - CONTEXTE & ENJEUX (05:00 - 10:00)\nExpliquer pourquoi la gestion de projet est ce qui distingue l'amateur du professionnel. Faire le lien explicite avec le Livrable 1 qu'ils viennent de terminer et le Livrable 2 qui arrive. Rassurer le groupe : tout le monde va y arriver avec la méthode pas-à-pas.")

# ==============================================================================
# SLIDE 3 : SOMMAIRE / LE PARCOURS DE LA SOIRÉE
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Le Parcours de la Soirée : 5 Escales Méthodologiques")
add_footer(s3, 3)

modules = [
    ("Escale 1", "Démystifier le Diagramme de Gantt", "Origine, utilité, 5 composantes clés et vocabulaire fondamental (jalons, dépendances, chemin critique).", NAVY),
    ("Escale 2", "La Méthode pas-à-pas (WBS)", "Comment structurer sa pensée de la feuille blanche au découpage en 4 phases d'une campagne.", TEAL),
    ("Escale 3", "L'Ordonnancement & les RH", "Lier les antériorités, estimer les durées réelles, intégrer des marges et affecter les bons profils RH.", BLUE_ACCENT),
    ("Escale 4", "Le Budget par Tâche & Trésorerie", "Associer chaque tâche à un coût précis (RH, média, outils) et anticiper les décaissements (cash-flow).", ORANGE),
    ("Escale 5", "Cas Pratique, Grille PP2 & Atelier", "Démonstration d'un cas complet chiffré, décryptage de la grille /6 pts et conseils pour le rendu.", RED_ACCENT)
]

for idx, (step, title_m, desc, col) in enumerate(modules):
    y_pos = Inches(1.5 + idx * 1.05)
    c = create_card(s3, Inches(0.8), y_pos, Inches(11.733), Inches(0.92), bg_color=BG_WHITE)
    
    badge = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), y_pos + Inches(0.16), Inches(1.8), Inches(0.6))
    badge.fill.solid()
    badge.fill.fore_color.rgb = col
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = step
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s3.shapes.add_textbox(Inches(3.0), y_pos + Inches(0.1), Inches(9.3), Inches(0.72))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = 0
    p1 = tf_t.paragraphs[0]
    p1.text = title_m
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = NAVY
    
    p2 = tf_t.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(12)
    p2.font.color.rgb = LIGHT_SLATE

set_notes(s3, "SLIDE 3 - SOMMAIRE (10:00 - 12:00)\nPrésenter le menu de la séance. Annoncer le rythme : interactif avec des questions dans le chat et un cas pratique concret chiffré à la fin.")

# ==============================================================================
# SLIDE 4 : ICEBREAKER & DIAGNOSTIC INTERACTIF
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "Sondage en direct : Quel gestionnaire de projet êtes-vous ?")
add_footer(s4, 4)

c4_q = create_card(s4, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.3), bg_color=NAVY, border_color=ORANGE)
tf4_q = c4_q.text_frame
tf4_q.margin_left = Inches(0.4)
tf4_q.margin_top = Inches(0.2)
p = tf4_q.paragraphs[0]
p.text = "💬 Question dans le Chat (écrivez A, B ou C) :"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf4_q.add_paragraph()
p.text = "« Quand vous devez organiser un projet ou un événement, quelle est votre première réaction ? »"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = BG_WHITE
p.space_before = Pt(4)

options = [
    ("A", "L'Artiste Spontané", "« J'ai tout dans la tête ! Je fonce, j'improvise au fur et à mesure et je gère les urgences le jour J. »", RED_ACCENT),
    ("B", "L'Adepte de la To-Do List", "« J'écris une longue liste de choses à faire dans mon carnet ou mon téléphone, et je coche quand c'est fait. »", BLUE_ACCENT),
    ("C", "Le Stratège Visionnaire", "« Je découpe le projet, j'estime le temps, je vérifie qui fait quoi et je calcule les coûts à l'avance. »", TEAL)
]

for idx, (letter, title_opt, desc_opt, col) in enumerate(options):
    x_pos = Inches(0.8 + idx * 4.066)
    c = create_card(s4, x_pos, Inches(3.0), Inches(3.6), Inches(3.7), bg_color=BG_WHITE)
    
    badge = s4.shapes.add_shape(MSO_SHAPE.OVAL, x_pos + Inches(1.4), Inches(3.2), Inches(0.8), Inches(0.8))
    badge.fill.solid()
    badge.fill.fore_color.rgb = col
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = letter
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(20)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s4.shapes.add_textbox(x_pos + Inches(0.25), Inches(4.2), Inches(3.1), Inches(2.3))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = 0
    p1 = tf_t.paragraphs[0]
    p1.text = title_opt
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = NAVY
    
    p2 = tf_t.add_paragraph()
    p2.text = desc_opt
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(12.5)
    p2.font.color.rgb = DARK_SLATE
    p2.space_before = Pt(8)

set_notes(s4, "SLIDE 4 - ICEBREAKER (12:00 - 18:00)\nDonner 30 secondes aux apprenants pour taper A, B ou C dans le chat. Lire les réponses à voix haute avec humour et bienveillance. Expliquer que la majorité des gens commencent en A ou B, mais que le monde professionnel exige de basculer vers C : le Gantt.")

# ==============================================================================
# SLIDE 5 : QU'EST-CE QU'UN DIAGRAMME DE GANTT ?
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Escale 1 : Qu'est-ce qu'un Diagramme de Gantt ?")
add_footer(s5, 5)

c5_def = create_card(s5, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.2), bg_color=BG_WHITE)
tf5 = c5_def.text_frame
tf5.margin_left = tf5.margin_right = Inches(0.35)
tf5.margin_top = Inches(0.3)
p = tf5.paragraphs[0]
p.text = "📌 Définition & Rôle Central"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf5.add_paragraph()
p.text = "Un diagramme de Gantt est une représentation graphique du calendrier d'un projet. Il modélise sur un repère à double entrée :\n\n" \
         "1. En vertical (axe Y) : L'ensemble des tâches et activités nécessaires.\n" \
         "2. En horizontal (axe X) : L'échelle du temps (jours, semaines, mois).\n\n" \
         "Chaque tâche est matérialisée par une barre horizontale dont la position indique le début et la fin, et la longueur représente sa durée calendaire."
p.font.size = Pt(13.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(8)

p = tf5.add_paragraph()
p.text = "💡 Pourquoi a-t-il traversé plus d'un siècle ?"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ORANGE
p.space_before = Pt(14)
p = tf5.add_paragraph()
p.text = "Inventé par Henry Gantt vers 1910, cet outil s'est imposé car il répond au besoin biologique du cerveau humain : visualiser le temps dans l'espace pour coordonner des équipes sans stress."
p.font.size = Pt(13)
p.font.color.rgb = LIGHT_SLATE
p.space_before = Pt(6)

c5_r = create_card(s5, Inches(8.5), Inches(1.5), Inches(4.033), Inches(5.2), bg_color=NAVY)
tf5_r = c5_r.text_frame
tf5_r.margin_left = tf5_r.margin_right = Inches(0.3)
tf5_r.margin_top = Inches(0.3)
p = tf5_r.paragraphs[0]
p.text = "👁️ Les 3 Questions auxquelles le Gantt répond en 1 seconde :"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf5_r.add_paragraph()
p.text = "1. Qui fait quoi et quand ?\n" \
         "→ Visibilité immédiate sur les rôles et les échéances.\n\n" \
         "2. Qu'est-ce qui bloque quoi ?\n" \
         "→ Identification des goulots d'étranglement et des enchaînements obligatoires.\n\n" \
         "3. Où en sommes-nous aujourd'hui ?\n" \
         "→ Comparaison instantanée entre le prévisionnel et l'avancement réel."
p.font.size = Pt(13.5)
p.font.color.rgb = BG_WHITE
p.space_before = Pt(12)

set_notes(s5, "SLIDE 5 - DÉFINITION GANTT (18:00 - 23:00)\nDéfinir le Gantt avec clarté. Souligner la différence avec une simple To-Do List : une to-do list dit ce qu'il faut faire, mais elle ignore complètement le temps, les dépendances et la charge.")

# ==============================================================================
# SLIDE 6 : VOCABULAIRE ESSENTIEL (1/2) : TÂCHE, CHARGE VS DURÉE, JALON
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Le Vocabulaire Fondamental du Chef de Projet (1/2)")
add_footer(s6, 6)

terms_1 = [
    ("1. La Tâche (Task)", "L'unité élémentaire de travail. C'est une action concrète, assignable à un responsable unique, avec un début, une fin et un livrable vérifiable.", "« Rédiger les accroches du flyer »\n« Paramétrer la campagne Facebook Ads »", BLUE_ACCENT),
    ("2. Charge vs Durée", "ATTENTION : Le piège classique !\n• Charge : Temps de travail effectif requis (ex : 4 heures).\n• Durée : Délai calendaire écoulé entre le début et la fin (ex : 2 jours car on attend la validation).", "Charge graphiste = 3 heures.\nDurée dans le Gantt = 3 jours (création + aller-retour validation client).", ORANGE),
    ("3. Le Jalon (Milestone)", "Un événement clé, une étape charnière qui marque l'achèvement d'une phase ou une validation majeure.\nSa durée dans le Gantt est égale à ZÉRO (symbole losange ◆).", "« Validation officielle du brief »\n« Lancement public de la campagne »\n« Dépôt du Livrable PP2 »", GOLD)
]

for idx, (term, def_text, ex_text, col) in enumerate(terms_1):
    x_pos = Inches(0.8 + idx * 4.066)
    c = create_card(s6, x_pos, Inches(1.5), Inches(3.8), Inches(5.2), bg_color=BG_WHITE, border_color=col)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    
    p = tf.paragraphs[0]
    p.text = term
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = col
    
    p = tf.add_paragraph()
    p.text = def_text
    p.font.size = Pt(12.5)
    p.font.color.rgb = DARK_SLATE
    p.space_before = Pt(8)
    
    c_ex = create_card(s6, x_pos + Inches(0.15), Inches(4.7), Inches(3.5), Inches(1.8), bg_color=BG_LIGHT, border_color=BORDER_COLOR)
    tf_ex = c_ex.text_frame
    tf_ex.margin_left = tf_ex.margin_right = Inches(0.2)
    tf_ex.margin_top = Inches(0.15)
    p_ex_t = tf_ex.paragraphs[0]
    p_ex_t.text = "Exemple concret :"
    p_ex_t.font.size = Pt(11)
    p_ex_t.font.bold = True
    p_ex_t.font.color.rgb = NAVY
    p_ex = tf_ex.add_paragraph()
    p_ex.text = ex_text
    p_ex.font.size = Pt(11)
    p_ex.font.color.rgb = LIGHT_SLATE
    p_ex.space_before = Pt(4)

set_notes(s6, "SLIDE 6 - VOCABULAIRE 1 (23:00 - 28:00)\nInsister particulièrement sur la distinction Charge vs Durée. 80% des apprenants font l'erreur d'inscrire 2 heures sur le Gantt alors qu'il faut 3 jours calendaires pour que la tâche soit bouclée avec les validations. Expliquer le rôle du Jalon : durée 0, losange.")

# ==============================================================================
# SLIDE 7 : VOCABULAIRE ESSENTIEL (2/2) : DÉPENDANCES, CHEMIN CRITIQUE, MARGES
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Le Vocabulaire Fondamental du Chef de Projet (2/2)")
add_footer(s7, 7)

terms_2 = [
    ("4. Dépendances / Antériorités", "Les liaisons logiques qui dictent l'ordre des tâches.\n• Fin-à-Début (FD - le plus courant) : La tâche B ne peut commencer que si la tâche A est terminée.\n• Début-à-Début (DD) : Deux tâches démarrent ensemble.", "On ne peut pas diffuser la vidéo sponsorisée (B) si le montage vidéo n'est pas validé (A). Liaison FD obligatoire.", TEAL),
    ("5. Le Chemin Critique", "La séquence ininterrompue des tâches qui détermine la durée totale incompressible du projet.\nToute tâche sur le chemin critique a une marge nulle : 1 jour de retard sur elle = 1 jour de retard sur le projet entier !", "Brief → Tournage → Montage → Diffusion. Si le tournage prend 2 jours de retard, toute la campagne est décalée.", RED_ACCENT),
    ("6. Les Marges de Sécurité", "Le temps dont une tâche peut être retardée sans impacter la date finale du projet (marge totale) ou la tâche suivante (marge libre).\nC'est votre coussin de sécurité anti-stress face aux imprévus.", "La rédaction des articles de blog a 4 jours de marge car la newsletter part plus tard. On peut absorber un contretemps.", BLUE_ACCENT)
]

for idx, (term, def_text, ex_text, col) in enumerate(terms_2):
    x_pos = Inches(0.8 + idx * 4.066)
    c = create_card(s7, x_pos, Inches(1.5), Inches(3.8), Inches(5.2), bg_color=BG_WHITE, border_color=col)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    
    p = tf.paragraphs[0]
    p.text = term
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = col
    
    p = tf.add_paragraph()
    p.text = def_text
    p.font.size = Pt(12.5)
    p.font.color.rgb = DARK_SLATE
    p.space_before = Pt(8)
    
    c_ex = create_card(s7, x_pos + Inches(0.15), Inches(4.7), Inches(3.5), Inches(1.8), bg_color=BG_LIGHT, border_color=BORDER_COLOR)
    tf_ex = c_ex.text_frame
    tf_ex.margin_left = tf_ex.margin_right = Inches(0.2)
    tf_ex.margin_top = Inches(0.15)
    p_ex_t = tf_ex.paragraphs[0]
    p_ex_t.text = "Exemple concret :"
    p_ex_t.font.size = Pt(11)
    p_ex_t.font.bold = True
    p_ex_t.font.color.rgb = NAVY
    p_ex = tf_ex.add_paragraph()
    p_ex.text = ex_text
    p_ex.font.size = Pt(11)
    p_ex.font.color.rgb = LIGHT_SLATE
    p_ex.space_before = Pt(4)

set_notes(s7, "SLIDE 7 - VOCABULAIRE 2 (28:00 - 33:00)\nExpliquer l'image du domino pour les dépendances. Pour le chemin critique, faire l'analogie de la maison : si la fondation a du retard, le toit aura du retard. Mais si peindre la clôture a du retard, on peut quand même emménager.")

# ==============================================================================
# SLIDE 8 : STRUCTURER SA PENSÉE : LA MÉTHODE WBS
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Escale 2 : Structurer sa pensée — La Règle d'Or")
add_footer(s8, 8)

c8_warn = create_card(s8, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.1), bg_color=RGBColor(254, 243, 199), border_color=ORANGE)
tf8_w = c8_warn.text_frame
tf8_w.margin_left = Inches(0.35)
tf8_w.margin_top = Inches(0.15)
p = tf8_w.paragraphs[0]
p.text = "⚠️ LA RÈGLE D'OR ABSOLUE DU GESTIONNAIRE DE PROJET :"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf8_w.add_paragraph()
p.text = "« On ne commence JAMAIS par dessiner des barres sur un calendrier ! On commence par décomposer son projet. »"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY
p.space_before = Pt(2)

c8_l = create_card(s8, Inches(0.8), Inches(2.8), Inches(5.6), Inches(3.9), bg_color=BG_WHITE)
tf8_l = c8_l.text_frame
tf8_l.margin_left = tf8_l.margin_right = Inches(0.3)
tf8_l.margin_top = Inches(0.25)
p = tf8_l.paragraphs[0]
p.text = "🧱 La Méthode WBS (Work Breakdown Structure)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf8_l.add_paragraph()
p.text = "En français : Organigramme des Tâches (OT) ou Structure de Décomposition du Projet (SDP).\n\n" \
         "Principe : On découpe un gros livrable intimidant en sous-ensembles gérables, comme on découpe une pizza en parts pour pouvoir la manger.\n\n" \
         "La hiérarchie universelle :\n" \
         "• Niveau 1 : Le Projet Global\n" \
         "• Niveau 2 : Les Grandes Phases chronologiques\n" \
         "• Niveau 3 : Les Lots de travail (Livrables)\n" \
         "• Niveau 4 : Les Tâches opérationnelles"
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(6)

c8_r = create_card(s8, Inches(6.933), Inches(2.8), Inches(5.6), Inches(3.9), bg_color=BG_WHITE, border_color=TEAL)
tf8_r = c8_r.text_frame
tf8_r.margin_left = tf8_r.margin_right = Inches(0.3)
tf8_r.margin_top = Inches(0.25)
p = tf8_r.paragraphs[0]
p.text = "🎯 Pourquoi cette étape vous sauve la vie ?"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL
p = tf8_r.add_paragraph()
p.text = "1. Zéro Oubli : En suivant les phases, vous ne risquez pas d'oublier la relecture, le paramétrage technique ou le bilan.\n\n" \
         "2. Clarté Mentale : Vous évitez la sensation d'être submergé par l'ampleur de la campagne.\n\n" \
         "3. Estimation Facile : Il est 10 fois plus facile d'estimer le temps et le coût d'une tâche précise de 2 jours que d'une campagne entière de 2 mois.\n\n" \
         "4. Cohérence PP1 → PP2 : Chaque action d'acquisition ou de rétention définie dans votre Livrable 1 devient un lot de travail WBS !"
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(6)

set_notes(s8, "SLIDE 8 - STRUCTURER SA PENSÉE (33:00 - 38:00)\nInsister sur le piège des apprenants qui ouvrent Canva ou Excel et commencent à tracer des barres au hasard. Leur faire répéter : 'D'abord le WBS, ensuite le Gantt'. Faire le lien avec les actions d'acquisition/rétention du PP1.")

# ==============================================================================
# SLIDE 9 : LES 4 PHASES CLÉS D'UNE CAMPAGNE MARKETING
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Les 4 Phases Incontournables d'une Campagne Marketing")
add_footer(s9, 9)

phases = [
    ("PHASE 1", "Cadrage & Préparation", [
        "Validation du brief & des objectifs SMART",
        "Rétroplanning & budget prévisionnel",
        "Benchmark concurrentiel rapide",
        "Jalon : Validation formelle de cadrage ◆"
    ], NAVY),
    ("PHASE 2", "Création & Production", [
        "Rédaction des textes (copywriting, posts)",
        "Création graphique (visuels, flyers Canva)",
        "Tournage & montage vidéo (CapCut, etc.)",
        "Jalon : Livrables créatifs validés ◆"
    ], BLUE_ACCENT),
    ("PHASE 3", "Déploiement & Diffusion", [
        "Configuration des régies (Meta / TikTok)",
        "Publications organiques & relations influenceurs",
        "Lancement officiel et monitoring direct",
        "Jalon : Campagne lancée publiquement ◆"
    ], TEAL),
    ("PHASE 4", "Analyse & Optimisation", [
        "Suivi quotidien des métriques clés (KPIs)",
        "Ajustement des enchères et des visuels",
        "Rapport de clôture & bilan financier (ROI)",
        "Jalon : Bilan de campagne remis ◆"
    ], ORANGE)
]

for idx, (p_tag, p_title, tasks, col) in enumerate(phases):
    x_pos = Inches(0.8 + idx * 3.033)
    c = create_card(s9, x_pos, Inches(1.5), Inches(2.85), Inches(5.2), bg_color=BG_WHITE, border_color=col)
    
    badge = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.2), Inches(1.7), Inches(2.45), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = col
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = p_tag
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s9.shapes.add_textbox(x_pos + Inches(0.2), Inches(2.25), Inches(2.45), Inches(4.3))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = p_title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    for t in tasks:
        p_t = tf.add_paragraph()
        p_t.text = "• " + t if not t.startswith("Jalon") else "◆ " + t
        p_t.font.size = Pt(11.5)
        p_t.font.color.rgb = DARK_SLATE if not t.startswith("Jalon") else col
        p_t.font.bold = t.startswith("Jalon")
        p_t.space_before = Pt(8)

set_notes(s9, "SLIDE 9 - LES 4 PHASES (38:00 - 43:00)\nPrésenter cette structure universelle. Quel que soit leur projet pour le PP2 (boutique e-commerce, média Francotechno, application mobile, agence locale), leur Gantt doit comporter ces 4 grandes phases chronologiques.")

# ==============================================================================
# SLIDE 10 : ÉTAPE 1 : LISTER ET CALIBRER SES TÂCHES
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Étape 1 : Lister et calibrer ses tâches (La Granularité)")
add_footer(s10, 10)

c10_rule = create_card(s10, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), bg_color=BG_WHITE)
tf10_r = c10_rule.text_frame
tf10_r.margin_left = tf10_r.margin_right = Inches(0.3)
tf10_r.margin_top = Inches(0.3)
p = tf10_r.paragraphs[0]
p.text = "⚖️ Le Dilemme du Calibrage"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf10_r.add_paragraph()
p.text = "La granularité désigne le niveau de détail de votre planning. Deux pièges opposés vous guettent :"
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(6)

p = tf10_r.add_paragraph()
p.text = "❌ Piège 1 : Le Planning Macro (Trop vague)\n" \
         "Mettre une seule tâche : « Faire le marketing » (durée 2 mois). C'est inutile, invérifiable et impossible à piloter."
p.font.size = Pt(12)
p.font.color.rgb = RED_ACCENT
p.space_before = Pt(10)

p = tf10_r.add_paragraph()
p.text = "❌ Piège 2 : Le Planning Micro (Usine à gaz)\n" \
         "Mettre des micro-actions de 15 minutes : « Ouvrir Google Docs », « Envoyer un email de test ». Vous passerez plus de temps à mettre à jour votre planning qu'à travailler !"
p.font.size = Pt(12)
p.font.color.rgb = RED_ACCENT
p.space_before = Pt(10)

p = tf10_r.add_paragraph()
p.text = "✅ La Bonne Mesure D-CLIC :\n" \
         "Des tâches de 1 à 5 jours ouvrés. Entre 15 et 25 tâches au total pour une campagne complète."
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = TEAL
p.space_before = Pt(10)

c10_fmt = create_card(s10, Inches(6.933), Inches(1.5), Inches(5.6), Inches(5.2), bg_color=BG_WHITE, border_color=BLUE_ACCENT)
tf10_f = c10_fmt.text_frame
tf10_f.margin_left = tf10_f.margin_right = Inches(0.3)
tf10_f.margin_top = Inches(0.3)
p = tf10_f.paragraphs[0]
p.text = "✍️ La Formule Magique d'une Bonne Tâche"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = BLUE_ACCENT
p = tf10_f.add_paragraph()
p.text = "Une tâche bien formulée contient TOUJOURS 3 ingrédients :"
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(6)

rules_fmt = [
    ("1. Un verbe d'action à l'infinitif", "Rédiger, Concevoir, Tourner, Paramétrer, Valider (pas de noms vagues comme « Vidéo » ou « Réunion »)."),
    ("2. Un livrable explicite", "Ce qui existe physiquement ou numériquement quand c'est fini (ex : « 1 flyer au format A5 validé »)."),
    ("3. Une condition d'achèvement binaire", "On doit pouvoir répondre par OUI ou par NON sans ambiguïté : « Est-ce terminé ? ».")
]

for title_rf, desc_rf in rules_fmt:
    p = tf10_f.add_paragraph()
    p.text = f"• {title_rf} :"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_before = Pt(10)
    p_d = tf10_f.add_paragraph()
    p_d.text = f"   {desc_rf}"
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = DARK_SLATE

set_notes(s10, "SLIDE 10 - CALIBRER LES TÂCHES (43:00 - 48:00)\nDonner l'astuce de la formule : [Verbe d'action] + [Objet précis] + [Critère d'achèvement]. Expliquer que les tuteurs vérifient que les tâches ne sont ni trop floues ni microscopiques.")

# ==============================================================================
# SLIDE 11 : ÉTAPE 2 : ORDONNANCER ET CRÉER LES DÉPENDANCES
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Étape 2 : Ordonnancer et créer les dépendances")
add_footer(s11, 11)

c11_top = create_card(s11, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.4), bg_color=BG_WHITE)
tf11_t = c11_top.text_frame
tf11_t.margin_left = tf11_t.margin_right = Inches(0.3)
tf11_t.margin_top = Inches(0.2)
p = tf11_t.paragraphs[0]
p.text = "🔗 La Matrice des Antécédents : Deux questions à poser systématiquement"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf11_t.add_paragraph()
p.text = "Pour chaque tâche identifiée dans votre WBS, vous devez vous poser deux questions indispensables :\n" \
         "1. « Quelle(s) tâche(s) dois-je OBLIGATOIREMENT terminer avant de pouvoir commencer celle-ci ? » (Antécédent direct)\n" \
         "2. « Quelles tâches peuvent se dérouler EN MÊME TEMPS sans se bloquer ? » (Tâches parallèles)"
p.font.size = Pt(13)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(6)

# Tableau d'ordonnancement
c11_tab = create_card(s11, Inches(0.8), Inches(3.1), Inches(11.733), Inches(3.6), bg_color=BG_WHITE, border_color=TEAL)
shape_t = s11.shapes.add_table(5, 4, Inches(1.0), Inches(3.3), Inches(11.333), Inches(3.2))
tbl = shape_t.table
tbl.columns[0].width = Inches(1.5)
tbl.columns[1].width = Inches(4.5)
tbl.columns[2].width = Inches(2.2)
tbl.columns[3].width = Inches(3.133)

headers = ["Code", "Intitulé de la Tâche", "Antécédent(s)", "Type d'Enchaînement"]
for i, h in enumerate(headers):
    cell = tbl.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    tf = cell.text_frame
    p = tf.paragraphs[0]
    p.text = h
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BG_WHITE

data_rows = [
    ("T1", "Rédaction du script vidéo et brief visuel", "— (Démarrage)", "Tâche initiale"),
    ("T2", "Tournage de la vidéo promotionnelle", "T1", "Fin-à-Début (FD)"),
    ("T3", "Création graphique du flyer promotionnel", "T1", "Parallèle avec T2 (même antécédent T1)"),
    ("T4", "Paramétrage et lancement Meta Ads", "T2, T3 (validés)", "Fin-à-Début (Attend la fin de T2 ET T3)")
]

for row_idx, row in enumerate(data_rows, start=1):
    for col_idx, text in enumerate(row):
        cell = tbl.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_LIGHT if row_idx % 2 == 1 else BG_WHITE
        tf = cell.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(11.5)
        p.font.color.rgb = DARK_SLATE
        if col_idx == 0:
            p.font.bold = True
            p.font.color.rgb = TEAL

set_notes(s11, "SLIDE 11 - ORDONNANCEMENT (48:00 - 53:00)\nMontrer comment le tableau des antécédents prépare directement le Gantt. Souligner le gain de temps obtenu grâce aux tâches en parallèle (ex : le flyer et le tournage peuvent se faire en parallèle après validation des scripts).")

# ==============================================================================
# SLIDE 12 : ÉTAPE 3 : ESTIMER LES DURÉES & LES MARGES
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Étape 3 : Estimer les durées réalistes & les marges")
add_footer(s12, 12)

c12_1 = create_card(s12, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.2), bg_color=BG_WHITE)
tf12_1 = c12_1.text_frame
tf12_1.margin_left = tf12_1.margin_right = Inches(0.25)
tf12_1.margin_top = Inches(0.3)
p = tf12_1.paragraphs[0]
p.text = "🧠 Le Biais d'Optimisme"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = RED_ACCENT
p = tf12_1.add_paragraph()
p.text = "• « Ça me prendra 2 heures ! »\n• En réalité, on oublie :\n  - Le temps de recherche d'idées.\n  - Les bugs techniques (logiciel qui plante, coupure Internet).\n  - Les interruptions quotidiennes.\n• Règle d'or : Multipliez toujours votre première estimation par 1,5."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(10)

c12_2 = create_card(s12, Inches(4.866), Inches(1.5), Inches(3.6), Inches(5.2), bg_color=BG_WHITE, border_color=ORANGE)
tf12_2 = c12_2.text_frame
tf12_2.margin_left = tf12_2.margin_right = Inches(0.25)
tf12_2.margin_top = Inches(0.3)
p = tf12_2.paragraphs[0]
p.text = "⏳ La Loi de Parkinson"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf12_2.add_paragraph()
p.text = "• « Tout travail s'étale de façon à occuper tout le temps disponible pour son achèvement. »\n• Si vous donnez 3 semaines à un graphiste pour faire un flyer, il le fera les 2 derniers jours !\n• Solution : Fixer des échéances courtes et des jalons intermédiaires réguliers."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(10)

c12_3 = create_card(s12, Inches(8.933), Inches(1.5), Inches(3.6), Inches(5.2), bg_color=BG_WHITE)
tf12_3 = c12_3.text_frame
tf12_3.margin_left = tf12_3.margin_right = Inches(0.25)
tf12_3.margin_top = Inches(0.3)
p = tf12_3.paragraphs[0]
p.text = "🛡️ Intégrer les Validations"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = TEAL
p = tf12_3.add_paragraph()
p.text = "• L'oubli fatal en marketing digital : croire que dès qu'un visuel est fini, il est publié le soir même.\n• Il faut prévoir le délai de validation du client / tuteur (24 à 48h).\n• Il faut prévoir le délai de validation des publicités par Meta ou TikTok (24h)."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(10)

set_notes(s12, "SLIDE 12 - ESTIMATION DURÉES (53:00 - 58:00)\nPartager ces lois psychologiques de la gestion de projet. Insister sur le délai d'approbation publicitaire de Meta ou Google : une pub rejetée peut bloquer tout le planning si aucune marge n'a été prévue.")

# ==============================================================================
# SLIDE 13 : ÉTAPE 4 : AFFECTER LES RESSOURCES HUMAINES (RH)
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Étape 4 : Affecter les Ressources Humaines (RH)")
add_footer(s13, 13)

c13_l = create_card(s13, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.2), bg_color=BG_WHITE)
tf13_l = c13_l.text_frame
tf13_l.margin_left = tf13_l.margin_right = Inches(0.3)
tf13_l.margin_top = Inches(0.3)
p = tf13_l.paragraphs[0]
p.text = "👥 Les Profils Métiers Clés en Marketing Digital"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf13_l.add_paragraph()
p.text = "Votre Livrable PP2 exige d'identifier les RH associées à chaque tâche. Ne mettez pas « Quelqu'un », utilisez les vrais métiers étudiés en Séquence 1 & 2 :"
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(6)

roles = [
    ("Chef de Projet Digital", "Coordination globale, respect des délais, gestion du budget et interface client."),
    ("Concepteur-Rédacteur / Copywriter", "Rédaction des messages, scripts vidéos, argumentaires de vente, posts sociaux."),
    ("Graphiste / Designer Visuel", "Identité graphique, création des flyers, bannières, formats carrousel."),
    ("Vidéaste / Monteur Vidéo", "Captation, cadrage, montage dynamique des vidéos courtes (Reels/TikTok)."),
    ("Traffic Manager / Media Buyer", "Paramétrage régies publicitaires (Meta Ads, Google Ads), ciblage, tracking.")
]

for r_name, r_desc in roles:
    p = tf13_l.add_paragraph()
    p.text = f"• {r_name} :"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEAL
    p.space_before = Pt(6)
    p_d = tf13_l.add_paragraph()
    p_d.text = f"   {r_desc}"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = DARK_SLATE

c13_r = create_card(s13, Inches(7.133), Inches(1.5), Inches(5.4), Inches(5.2), bg_color=BG_WHITE, border_color=BLUE_ACCENT)
tf13_r = c13_r.text_frame
tf13_r.margin_left = tf13_r.margin_right = Inches(0.3)
tf13_r.margin_top = Inches(0.3)
p = tf13_r.paragraphs[0]
p.text = "🏷️ La Logique RACI Simplifiée"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = BLUE_ACCENT
p = tf13_r.add_paragraph()
p.text = "Pour éviter le flou (« quand tout le monde est responsable, personne n'est responsable ») :\n\n" \
         "• R (Réalisateur) : La personne qui produit concrètement la tâche (ex : le graphiste crée le flyer).\n\n" \
         "• A (Approbateur / Valideur) : Le responsable qui donne le feu vert final (ex : le Chef de Projet ou le Directeur Marketing).\n\n" \
         "• C (Consulté) : L'expert qu'on sollicite pour avis technique.\n\n" \
         "• I (Informé) : Les personnes tenues au courant de l'avancement."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(8)

p = tf13_r.add_paragraph()
p.text = "⚠️ Règle d'or D-CLIC : Une tâche = UN SEUL Réalisateur principal clairement nommé sur votre planning Gantt !"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = RED_ACCENT
p.space_before = Pt(12)

set_notes(s13, "SLIDE 13 - RESSOURCES HUMAINES (58:00 - 63:00)\nFaire le lien avec le critère 3 de la grille PP2 : 'Pertinence des RH identifiées'. Montrer que rattacher chaque tâche à un profil métier précis garantit 1 point plein sur la grille !")

# ==============================================================================
# SLIDE 14 : LE MARIAGE GANTT & BUDGET : POURQUOI C'EST INSÉPARABLE ?
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Escale 4 : Le Mariage Gantt & Budget — Pourquoi et Comment ?")
add_footer(s14, 14)

c14_top = create_card(s14, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.3), bg_color=NAVY, border_color=ORANGE)
tf14_t = c14_top.text_frame
tf14_t.margin_left = Inches(0.4)
tf14_t.margin_top = Inches(0.2)
p = tf14_t.paragraphs[0]
p.text = "⚡ LE CONSTAT CRUCIAL :"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf14_t.add_paragraph()
p.text = "« Un planning sans budget est un rêve pieux. Un budget sans planning est une loterie. »"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = BG_WHITE
p.space_before = Pt(4)

c14_1 = create_card(s14, Inches(0.8), Inches(3.0), Inches(5.6), Inches(3.7), bg_color=BG_WHITE, border_color=RED_ACCENT)
tf14_1 = c14_1.text_frame
tf14_1.margin_left = tf14_1.margin_right = Inches(0.3)
tf14_1.margin_top = Inches(0.25)
p = tf14_1.paragraphs[0]
p.text = "❌ L'Erreur Fréquente : Le Budget « Hors-Sol »"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = RED_ACCENT
p = tf14_1.add_paragraph()
p.text = "• L'apprenant donne un chiffre global sorti du chapeau (ex : « Mon budget est de 1 000 000 FCFA »).\n\n" \
         "• Problème : On ne sait pas d'où vient ce chiffre, comment il est calculé, ni à quel moment l'argent sera dépensé !\n\n" \
         "• Conséquence : Sanctionné dans le Livrable PP2 (perte de points sur la faisabilité globale)."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(8)

c14_2 = create_card(s14, Inches(6.933), Inches(3.0), Inches(5.6), Inches(3.7), bg_color=BG_WHITE, border_color=TEAL)
tf14_2 = c14_2.text_frame
tf14_2.margin_left = tf14_2.margin_right = Inches(0.3)
tf14_2.margin_top = Inches(0.25)
p = tf14_2.paragraphs[0]
p.text = "✅ La Démarche Professionnelle : Le Budget par Tâche"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = TEAL
p = tf14_2.add_paragraph()
p.text = "• Chaque ligne de votre Gantt se voit attribuer ses coûts directs (temps RH, outils consommés, achat média).\n\n" \
         "• Le budget total devient la SOMME exacte de toutes vos tâches valorisées.\n\n" \
         "• Résultat : Vous savez exactement combien coûte chaque phase, et surtout QUAND payer quoi (maîtrise du cash-flow)."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(8)

set_notes(s14, "SLIDE 14 - MARIAGE GANTT & BUDGET (63:00 - 68:00)\nExpliquer cette liaison intime. Le budget n'est pas un document séparé qu'on invente dans un coin ; c'est la valorisation financière directe des barres de votre diagramme de Gantt.")

# ==============================================================================
# SLIDE 15 : TYPOLOGIE DES COÛTS EN MARKETING NUMÉRIQUE
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "Typologie des Coûts en Marketing Numérique")
add_footer(s15, 15)

cost_types = [
    ("1. Coûts RH / Prestations", "La rémunération du temps de travail des profils mobilisés.\n\n• TJM (Taux Journalier Moyen) ou tarif horaire pour des freelances.\n• Forfait à la tâche (ex : 50 000 FCFA pour le montage vidéo complet).\n• Valorisation du temps du chef de projet.", NAVY),
    ("2. Achat Média (Publicité)", "L'argent payé directement aux plateformes publicitaires pour diffuser vos annonces.\n\n• Meta Ads (Facebook & Instagram).\n• Google Ads / YouTube Ads.\n• TikTok Ads.\n• Budget d'influenceurs ou partenariats.", BLUE_ACCENT),
    ("3. Outils, Logiciels & Tech", "Les abonnements et licences nécessaires à la production et au suivi.\n\n• Outils graphiques (Canva Pro).\n• Plateforme d'emailing (Mailchimp, Brevo).\n• Hébergement web & nom de domaine.\n• Outils de montage ou stockage cloud.", TEAL),
    ("4. Réserve pour Imprévus", "Le coussin financier indispensable pour absorber les aléas de campagne.\n\n• Re-tournage d'un plan vidéo.\n• Hausse imprévue du coût par clic (CPC).\n• Frais bancaires de paiement en devises.\n• Règle d'or : Prévoir 10% à 15% de marge de contingence !", ORANGE)
]

for idx, (c_title, c_desc, col) in enumerate(cost_types):
    x_pos = Inches(0.8 + idx * 3.033)
    c = create_card(s15, x_pos, Inches(1.5), Inches(2.85), Inches(5.2), bg_color=BG_WHITE, border_color=col)
    
    badge = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.15), Inches(1.7), Inches(2.55), Inches(0.5))
    badge.fill.solid()
    badge.fill.fore_color.rgb = col
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = c_title.split(". ")[1]
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s15.shapes.add_textbox(x_pos + Inches(0.15), Inches(2.3), Inches(2.55), Inches(4.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = c_desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = DARK_SLATE

set_notes(s15, "SLIDE 15 - TYPOLOGIE DES COÛTS (68:00 - 73:00)\nDétailler ces 4 familles. Mettre en garde : beaucoup d'apprenants n'incluent QUE le budget Facebook Ads et oublient le coût de production des visuels, ou l'inverse. Insister sur les 10 à 15% de marge pour imprévus (critère tuteur PP2 !).")

# ==============================================================================
# SLIDE 16 : LA MÉCANIQUE DU BUDGET PAR TÂCHE
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
add_header(s16, "La Mécanique du Budget par Tâche : Formule & Tableau Modèle")
add_footer(s16, 16)

c16_f = create_card(s16, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.9), bg_color=BG_LIGHT, border_color=NAVY)
tf16_f = c16_f.text_frame
tf16_f.margin_left = Inches(0.3)
tf16_f.margin_top = Inches(0.12)
p = tf16_f.paragraphs[0]
p.text = "🧮 La Formule du Coût d'une Tâche : " \
         "Coût Tâche = [Temps RH × Taux Horaire/Forfait] + [Achat Média] + [Outils dédiés]"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = NAVY

# Tableau exemple
shape_bt = s16.shapes.add_table(5, 6, Inches(0.8), Inches(2.6), Inches(11.733), Inches(4.2))
t_b = shape_bt.table
t_b.columns[0].width = Inches(1.0)
t_b.columns[1].width = Inches(3.6)
t_b.columns[2].width = Inches(2.2)
t_b.columns[3].width = Inches(1.5)
t_b.columns[4].width = Inches(1.6)
t_b.columns[5].width = Inches(1.833)

b_headers = ["Code", "Intitulé Tâche", "Ressource RH", "Coût RH", "Coût Autre", "Total Tâche"]
for i, h in enumerate(b_headers):
    cell = t_b.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    tf = cell.text_frame
    p = tf.paragraphs[0]
    p.text = h
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = BG_WHITE

b_rows = [
    ("T1", "Rédaction des scripts & briefs", "Concepteur-Rédacteur", "60 000 FCFA", "0 FCFA", "60 000 FCFA"),
    ("T2", "Création des visuels & flyer", "Graphiste freelance", "100 000 FCFA", "15 000 (Canva)", "115 000 FCFA"),
    ("T3", "Tournage & montage vidéo", "Monteur Vidéo", "150 000 FCFA", "20 000 (Loc. mat.)", "170 000 FCFA"),
    ("T4", "Diffusion sponsorisée Meta Ads", "Traffic Manager", "80 000 FCFA", "450 000 (Budget Pub)", "530 000 FCFA")
]

for row_idx, row in enumerate(b_rows, start=1):
    for col_idx, text in enumerate(row):
        cell = t_b.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_LIGHT if row_idx % 2 == 1 else BG_WHITE
        tf = cell.text_frame
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_SLATE
        if col_idx == 5:
            p.font.bold = True
            p.font.color.rgb = ORANGE

set_notes(s16, "SLIDE 16 - BUDGET PAR TÂCHE (73:00 - 77:00)\nMontrer aux apprenants la clarté d'un tableau à double entrée. Le tuteur voit instantanément que pour la tâche T4, il y a 80 000 FCFA d'honoraires et 450 000 FCFA d'achat média direct sur Meta. Rigueur exemplaire !")

# ==============================================================================
# SLIDE 17 : TRÉSORERIE & CASH-FLOW
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
add_header(s17, "La Dimension Temporelle : Trésorerie & Courbe de Décaissement")
add_footer(s17, 17)

c17_top = create_card(s17, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.2), bg_color=BG_WHITE)
tf17_t = c17_top.text_frame
tf17_t.margin_left = tf17_t.margin_right = Inches(0.3)
tf17_t.margin_top = Inches(0.18)
p = tf17_t.paragraphs[0]
p.text = "💸 Pourquoi le timing des dépenses est vital ?"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY
p = tf17_t.add_paragraph()
p.text = "Avoir un budget de 1 500 000 FCFA ne signifie pas qu'on dépense tout le premier jour ! La trésorerie (cash-flow) consiste à savoir combien d'argent doit sortir chaque semaine. Sans cela, le projet s'arrête net par manque de liquidités."
p.font.size = Pt(12.5)
p.font.color.rgb = DARK_SLATE
p.space_before = Pt(4)

weeks = [
    ("Semaine 1", "Préparation & Cadrage", "• Acompte graphiste (30%)\n• Outils & abonnements\n\nDécaissement : 120 000 F", NAVY),
    ("Semaine 2", "Production Créative", "• Acompte monteur vidéo (50%)\n• Frais de shooting\n\nDécaissement : 250 000 F", TEAL),
    ("Semaine 3", "Validation & Solde Prod", "• Solde des prestataires créa\n• Approvisionnement compte pub\n\nDécaissement : 380 000 F", BLUE_ACCENT),
    ("Semaines 4-5", "Campagne Active", "• Dépenses quotidiennes Meta\n• Animation communauté\n\nDécaissement : 650 000 F", ORANGE),
    ("Semaine 6", "Reporting & Clôture", "• Bilan de campagne\n• Rémunération Chef de Projet\n\nDécaissement : 100 000 F", RED_ACCENT)
]

for idx, (w_title, w_sub, w_desc, col) in enumerate(weeks):
    x_pos = Inches(0.8 + idx * 2.426)
    c = create_card(s17, x_pos, Inches(2.9), Inches(2.25), Inches(3.8), bg_color=BG_WHITE, border_color=col)
    
    badge = s17.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.1), Inches(3.05), Inches(2.05), Inches(0.42))
    badge.fill.solid()
    badge.fill.fore_color.rgb = col
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = w_title
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s17.shapes.add_textbox(x_pos + Inches(0.1), Inches(3.55), Inches(2.05), Inches(3.0))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = w_sub
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    p_d = tf.add_paragraph()
    p_d.text = w_desc
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = DARK_SLATE
    p_d.space_before = Pt(8)

set_notes(s17, "SLIDE 17 - TRÉSORERIE & CASH-FLOW (77:00 - 81:00)\nExpliquer l'angoisse du chef de projet qui arrive en semaine 4 sans argent pour payer les pubs parce qu'il a tout payé d'avance aux créatifs. Le plan de décaissement est la marque des gestionnaires d'élite.")

# ==============================================================================
# SLIDE 18 : CAS PRATIQUE COMPLET D-CLIC : CAMPAGNE FRANCOTECHNO
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
add_header(s18, "Cas Pratique : Campagne Digitale « Francotechno » (6 Semaines)")
add_footer(s18, 18)

# Zone gauche : Tableau de synthèse
c18_l = create_card(s18, Inches(0.8), Inches(1.4), Inches(7.2), Inches(5.3), bg_color=BG_WHITE)
tf18_l = c18_l.text_frame
tf18_l.margin_left = tf18_l.margin_right = Inches(0.25)
tf18_l.margin_top = Inches(0.2)
p = tf18_l.paragraphs[0]
p.text = "📋 Plan d'Action & Découpage WBS Synthétique"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = NAVY

# Mini tableau dans la zone gauche
t_cas = s18.shapes.add_table(7, 4, Inches(0.9), Inches(1.8), Inches(7.0), Inches(4.7)).table
t_cas.columns[0].width = Inches(2.7)
t_cas.columns[1].width = Inches(1.3)
t_cas.columns[2].width = Inches(1.5)
t_cas.columns[3].width = Inches(1.5)

cas_headers = ["Tâche", "Durée", "Responsable", "Budget (FCFA)"]
for i, h in enumerate(cas_headers):
    cell = t_cas.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    tf = cell.text_frame
    p = tf.paragraphs[0]
    p.text = h
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = BG_WHITE

cas_data = [
    ("1. Cadrage & Brief stratégique", "S1 (5j)", "Chef de projet", "150 000"),
    ("2. Rédaction scripts & visuels", "S2 (5j)", "Copywriter", "120 000"),
    ("3. Production Flyer & Vidéo", "S2-S3 (8j)", "Graphiste + Vidéaste", "450 000"),
    ("4. Validation interne ◆", "Fin S3 (0j)", "Tuteur / Client", "0 (Jalon)"),
    ("5. Campagne Ads (Meta/TikTok)", "S4-S5 (14j)", "Traffic Manager", "850 000"),
    ("6. Bilan & Reporting final ◆", "S6 (4j)", "Data Analyst", "180 000")
]

for r_idx, row in enumerate(cas_data, start=1):
    for c_idx, val in enumerate(row):
        cell = t_cas.cell(r_idx, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_LIGHT if r_idx % 2 == 1 else BG_WHITE
        tf = cell.text_frame
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK_SLATE
        if c_idx == 3 and not "Jalon" in val:
            p.font.bold = True

# Zone droite : Bilan chiffré consolidé
c18_r = create_card(s18, Inches(8.3), Inches(1.4), Inches(4.233), Inches(5.3), bg_color=BG_WHITE, border_color=TEAL)
tf18_r = c18_r.text_frame
tf18_r.margin_left = tf18_r.margin_right = Inches(0.3)
tf18_r.margin_top = Inches(0.25)
p = tf18_r.paragraphs[0]
p.text = "💰 Budget Consolidé & Répartition"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = TEAL

items_bud = [
    ("Coûts RH & Prestations :", "900 000 FCFA (45%)"),
    ("Achat Média (Publicité) :", "750 000 FCFA (37,5%)"),
    ("Outils, Licences & Matériel :", "100 000 FCFA (5%)"),
    ("Marge d'Imprévus (12,5%) :", "250 000 FCFA (12,5%)"),
]

for lbl, val in items_bud:
    p = tf18_r.add_paragraph()
    p.text = lbl
    p.font.size = Pt(11.5)
    p.font.color.rgb = LIGHT_SLATE
    p.space_before = Pt(8)
    p_v = tf18_r.add_paragraph()
    p_v.text = val
    p_v.font.size = Pt(13)
    p_v.font.bold = True
    p_v.font.color.rgb = NAVY

c_tot = create_card(s18, Inches(8.5), Inches(5.4), Inches(3.8), Inches(1.1), bg_color=NAVY)
tf_tot = c_tot.text_frame
tf_tot.margin_left = Inches(0.2)
tf_tot.margin_top = Inches(0.15)
p = tf_tot.paragraphs[0]
p.text = "TOTAL BUDGET CAMPAGNE :"
p.font.size = Pt(11)
p.font.color.rgb = ORANGE
p = tf_tot.add_paragraph()
p.text = "2 000 000 FCFA (~3 050 €)"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = BG_WHITE

set_notes(s18, "SLIDE 18 - CAS PRATIQUE (81:00 - 86:00)\nCe cas pratique modélise exactement ce qui est attendu pour le Livrable PP2. Attirer l'attention des apprenants sur les 250 000 FCFA de réserve d'imprévus et le jalon de validation en fin de S3.")

# ==============================================================================
# SLIDE 19 : DÉCRYPTAGE DE LA GRILLE DU LIVRABLE PP2 (/6 PTS)
# ==============================================================================
s19 = prs.slides.add_slide(blank_layout)
add_header(s19, "Décryptage de la Grille Officielle du Livrable PP2 (/6 points)")
add_footer(s19, 19)

shape_g = s19.shapes.add_table(7, 3, Inches(0.8), Inches(1.45), Inches(11.733), Inches(5.3))
t_g = shape_g.table
t_g.columns[0].width = Inches(3.2)
t_g.columns[1].width = Inches(1.2)
t_g.columns[2].width = Inches(7.333)

g_headers = ["Critère Officiel", "Barème", "Ce qui donne la note maximale (Conseils Tuteur)"]
for i, h in enumerate(g_headers):
    cell = t_g.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    tf = cell.text_frame
    p = tf.paragraphs[0]
    p.text = h
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BG_WHITE

g_rows = [
    ("1. Planning Gantt", "/1 pt", "Gantt complet, lisible, chronologie impeccable avec phases, tâches, dates et jalons visibles. 0 pt si simple to-do list ou visuel illisible."),
    ("2. Pertinence des tâches", "/1 pt", "Alignement parfait avec le Livrable 1 (PP1). Les tâches réalisent exactement les actions d'acquisition et de rétention prévues."),
    ("3. Pertinence des RH", "/1 pt", "Chaque tâche est associée à un profil métier précis et réaliste (CM, graphiste, rédacteur, chef de projet...). 0 pt si aucune RH."),
    ("4. Cohérence globale", "/1 pt", "Équilibre d'ensemble (temps, budget, RH). Délais crédibles et budget proportionné au projet choisi."),
    ("5. Critère Tuteur 1 : Budget", "/1 pt", "Précision et granularité du chiffrage par tâche (détail RH vs média vs outils au lieu d'un montant vague)."),
    ("6. Critère Tuteur 2 : Sécurité", "/1 pt", "Présence d'une marge pour imprévus (10-15%) et logique claire des jalons de validation intermédiaire.")
]

for r_idx, row in enumerate(g_rows, start=1):
    for c_idx, val in enumerate(row):
        cell = t_g.cell(r_idx, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_LIGHT if r_idx % 2 == 1 else BG_WHITE
        tf = cell.text_frame
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_SLATE
        if c_idx == 0:
            p.font.bold = True
            p.font.color.rgb = NAVY
        elif c_idx == 1:
            p.font.bold = True
            p.alignment = PP_ALIGN.CENTER
            p.font.color.rgb = ORANGE

set_notes(s19, "SLIDE 19 - GRILLE D'ÉVALUATION (86:00 - 90:00)\nLire la grille attentivement. Expliquer aux apprenants que le tuteur ne note pas 'au feeling', mais selon ces 6 points précis. S'ils suivent les recommandations de cette slide, ils ont 6/6 garanti.")

# ==============================================================================
# SLIDE 20 : LES 5 ERREURS ÉLIMINATOIRES À ÉVITER
# ==============================================================================
s20 = prs.slides.add_slide(blank_layout)
add_header(s20, "Les 5 Erreurs Éliminatoires à éviter absolument")
add_footer(s20, 20)

c20_top = create_card(s20, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.85), bg_color=RGBColor(254, 242, 242), border_color=RED_ACCENT)
tf20_t = c20_top.text_frame
tf20_t.margin_left = Inches(0.3)
tf20_t.margin_top = Inches(0.12)
p = tf20_t.paragraphs[0]
p.text = "🚨 CE QUE LES TUTEURS CORRIGENT EN PREMIER (ET QUI FAIT PERDRE DES POINTS) :"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = RED_ACCENT

traps = [
    ("1. Le Gantt To-Do List", "Faire un tableau avec des tâches mais sans dates calendaires, sans barres horizontales ni chronologie visible. C'est 0/1 d'office sur le critère 1 !"),
    ("2. Les Antériorités Oubliées", "Placer des tâches dans le désordre ou faire tout commencer le jour 1 en même temps (ex : lancer la pub Facebook avant d'avoir écrit le script ou monté la vidéo)."),
    ("3. Le Budget Fantaisiste", "Indiquer un budget total de 0 FCFA (« tout est gratuit ») ou au contraire 50 millions sans aucune justification unitaire. Un projet marketing a toujours un coût réel."),
    ("4. L'Oubli des Profils RH", "Ne mentionner aucun responsable ou écrire simplement « l'équipe ». Il faut nommer le profil expert (Community manager, Monteur vidéo, etc.)."),
    ("5. La Déconnexion du PP1", "Inventer un planning qui n'a aucun rapport avec la stratégie de marketing rédigée dans le Livrable 1 (ex : avoir prévu du SEO et de l'emailing en PP1, mais ne mettre que TikTok sur le Gantt).")
]

for idx, (t_title, t_desc) in enumerate(traps):
    y_pos = Inches(2.45 + idx * 0.9)
    c = create_card(s20, Inches(0.8), y_pos, Inches(11.733), Inches(0.82), bg_color=BG_WHITE, border_color=BORDER_COLOR)
    
    badge = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), y_pos + Inches(0.14), Inches(2.6), Inches(0.52))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RED_ACCENT
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = t_title
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(11.5)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s20.shapes.add_textbox(Inches(3.8), y_pos + Inches(0.08), Inches(8.5), Inches(0.65))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = 0
    p = tf_t.paragraphs[0]
    p.text = t_desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = DARK_SLATE

set_notes(s20, "SLIDE 20 - ERREURS ÉLIMINATOIRES (90:00 - 94:00)\nPasser en revue ces 5 pièges avec insistance. Dire aux apprenants : 'Avant de cliquer sur Envoyer pour votre devoir, faites cette checklist des 5 erreurs'.")

# ==============================================================================
# SLIDE 21 : QUELS OUTILS CHOISIR POUR VOTRE RENDU ?
# ==============================================================================
s21 = prs.slides.add_slide(blank_layout)
add_header(s21, "Quels Outils Choisir pour Concevoir votre Gantt & Budget ?")
add_footer(s21, 21)

tools = [
    ("Google Sheets / Excel", "LE RECOMMANDÉ D-CLIC ⭐", [
        "Avantages : Idéal pour combiner le tableau WBS, les barres Gantt et le calcul automatique du budget.",
        "Facilité : Utiliser la mise en forme conditionnelle ou colorier les cellules par semaine.",
        "Export : Enregistrement facile en PDF propre pour le dépôt officiel sur Moodle."
    ], TEAL),
    ("Canva", "L'ALTERNATIVE TRÈS VISUELLE 🎨", [
        "Avantages : Magnifiques modèles prédéfinis de diagrammes de Gantt et de tableaux de bord.",
        "Inconvénients : Moins adapté aux formules de calcul automatique du budget.",
        "Conseil : Faire le budget sous Sheets et insérer le tableau sur Canva."
    ], BLUE_ACCENT),
    ("Notion / GanttProject", "POUR LES PROFILS TECH 💻", [
        "Avantages : Logiciels spécialisés de gestion de projet (GanttProject est gratuit et open-source).",
        "Puissance : Gestion automatique des antériorités et calcul du chemin critique.",
        "Export : Export en image haute résolution intégrable dans votre rapport."
    ], ORANGE)
]

for idx, (t_name, t_badge, points, col) in enumerate(tools):
    x_pos = Inches(0.8 + idx * 4.066)
    c = create_card(s21, x_pos, Inches(1.5), Inches(3.8), Inches(5.2), bg_color=BG_WHITE, border_color=col)
    
    badge = s21.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.2), Inches(1.7), Inches(3.4), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = col
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = t_badge
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(10.5)
    p_b.font.bold = True
    p_b.font.color.rgb = BG_WHITE
    
    t_box = s21.shapes.add_textbox(x_pos + Inches(0.2), Inches(2.25), Inches(3.4), Inches(4.3))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    p = tf.paragraphs[0]
    p.text = t_name
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    for pt in points:
        p_pt = tf.add_paragraph()
        p_pt.text = "• " + pt
        p_pt.font.size = Pt(11.5)
        p_pt.font.color.rgb = DARK_SLATE
        p_pt.space_before = Pt(10)

set_notes(s21, "SLIDE 21 - CHOIX DES OUTILS (94:00 - 98:00)\nRassurer les apprenants : pas besoin d'être un génie de l'informatique. Un Google Sheets propre avec des cellules colorées pour les semaines et une colonne SOMME pour le budget suffit largement pour avoir 6/6 !")

# ==============================================================================
# SLIDE 22 : PLAN D'ACTION, DÉFI DE LA SEMAINE & QUESTIONS / RÉPONSES
# ==============================================================================
s22 = prs.slides.add_slide(blank_layout)
add_header(s22, "Plan d'Action, Q&A & Défi de la Semaine")
add_footer(s22, 22)

c22_l = create_card(s22, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2), bg_color=BG_WHITE)
tf22_l = c22_l.text_frame
tf22_l.margin_left = tf22_l.margin_right = Inches(0.3)
tf22_l.margin_top = Inches(0.3)
p = tf22_l.paragraphs[0]
p.text = "🚀 Votre Feuille de Route de la Semaine"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = NAVY

roadmap = [
    ("Étape 1 : Reprenez votre PP1", "Identifiez vos 2 actions d'acquisition et vos 2 actions de rétention."),
    ("Étape 2 : Faites votre tableau WBS", "Découpez en 4 phases et listez 15 à 20 tâches avec verbes d'action."),
    ("Étape 3 : Tracez votre Gantt", "Fixez les dates, durées, antécédents et jalons de validation sur Sheets ou Canva."),
    ("Étape 4 : Chiffrez le budget par tâche", "Valorisez les profils RH, les achats média et prévoyez 10-15% d'imprévus."),
    ("Étape 5 : Déposez en entraînement", "Bénéficiez du retour de votre tuteur avant l'évaluation finale !")
]

for s_title, s_desc in roadmap:
    p = tf22_l.add_paragraph()
    p.text = f"• {s_title} :"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEAL
    p.space_before = Pt(6)
    p_d = tf22_l.add_paragraph()
    p_d.text = f"   {s_desc}"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = DARK_SLATE

c22_r = create_card(s22, Inches(6.933), Inches(1.5), Inches(5.6), Inches(5.2), bg_color=NAVY, border_color=ORANGE)
tf22_r = c22_r.text_frame
tf22_r.margin_left = tf22_r.margin_right = Inches(0.35)
tf22_r.margin_top = Inches(0.3)
p = tf22_r.paragraphs[0]
p.text = "💬 Place aux Questions & Échanges !"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf22_r.add_paragraph()
p.text = "• Levez la main virtuelle ou posez votre question dans le chat.\n\n" \
         "• Aucun doute ne doit rester sans réponse ce soir.\n\n" \
         "• Vous avez toutes les clés pour faire un Livrable 2 brillant !"
p.font.size = Pt(13)
p.font.color.rgb = BG_WHITE
p.space_before = Pt(12)

c_motto = create_card(s22, Inches(7.2), Inches(4.7), Inches(5.066), Inches(1.6), bg_color=RGBColor(36, 75, 115), border_color=ORANGE)
tf_m = c_motto.text_frame
tf_m.margin_left = Inches(0.2)
tf_m.margin_top = Inches(0.15)
p = tf_m.paragraphs[0]
p.text = "🌟 La devise D-CLIC du Chef de Projet :"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = ORANGE
p = tf_m.add_paragraph()
p.text = "« Planifier ne garantit pas le succès absolu, mais ne pas planifier garantit l'échec. Vous avez le pouvoir de réussir ! »"
p.font.size = Pt(12.5)
p.font.color.rgb = BG_WHITE
p.space_before = Pt(6)

set_notes(s22, "SLIDE 22 - CONCLUSION & Q&A (98:00 - 105:00)\nOuvrir la session de questions/réponses. Répondre avec patience et bienveillance. Rappeler la date limite de dépôt du livrable d'entraînement. Remercier chaleureusement tous les participants.")

# ==============================================================================
# SAUVEGARDE DE LA PRÉSENTATION
# ==============================================================================
prs.save(OUTPUT_PATH)
print(f"Presentation saved successfully to: {OUTPUT_PATH}")
print(f"Total slides generated: {len(prs.slides)}")

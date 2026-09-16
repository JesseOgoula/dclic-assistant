import os
import subprocess
import sys
import fitz

def build_html():
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Guide de Cadrage et Description du Projet Professionnel</title>
<style>
  @page {
    size: A4;
    margin: 14mm 16mm 14mm 16mm;
  }

  *, *:before, *:after {
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #111111;
    background: #ffffff;
    line-height: 1.36;
    font-size: 9pt;
    margin: 0;
    padding: 0;
  }

  .page-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .header {
    border-bottom: 1.2pt solid #111111;
    padding-bottom: 5px;
    margin-bottom: 10px;
  }

  .institution {
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #444444;
    margin-bottom: 2px;
  }

  .doc-title {
    font-size: 13pt;
    font-weight: 800;
    line-height: 1.15;
    color: #111111;
    margin: 0 0 2px 0;
    text-transform: uppercase;
  }

  .doc-subtitle {
    font-size: 8.5pt;
    color: #444444;
    font-weight: 500;
    margin: 0;
  }

  .page-break {
    page-break-before: always;
    break-before: page;
  }

  h1 {
    font-size: 9.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    border-bottom: 0.5pt solid #333333;
    padding-bottom: 2px;
    margin-top: 10px;
    margin-bottom: 6px;
    color: #111111;
  }

  h2 {
    font-size: 9pt;
    font-weight: 700;
    margin-top: 6px;
    margin-bottom: 2px;
    color: #111111;
  }

  p {
    margin: 0 0 4px 0;
    text-align: justify;
  }

  ul {
    margin: 0 0 5px 0;
    padding-left: 15px;
  }

  li {
    margin-bottom: 2px;
  }

  .meta-grid {
    display: table;
    width: 100%;
    margin-bottom: 8px;
    border-collapse: collapse;
  }

  .meta-row {
    display: table-row;
  }

  .meta-label {
    display: table-cell;
    width: 32%;
    font-weight: 600;
    padding: 2px 0;
    color: #333333;
    font-size: 8.5pt;
  }

  .meta-value {
    display: table-cell;
    padding: 2px 0;
    font-size: 8.5pt;
    color: #111111;
  }

  .note-box {
    margin: 6px 0 8px 0;
    padding: 5px 8px;
    border-left: 1.5pt solid #333333;
    background-color: transparent;
    font-size: 8pt;
    color: #222222;
    line-height: 1.3;
  }

  .prompt-guide {
    font-style: italic;
    color: #555555;
    font-size: 8pt;
    margin-bottom: 2px;
  }

  .footer-note {
    margin-top: 8px;
    padding-top: 4px;
    border-top: 0.5pt solid #cccccc;
    font-size: 7.5pt;
    color: #666666;
    display: flex;
    justify-content: space-between;
  }
</style>
</head>
<body>

  <!-- ==================== PARTIE 1 : LE CANEVAS ==================== -->
  <div class="header">
    <div class="institution">Programme D-CLIC &bull; Organisation Internationale de la Francophonie (OIF)</div>
    <div class="doc-title">Canevas de Cadrage du Projet Professionnel</div>
    <div class="doc-subtitle">Marketing Numérique &bull; Livrable Initial : Description et Positionnement du Projet</div>
  </div>

  <div class="note-box">
    <strong>Objet du document :</strong> Cette fiche de cadrage constitue le socle stratégique de votre projet professionnel. Elle dépasse la simple liste de points pour présenter une vision cohérente, concrète et opérationnelle de votre entreprise. Ce travail initial conditionne directement la réussite des livrables ultérieurs : la stratégie marketing (personas, concurrence, plan d'action), la gestion de projet (planning Gantt et budget), la production des contenus (flyer et vidéo) et le tableau de bord des indicateurs.
  </div>

  <h1>I. Fiche Signalétique de l'Organisation</h1>
  <div class="meta-grid">
    <div class="meta-row">
      <div class="meta-label">Nom et prénom de l'apprenant :</div>
      <div class="meta-value">[À renseigner]</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Pays et ville d'implantation :</div>
      <div class="meta-value">[Exemple : Cotonou, Bénin / Dakar, Sénégal / etc.]</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Tuteur référent :</div>
      <div class="meta-value">[Nom du tuteur D-CLIC]</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Sujet de référence :</div>
      <div class="meta-value">[Préciser le numéro du sujet officiel ou mentionner Sujet libre]</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Nom de la marque / entreprise :</div>
      <div class="meta-value">[Dénomination commerciale du projet]</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Signature de marque (slogan) :</div>
      <div class="meta-value">[Formule concise synthétisant la promesse client]</div>
    </div>
  </div>

  <h1>II. Structure Narrative du Projet (4 Axes Directeurs)</h1>

  <h2>1. Contexte, Historique et Structure de l'Entreprise</h2>
  <div class="prompt-guide">Situer l'organisation dans son environnement réel et justifier sa création.</div>
  <ul>
    <li><strong>Genèse et constat initial :</strong> Quel problème concret sur le terrain a motivé ce projet ? Quel est le besoin local non satisfait ?</li>
    <li><strong>Statut et périmètre :</strong> Quelle est la forme de la structure (start-up, TPE/PME, association) et son ancrage géographique ?</li>
    <li><strong>Taille et organisation humaine :</strong> Quel est l'effectif total ? Comment s'organisent les fonctions clés (direction, production, marketing digital, relation client) ?</li>
  </ul>

  <h2>2. Activité, Offre Commerciale et Proposition de Valeur</h2>
  <div class="prompt-guide">Décrire l'offre tangible et ce qui la différencie nettement de la concurrence.</div>
  <ul>
    <li><strong>Nature précise des produits ou services :</strong> Quels articles ou prestations sont commercialisés ? Citer des exemples concrets de la gamme.</li>
    <li><strong>Proposition de valeur unique (USP) :</strong> Quel bénéfice exclusif apporte l'entreprise par rapport aux alternatives déjà existantes ?</li>
    <li><strong>Principes directeurs et valeurs :</strong> Quelles sont les lignes directrices de la marque (qualité, accessibilité, approvisionnement local) ?</li>
  </ul>

  <h2>3. Audience Cible et Comportements Utilisateurs</h2>
  <div class="prompt-guide">Définir avec précision les bénéficiaires et futurs acheteurs.</div>
  <ul>
    <li><strong>Profil socio-démographique prioritaire :</strong> Tranche d'âge, genre, situation professionnelle, niveau d'équipement smartphone et connectivité.</li>
    <li><strong>Attentes prioritaires et freins :</strong> Que recherchent-ils ? Quelles sont les réticences ou craintes à lever (confiance, paiement, livraison) ?</li>
    <li><strong>Cible secondaire ou prescripteurs :</strong> Y a-t-il des partenaires, relais d'opinion ou prescripteurs institutionnels ?</li>
  </ul>

  <h2>4. Objectifs de l'Entreprise et Stratégie Digitale</h2>
  <div class="prompt-guide">Fixer la trajectoire et le cap opérationnel de la campagne marketing.</div>
  <ul>
    <li><strong>Mission globale :</strong> Quel est le rôle économique et social visé à moyen terme ?</li>
    <li><strong>Objectifs de la campagne numérique (méthode SMART) :</strong> Quels résultats chiffrés atteindre sous 90 jours (notoriété, contacts qualifiés, volume de ventes) ?</li>
    <li><strong>Canaux numériques prioritaires :</strong> Quels leviers sont mobilisés en priorité (réseaux sociaux, messagerie instantanée, boutique web mobile) et pourquoi ?</li>
  </ul>

  <div class="footer-note">
    <span>D-CLIC &bull; Marketing Numérique &bull; Projet Professionnel</span>
    <span>Page 1 / 2</span>
  </div>

  <!-- ==================== PARTIE 2 : L'EXEMPLE REDIGE ==================== -->
  <div class="page-break"></div>

  <div class="header">
    <div class="institution">Programme D-CLIC &bull; Organisation Internationale de la Francophonie (OIF)</div>
    <div class="doc-title">Exemple d'Application : Description de Projet</div>
    <div class="doc-subtitle">Illustration concrète basée sur le Sujet n°4 (Start-up e-commerce de produits de beauté)</div>
  </div>

  <div class="meta-grid">
    <div class="meta-row">
      <div class="meta-label">Apprenante :</div>
      <div class="meta-value">Aïcha Traoré</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Formation / Promotion :</div>
      <div class="meta-value">Marketing Numérique D-CLIC &bull; Session 2026</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Tuteur référent :</div>
      <div class="meta-value">Jesse OGOULA</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Sujet choisi :</div>
      <div class="meta-value">Sujet n°4 &bull; Start-up e-commerce de produits de beauté</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Nom de la marque :</div>
      <div class="meta-value">NURA SKINCARE</div>
    </div>
    <div class="meta-row">
      <div class="meta-label">Signature de marque :</div>
      <div class="meta-value">La richesse botanique africaine au service de l'éclat de votre peau.</div>
    </div>
  </div>

  <h1>1. Contexte, Historique et Organisation de l'Entreprise</h1>
  <p>
    Sur le marché cosmétique ouest-africain, les jeunes adultes font face à une double difficulté : la prolifération de produits décapants nocifs pour la santé et une abondance de marques importées coûteuses, rarement adaptées aux spécificités des peaux noires et métissées sous climat tropical. Pour répondre à ce besoin d'authenticité et de sécurité, <strong>Nura Skincare</strong> a été fondée en 2025 à Cotonou (Bénin). L'entreprise est une start-up spécialisée dans la vente en ligne de soins dermo-naturels accessibles et éthiques.
  </p>
  <p>
    L'organisation repose sur une équipe agile de <strong>deux personnes</strong> :
  </p>
  <ul>
    <li><strong>La co-fondatrice et responsable production :</strong> supervise le sourcing des matières premières locales (beurre de karité brut, huiles de moringa et de baobab), la coordination avec le laboratoire certifié partenaire et la logistique des expéditions.</li>
    <li><strong>Le co-fondateur et chargé du marketing numérique :</strong> pilote la boutique en ligne, assure la création des contenus éditoriaux et visuels, gère les campagnes publicitaires et assure la relation client sur les canaux de messagerie.</li>
  </ul>

  <h1>2. Activité, Offre Commerciale et Valeur Ajoutée</h1>
  <p>
    Nura Skincare conçoit et commercialise exclusivement en ligne une gamme courte de soins quotidiens pour le visage : un gel nettoyant doux moussant aux extraits de papaye et de thé vert (150 ml), une crème hydratante unifiante à l'aloe vera et moringa (50 ml), et un sérum anti-imperfections à l'huile de pépins de figue de barbarie et vitamine C (30 ml).
  </p>
  <p>
    <strong>Proposition de valeur unique (USP) :</strong> À la différence des revendeurs généralistes, Nura Skincare associe la vente à un parcours éducatif personnalisé. Chaque visiteur peut réaliser un diagnostic de peau simplifié en ligne et obtenir des recommandations ciblées via WhatsApp avant de finaliser sa commande.
  </p>
  <p>
    <strong>Valeurs fondamentales :</strong> innocuité dermatologique absolue (0 % d'ingrédients éclaircissants), valorisation des filières végétales locales et relation client fondée sur la transparence.
  </p>

  <h1>3. Cible et Profil des Utilisateurs</h1>
  <p>
    L'audience prioritaire est composée de <strong>jeunes femmes et hommes âgés de 18 à 30 ans</strong>, résidant dans les centres urbains du Bénin (Cotonou, Porto-Novo, Calavi) et des métropoles régionales francophones (Lomé, Abidjan).
  </p>
  <ul>
    <li><strong>Comportement numérique :</strong> Utilisateurs quotidiens de smartphones, actifs sur TikTok et Instagram, attentifs aux retours d'expérience vérifiés et aux démonstrations vidéo de routines de soins.</li>
    <li><strong>Attentes et freins :</strong> Ils recherchent un résultat net sur les imperfections et l'excès de sébum causés par la chaleur, sans agresser leur épiderme. Leurs freins majeurs sont la méfiance envers les arnaques du web et les contraintes logistiques. L'intégration des paiements par Mobile Money et la livraison sécurisée à domicile lèvent directement ces obstacles.</li>
  </ul>

  <h1>4. Objectifs de l'Entreprise et Ambition de la Campagne Digitale</h1>
  <p>
    À moyen terme, Nura Skincare entend s'imposer comme la référence e-commerce des soins naturels pour la jeunesse urbaine d'Afrique de l'Ouest. Pour son lancement commercial, une campagne marketing numérique de <strong>90 jours</strong> est articulée autour des objectifs suivants :
  </p>
  <ul>
    <li><strong>Notoriété :</strong> Atteindre 100 000 vues qualifiées sur les formats vidéo éducatifs diffusés sur TikTok et Instagram, et rassembler une communauté active de 5 000 abonnés.</li>
    <li><strong>Acquisition et conversion (SMART) :</strong> Enregistrer <strong>400 commandes effectives</strong> sur la boutique e-commerce et constituer une base de contacts qualifiés de <strong>1 200 prospects opt-in</strong> sous 90 jours.</li>
    <li><strong>Canaux prioritaires :</strong> Vidéos courtes et collaborations avec des micro-créateurs locaux pour la découverte ; WhatsApp Business pour le conseil et la réassurance ; boutique e-commerce mobile-first pour un paiement simple et rapide.</li>
  </ul>

  <div class="footer-note">
    <span>D-CLIC &bull; Marketing Numérique &bull; Projet Professionnel</span>
    <span>Page 2 / 2</span>
  </div>

</body>
</html>
"""
    return html

def main():
    workspace = r"c:\Users\chris\Desktop\Project\DCLIC\DclicAssistant"
    html_path = os.path.join(workspace, "Description_Projet_Canevas_et_Exemple.html")
    pdf_path = os.path.join(workspace, "Description_Projet_Canevas_et_Exemple.pdf")

    html_content = build_html()
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        print(f"SUCCESS: PDF generated! Pages: {len(doc)}, Size: {os.path.getsize(pdf_path)/1024:.1f} KB")
    else:
        print("ERROR:", res.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

/**
 * generate-pdf.js
 * ================
 * Script de génération automatique de rapports PDF D-CLIC.
 *
 * Usage :
 *   node scripts/generate-pdf.js <fichier.md> [--output <fichier.pdf>]
 *
 * Exemples :
 *   node scripts/generate-pdf.js Rapport_Hebdomadaire_1_2026-08-03.md
 *   node scripts/generate-pdf.js Rapport_Hebdomadaire_1_2026-08-03.md --output MonRapport.pdf
 *
 * Le script :
 *   1. Lit le fichier Markdown
 *   2. Convertit le Markdown en HTML stylisé (avec logo D-CLIC intégré en base64)
 *   3. Génère un PDF via Microsoft Edge en mode headless (sans en-tête/pied de page)
 *   4. Range le résultat dans rapports/YYYY-MM-DD/
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ---------------------------------------------------------------------------
// 1. Configuration
// ---------------------------------------------------------------------------

const SCRIPT_DIR = __dirname;
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const LOGO_PATH = path.join(PROJECT_DIR, 'Logo.jpg');
const RAPPORTS_DIR = path.join(PROJECT_DIR, 'rapports');

// Chemins possibles pour Edge sur Windows
const EDGE_PATHS = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  path.join(process.env.LOCALAPPDATA || '', 'Microsoft\\Edge\\Application\\msedge.exe'),
];

// ---------------------------------------------------------------------------
// 2. Utilitaires
// ---------------------------------------------------------------------------

function findEdge() {
  for (const p of EDGE_PATHS) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function logoToBase64() {
  if (!fs.existsSync(LOGO_PATH)) return null;
  const buf = fs.readFileSync(LOGO_PATH);
  return `data:image/jpeg;base64,${buf.toString('base64')}`;
}

/**
 * Crée le dossier rapports/YYYY-MM-DD/ et retourne le chemin.
 */
function createRapportDir() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const dateFolder = `${yyyy}-${mm}-${dd}`;
  const dir = path.join(RAPPORTS_DIR, dateFolder);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

/**
 * Mini-parseur Markdown → HTML.
 * Gère les éléments courants : titres, gras, italique, listes, séparateurs,
 * images, liens, et paragraphes.
 */
function markdownToHtml(md) {
  const lines = md.split('\n');
  const html = [];
  let listStack = []; // stack of {type: 'ul'|'ol', indent}

  function closeListsToIndent(indent) {
    while (listStack.length > 0 && listStack[listStack.length - 1].indent >= indent) {
      const last = listStack.pop();
      html.push(`</${last.type}>`);
    }
  }

  function closeAllLists() {
    while (listStack.length > 0) {
      const last = listStack.pop();
      html.push(`</${last.type}>`);
    }
  }

  function inlineFormat(text) {
    // Images : ![alt](src)
    text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');
    // Liens  : [text](url)
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    // Gras   : **text**
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italique : *text*
    text = text.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    return text;
  }

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    // Ligne vide
    if (line.trim() === '') {
      closeAllLists();
      continue;
    }

    // Séparateur ---
    if (/^-{3,}\s*$/.test(line.trim())) {
      closeAllLists();
      html.push('<hr>');
      continue;
    }

    // Titres
    const headingMatch = line.match(/^(#{1,6})\s+(.*)/);
    if (headingMatch) {
      closeAllLists();
      const level = headingMatch[1].length;
      html.push(`<h${level}>${inlineFormat(headingMatch[2])}</h${level}>`);
      continue;
    }

    // Liste ordonnée : 1. item
    const olMatch = line.match(/^(\s*)\d+\.\s+(.*)/);
    if (olMatch) {
      const content = olMatch[2];
      const indent = olMatch[1].length;
      if (listStack.length === 0 || listStack[listStack.length - 1].type !== 'ol' || listStack[listStack.length - 1].indent < indent) {
        html.push('<ol>');
        listStack.push({ type: 'ol', indent });
      }
      html.push(`<li>${inlineFormat(content)}</li>`);
      continue;
    }

    // Liste non ordonnée : - item
    const ulMatch = line.match(/^(\s*)- (.*)/);
    if (ulMatch) {
      const content = ulMatch[2];
      const indent = ulMatch[1].length;

      // If indent is deeper, open a new sublist
      if (listStack.length === 0 || indent > listStack[listStack.length - 1].indent) {
        html.push('<ul>');
        listStack.push({ type: 'ul', indent });
      } else if (indent < listStack[listStack.length - 1].indent) {
        // Close sublists until we match indent
        while (listStack.length > 0 && listStack[listStack.length - 1].indent > indent) {
          const last = listStack.pop();
          html.push(`</${last.type}>`);
        }
      }
      html.push(`<li>${inlineFormat(content)}</li>`);
      continue;
    }

    // Paragraphe standard
    closeAllLists();
    html.push(`<p>${inlineFormat(line)}</p>`);
  }

  closeAllLists();
  return html.join('\n');
}

// ---------------------------------------------------------------------------
// 3. Template HTML + CSS
// ---------------------------------------------------------------------------

function buildFullHtml(bodyHtml, logoBase64) {
  const logoBlock = logoBase64
    ? `<div class="page-header">
        <img src="${logoBase64}" alt="Logo D-CLIC" class="logo">
        <div class="header-subtitle">D-CLIC : FORMEZ-VOUS AU NUMÉRIQUE AVEC L'OIF</div>
        <div class="header-session">Marketing numérique – Session de juillet</div>
       </div>`
    : '';

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rapport D-CLIC</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :root {
    --color-primary: #1a3a5c;
    --color-accent: #e8912d;
    --color-text: #2c3e50;
    --color-text-light: #5a6a7a;
    --color-bg: #ffffff;
    --color-border: #dce3ea;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: var(--color-text);
    background: var(--color-bg);
    padding: 0;
  }

  /* ---- Page Header with Logo ---- */
  .page-header {
    text-align: center;
    padding: 20px 0 14px;
    border-bottom: 3px solid var(--color-accent);
    margin-bottom: 24px;
  }
  .logo {
    max-width: 300px;
    height: auto;
    margin-bottom: 8px;
  }
  .header-subtitle {
    font-size: 10pt;
    font-weight: 600;
    color: var(--color-primary);
    letter-spacing: 0.5px;
    margin-top: 4px;
  }
  .header-session {
    font-size: 9pt;
    color: var(--color-text-light);
    margin-top: 2px;
  }

  /* ---- Headings ---- */
  h1 {
    font-size: 20pt;
    font-weight: 700;
    color: var(--color-primary);
    text-align: center;
    margin: 20px 0 6px;
    letter-spacing: -0.3px;
  }
  h2 {
    font-size: 13pt;
    font-weight: 700;
    color: var(--color-primary);
    margin: 20px 0 8px;
    padding-bottom: 4px;
    border-bottom: 2px solid var(--color-accent);
    text-transform: uppercase;
  }
  h3 {
    font-size: 11.5pt;
    font-weight: 600;
    color: var(--color-accent);
    margin: 14px 0 6px;
  }

  /* ---- Paragraphs ---- */
  p {
    margin: 4px 0 8px;
    text-align: justify;
  }

  /* ---- HR ---- */
  hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, var(--color-accent), var(--color-primary));
    margin: 20px 0;
    border-radius: 2px;
  }

  /* ---- Lists ---- */
  ul, ol {
    margin: 6px 0 10px 22px;
    padding: 0;
  }
  li {
    margin: 4px 0;
    padding-left: 2px;
  }
  li ul, li ol {
    margin-top: 3px;
    margin-bottom: 3px;
  }
  li strong {
    color: var(--color-primary);
  }

  /* ---- Emphasis ---- */
  strong {
    font-weight: 600;
  }
  em {
    font-style: italic;
    color: var(--color-text-light);
  }

  /* ---- Print ---- */
  @media print {
    body { padding: 0; }
    @page {
      size: A4;
      margin: 18mm 18mm 18mm 18mm;
    }
    .page-header {
      position: running(header);
    }
  }
</style>
</head>
<body>
${logoBlock}
${bodyHtml}
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// 4. Génération PDF via Edge headless
// ---------------------------------------------------------------------------

function generatePdf(htmlPath, pdfPath) {
  const edgePath = findEdge();
  if (!edgePath) {
    console.error('❌ Microsoft Edge introuvable. Chemins essayés :');
    EDGE_PATHS.forEach((p) => console.error(`   - ${p}`));
    process.exit(1);
  }

  console.log(`📄 Impression PDF via Edge...`);
  const fileUrl = `file:///${htmlPath.replace(/\\/g, '/')}`;
  // --print-to-pdf-no-header supprime l'en-tête et le pied de page du navigateur
  const cmd = `"${edgePath}" --headless --disable-gpu --no-sandbox --print-to-pdf="${pdfPath}" --print-to-pdf-no-header "${fileUrl}"`;

  try {
    execSync(cmd, { timeout: 30000, stdio: 'pipe' });
    return true;
  } catch (err) {
    console.error('⚠️  Edge headless a échoué :', err.message);
    return false;
  }
}

// ---------------------------------------------------------------------------
// 5. Main
// ---------------------------------------------------------------------------

function main() {
  // Parse arguments
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
  Usage: node scripts/generate-pdf.js <rapport.md> [--output <fichier.pdf>]

  Options:
    --output, -o   Chemin du fichier PDF de sortie (optionnel)
    --help, -h     Affiche cette aide

  Le rapport est automatiquement rangé dans rapports/YYYY-MM-DD/
    `);
    process.exit(0);
  }

  // Input markdown
  let inputPath = args[0];
  if (!path.isAbsolute(inputPath)) {
    inputPath = path.resolve(process.cwd(), inputPath);
  }
  if (!fs.existsSync(inputPath)) {
    console.error(`❌ Fichier introuvable : ${inputPath}`);
    process.exit(1);
  }

  // Create dated rapport directory
  const rapportDir = createRapportDir();
  const inputBasename = path.basename(inputPath, '.md');

  // Output PDF
  let outputPath;
  const outIdx = args.indexOf('--output') !== -1 ? args.indexOf('--output') : args.indexOf('-o');
  if (outIdx !== -1 && args[outIdx + 1]) {
    outputPath = args[outIdx + 1];
    if (!path.isAbsolute(outputPath)) {
      outputPath = path.resolve(rapportDir, outputPath);
    }
  } else {
    outputPath = path.join(rapportDir, `${inputBasename}.pdf`);
  }

  console.log(`\n🔧 Génération du rapport PDF D-CLIC`);
  console.log(`   Source    : ${inputPath}`);
  console.log(`   Dossier   : ${rapportDir}`);
  console.log(`   Sortie    : ${outputPath}\n`);

  // Step 1 — Read markdown
  console.log('1️⃣  Lecture du Markdown...');
  let mdContent = fs.readFileSync(inputPath, 'utf-8');
  // Remove markdown image of logo if present (we embed it via HTML template)
  mdContent = mdContent.replace(/^!\[.*Logo.*\]\(.*\)\s*\n?/im, '');

  // Step 2 — Convert to HTML
  console.log('2️⃣  Conversion Markdown → HTML...');
  const bodyHtml = markdownToHtml(mdContent);
  const logoBase64 = logoToBase64();
  const fullHtml = buildFullHtml(bodyHtml, logoBase64);

  // Step 3 — Write temp HTML
  const htmlTempPath = path.join(rapportDir, `${inputBasename}_temp.html`);
  fs.writeFileSync(htmlTempPath, fullHtml, 'utf-8');
  console.log(`   ✅ HTML temporaire : ${htmlTempPath}`);

  // Step 4 — Generate PDF
  console.log('3️⃣  Génération du PDF...');
  const success = generatePdf(htmlTempPath, outputPath);

  if (success && fs.existsSync(outputPath)) {
    const sizeKB = (fs.statSync(outputPath).size / 1024).toFixed(1);
    console.log(`\n✅ PDF généré avec succès : ${outputPath} (${sizeKB} Ko)`);

    // Copy the source markdown into the rapport dir
    const mdDest = path.join(rapportDir, path.basename(inputPath));
    fs.copyFileSync(inputPath, mdDest);
    console.log(`📝 Markdown copié : ${mdDest}`);

    // Save clean HTML version
    const htmlDest = path.join(rapportDir, `${inputBasename}.html`);
    fs.copyFileSync(htmlTempPath, htmlDest);
    console.log(`📝 HTML stylisé : ${htmlDest}`);
  } else {
    console.error('\n❌ Échec de la génération du PDF.');
    console.log('   Le fichier HTML stylisé est disponible ici :');
    console.log(`   ${htmlTempPath}`);
    console.log('   Vous pouvez l\'ouvrir dans un navigateur et utiliser Ctrl+P pour imprimer en PDF.');
    process.exit(1);
  }

  // Cleanup temp HTML
  try { fs.unlinkSync(htmlTempPath); } catch (_) {}

  console.log(`\n📁 Fichiers dans ${rapportDir} :`);
  fs.readdirSync(rapportDir).forEach((f) => console.log(`   - ${f}`));
  console.log('\n🎉 Terminé !');
}

main();

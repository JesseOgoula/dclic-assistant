/**
 * generate-docx.js
 * =================
 * Génère un fichier Word (.docx) natif à partir d'un fichier Markdown.
 * Utilise la librairie 'docx' pour créer un document Word valide.
 *
 * Usage :
 *   node scripts/generate-docx.js <fichier.md> [--output <fichier.docx>]
 */

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, Footer, ImageRun,
  TabStopPosition, TabStopType, UnderlineType,
} = require('docx');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const SCRIPT_DIR = __dirname;
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const LOGO_PATH = path.join(PROJECT_DIR, 'Logo.jpg');

const COLORS = {
  primary: '1a3a5c',
  accent: 'e8912d',
  text: '2c3e50',
  textLight: '5a6a7a',
};

// ---------------------------------------------------------------------------
// Markdown Parser → structured blocks
// ---------------------------------------------------------------------------
function parseMarkdown(md) {
  const lines = md.split('\n');
  const blocks = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Empty line
    if (line.trim() === '') continue;

    // HR
    if (/^-{3,}\s*$/.test(line.trim())) {
      blocks.push({ type: 'hr' });
      continue;
    }

    // Headings
    const headingMatch = line.match(/^(#{1,6})\s+(.*)/);
    if (headingMatch) {
      blocks.push({
        type: 'heading',
        level: headingMatch[1].length,
        text: headingMatch[2],
      });
      continue;
    }

    // Ordered list: 1. item
    const olMatch = line.match(/^(\s*)\d+\.\s+(.*)/);
    if (olMatch) {
      blocks.push({
        type: 'list-item',
        ordered: true,
        indent: Math.floor(olMatch[1].length / 2),
        text: olMatch[2],
      });
      continue;
    }

    // Unordered list: - item
    const ulMatch = line.match(/^(\s*)- (.*)/);
    if (ulMatch) {
      blocks.push({
        type: 'list-item',
        ordered: false,
        indent: Math.floor(ulMatch[1].length / 2),
        text: ulMatch[2],
      });
      continue;
    }

    // Regular paragraph
    blocks.push({ type: 'paragraph', text: line });
  }

  return blocks;
}

// ---------------------------------------------------------------------------
// Inline formatting → TextRun[]
// ---------------------------------------------------------------------------
function parseInline(text, defaultOpts = {}) {
  const runs = [];
  // Split by **bold** patterns
  const parts = text.split(/(\*\*[^*]+\*\*)/g);

  for (const part of parts) {
    if (!part) continue;

    const boldMatch = part.match(/^\*\*(.+)\*\*$/);
    if (boldMatch) {
      runs.push(new TextRun({
        text: boldMatch[1],
        bold: true,
        font: 'Arial',
        size: defaultOpts.size || 22,
        color: defaultOpts.boldColor || COLORS.primary,
        ...defaultOpts,
        bold: true,
      }));
    } else {
      // Check for *italic*
      const italicParts = part.split(/(\*[^*]+\*)/g);
      for (const ip of italicParts) {
        if (!ip) continue;
        const italicMatch = ip.match(/^\*(.+)\*$/);
        if (italicMatch) {
          runs.push(new TextRun({
            text: italicMatch[1],
            italics: true,
            font: 'Arial',
            size: defaultOpts.size || 22,
            color: COLORS.textLight,
            ...defaultOpts,
            italics: true,
          }));
        } else {
          runs.push(new TextRun({
            text: ip,
            font: 'Arial',
            size: defaultOpts.size || 22,
            color: defaultOpts.color || COLORS.text,
            ...defaultOpts,
          }));
        }
      }
    }
  }

  return runs;
}

// ---------------------------------------------------------------------------
// Build Document
// ---------------------------------------------------------------------------
async function buildDocument(blocks, logoPath) {
  const children = [];

  // Logo + header
  if (fs.existsSync(logoPath)) {
    const logoData = fs.readFileSync(logoPath);
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 100 },
        children: [
          new ImageRun({
            data: logoData,
            transformation: { width: 300, height: 90 },
            type: 'jpg',
          }),
        ],
      })
    );
  }

  // Sub-header text
  children.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 50 },
      children: [
        new TextRun({
          text: 'D-CLIC : FORMEZ-VOUS AU NUMÉRIQUE AVEC L\'OIF',
          bold: true,
          font: 'Arial',
          size: 20,
          color: COLORS.primary,
        }),
      ],
    })
  );
  children.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 300 },
      children: [
        new TextRun({
          text: 'Marketing numérique – Session de décembre',
          font: 'Arial',
          size: 18,
          color: COLORS.textLight,
        }),
      ],
    })
  );

  // Accent line under header
  children.push(
    new Paragraph({
      spacing: { after: 200 },
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.accent },
      },
      children: [],
    })
  );

  // Process blocks
  for (const block of blocks) {
    switch (block.type) {
      case 'heading': {
        const levelMap = {
          1: HeadingLevel.HEADING_1,
          2: HeadingLevel.HEADING_2,
          3: HeadingLevel.HEADING_3,
        };
        const isH1 = block.level === 1;
        const isH3 = block.level === 3;

        children.push(
          new Paragraph({
            heading: levelMap[block.level] || HeadingLevel.HEADING_3,
            alignment: isH1 ? AlignmentType.CENTER : AlignmentType.LEFT,
            spacing: { before: isH1 ? 300 : 200, after: 100 },
            border: block.level === 2 ? {
              bottom: { style: BorderStyle.SINGLE, size: 4, color: COLORS.accent },
            } : undefined,
            children: [
              new TextRun({
                text: block.text,
                bold: true,
                font: 'Arial',
                size: isH1 ? 36 : block.level === 2 ? 26 : 23,
                color: isH3 ? COLORS.accent : COLORS.primary,
                allCaps: block.level === 2,
              }),
            ],
          })
        );
        break;
      }

      case 'list-item': {
        const bulletChar = block.ordered ? '' : '•  ';
        const indentMM = 360 + (block.indent * 360);

        children.push(
          new Paragraph({
            indent: { left: indentMM },
            spacing: { before: 40, after: 40 },
            children: [
              ...(block.ordered ? [] : [
                new TextRun({
                  text: bulletChar,
                  font: 'Arial',
                  size: 22,
                  color: COLORS.accent,
                }),
              ]),
              ...parseInline(block.text),
            ],
          })
        );
        break;
      }

      case 'hr':
        children.push(
          new Paragraph({
            spacing: { before: 150, after: 150 },
            border: {
              bottom: { style: BorderStyle.SINGLE, size: 3, color: COLORS.accent },
            },
            children: [],
          })
        );
        break;

      case 'paragraph':
      default:
        children.push(
          new Paragraph({
            alignment: AlignmentType.JUSTIFIED,
            spacing: { before: 50, after: 80 },
            children: parseInline(block.text),
          })
        );
        break;
    }
  }

  // Footer
  const footerParagraphs = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 0 },
      children: [
        new TextRun({
          text: 'D-CLIC : FORMEZ-VOUS AU NUMÉRIQUE AVEC L\'OIF',
          bold: true,
          font: 'Arial',
          size: 16,
          color: COLORS.primary,
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: 'Marketing numérique – Session de décembre',
          font: 'Arial',
          size: 16,
          color: COLORS.textLight,
        }),
      ],
    }),
  ];

  const doc = new Document({
    styles: {
      default: {
        document: {
          run: {
            font: 'Arial',
            size: 22,
            color: COLORS.text,
          },
        },
      },
    },
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 1440,
              bottom: 1440,
              left: 1080,
              right: 1080,
            },
          },
        },
        footers: {
          default: new Footer({ children: footerParagraphs }),
        },
        children,
      },
    ],
  });

  return doc;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help')) {
    console.log('Usage: node scripts/generate-docx.js <rapport.md> [--output <fichier.docx>]');
    process.exit(0);
  }

  let inputPath = args[0];
  if (!path.isAbsolute(inputPath)) {
    inputPath = path.resolve(process.cwd(), inputPath);
  }
  if (!fs.existsSync(inputPath)) {
    console.error(`❌ Fichier introuvable : ${inputPath}`);
    process.exit(1);
  }

  // Output path
  let outputPath;
  const outIdx = args.indexOf('--output') !== -1 ? args.indexOf('--output') : args.indexOf('-o');
  if (outIdx !== -1 && args[outIdx + 1]) {
    outputPath = args[outIdx + 1];
    if (!path.isAbsolute(outputPath)) {
      outputPath = path.resolve(path.dirname(inputPath), outputPath);
    }
  } else {
    const basename = path.basename(inputPath, '.md');
    outputPath = path.join(path.dirname(inputPath), `${basename}.docx`);
  }

  console.log(`📝 Génération du document Word...`);
  console.log(`   Source : ${inputPath}`);
  console.log(`   Sortie : ${outputPath}`);

  // Read & parse markdown
  let mdContent = fs.readFileSync(inputPath, 'utf-8');
  // Remove logo image reference if present
  mdContent = mdContent.replace(/^!\[.*Logo.*\]\(.*\)\s*\n?/im, '');

  const blocks = parseMarkdown(mdContent);
  const doc = await buildDocument(blocks, LOGO_PATH);

  // Generate buffer and write
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);

  const sizeKB = (fs.statSync(outputPath).size / 1024).toFixed(1);
  console.log(`✅ Document Word généré : ${outputPath} (${sizeKB} Ko)`);
}

main().catch(err => {
  console.error('❌ Erreur :', err.message);
  process.exit(1);
});

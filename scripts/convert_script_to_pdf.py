"""
Convertisseur du Script Markdown de la Visio Gantt & Budget en PDF haute qualité
Utilise python-markdown pour parser le contenu et Chrome/Edge headless pour le rendu PDF.
"""

import os
import re
import base64
import subprocess
import markdown

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(PROJECT_DIR, "Script_Complet_Visio_Gantt_Budget.md")
HTML_PATH = os.path.join(PROJECT_DIR, "Script_Complet_Visio_Gantt_Budget.html")
PDF_PATH = os.path.join(PROJECT_DIR, "Script_Complet_Visio_Gantt_Budget.pdf")
LOGO_PATH = os.path.join(PROJECT_DIR, "Logo.jpg")

def get_logo_base64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{data}"
    return ""

def build_html_content():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown to html with tables, fences, and callouts
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])

    # Post-process callouts for Action Tuteur & Interaction Chat
    html_body = re.sub(
        r'<code>\[ACTION TUTEUR :(.*?)\]</code>',
        r'<div class="callout action"><span class="callout-badge action-badge">🎬 ACTION TUTEUR</span> \1</div>',
        html_body
    )
    html_body = re.sub(
        r'<code>\[INTERACTION CHAT :(.*?)\]</code>',
        r'<div class="callout chat"><span class="callout-badge chat-badge">💬 INTERACTION CHAT</span> \1</div>',
        html_body
    )
    html_body = re.sub(
        r'<code>\[PAUSE(.*?)\]</code>',
        r'<div class="callout pause"><span class="callout-badge pause-badge">⏱️ PAUSE</span> \1</div>',
        html_body
    )

    logo_b64 = get_logo_base64()
    logo_img_tag = f'<img src="{logo_b64}" class="header-logo" alt="Logo D-CLIC">' if logo_b64 else ''

    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Script Complet Visio : Gantt & Budget - D-CLIC</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 18mm 18mm 18mm;
    @bottom-center {{
      content: "Formation D-CLIC (OIF) — Marketing Numérique • Tuteur : Jesse Adirigno OGOULA";
      font-size: 8pt;
      color: #666;
    }}
  }}
  *, *:before, *:after {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #2C3E50;
    line-height: 1.5;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background: #fff;
  }}
  .header-banner {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #1A3A5C;
    padding-bottom: 12px;
    margin-bottom: 20px;
  }}
  .header-titles {{
    flex: 1;
  }}
  .header-logo {{
    max-height: 55px;
    margin-left: 20px;
  }}
  .tagline {{
    color: #E8912D;
    font-weight: 700;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }}
  h1 {{
    color: #1A3A5C;
    font-size: 18pt;
    margin: 0 0 4px 0;
    font-weight: 800;
    line-height: 1.2;
  }}
  h2 {{
    color: #1A3A5C;
    font-size: 13pt;
    margin: 20px 0 10px 0;
    padding-bottom: 4px;
    border-bottom: 1.5px solid #E8912D;
    page-break-after: avoid;
  }}
  h3 {{
    color: #0D9488;
    font-size: 11pt;
    margin: 16px 0 8px 0;
    page-break-after: avoid;
  }}
  h4 {{
    color: #1A3A5C;
    font-size: 10pt;
    margin: 12px 0 6px 0;
    font-weight: 700;
    page-break-after: avoid;
  }}
  blockquote {{
    background: #F4F6F9;
    border-left: 4px solid #E8912D;
    margin: 14px 0;
    padding: 10px 16px;
    color: #1A3A5C;
    font-style: normal;
  }}
  .callout {{
    margin: 10px 0;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 9pt;
    line-height: 1.4;
  }}
  .callout.action {{
    background: #FEF3C7;
    border-left: 4px solid #D97706;
    color: #92400E;
  }}
  .callout.chat {{
    background: #E0F2FE;
    border-left: 4px solid #0284C7;
    color: #0369A1;
  }}
  .callout.pause {{
    background: #F3E8FF;
    border-left: 4px solid #9333EA;
    color: #6B21A8;
  }}
  .callout-badge {{
    font-weight: 700;
    margin-right: 6px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9pt;
    page-break-inside: avoid;
  }}
  th, td {{
    padding: 6px 10px;
    border: 1px solid #CBD5E1;
    text-align: left;
  }}
  th {{
    background: #1A3A5C;
    color: #fff;
    font-weight: 700;
    font-size: 8.5pt;
    text-transform: uppercase;
  }}
  tr:nth-child(even) {{
    background: #F8FAFC;
  }}
  hr {{
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 18px 0;
  }}
  ul, ol {{
    margin: 8px 0;
    padding-left: 20px;
  }}
  li {{
    margin-bottom: 4px;
  }}
  p {{
    margin: 6px 0;
  }}
  strong {{
    color: #1A3A5C;
  }}
</style>
</head>
<body>

<div class="header-banner">
  <div class="header-titles">
    <div class="tagline">Programme D-CLIC (OIF) • Marketing Numérique • Séquence 3 & PP2</div>
    <h1>Guide d'Animation & Script Verbatim : Diagramme de Gantt & Budget</h1>
    <div style="font-size: 9pt; color: #5A6A7A; margin-top: 4px;">
      Tuteur Référent : <strong>Jesse Adirigno OGOULA</strong> | Durée de la visio : <strong>1h30 (90 min)</strong> | Support : <strong>22 Diapositives</strong>
    </div>
  </div>
  {logo_img_tag}
</div>

{html_body}

</body>
</html>
"""
    return full_html

def main():
    html_content = build_html_content()
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML generated at: {HTML_PATH}")

    # Browser paths
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    browser = chrome_path if os.path.exists(chrome_path) else edge_path

    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(PDF_PATH):
        size_kb = os.path.getsize(PDF_PATH) / 1024
        print(f"SUCCESS: PDF generated successfully! Path: {PDF_PATH} ({size_kb:.1f} KB)")
    else:
        print("ERROR converting PDF:", res.stderr)

if __name__ == "__main__":
    main()

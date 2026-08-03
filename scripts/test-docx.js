const HTMLtoDOCX = require('html-to-docx');
const fs = require('fs');

async function run() {
  try {
    const html = `<div><h1>Test</h1><p>Ceci est un test</p></div>`;
    const buf = await HTMLtoDOCX(html, null, { margins: { top: 1440 } });
    fs.writeFileSync('test1.docx', buf);
    console.log('test1.docx generated');

    const htmlWithStyle = `<style>h1 { color: red; }</style><div><h1>Test 2</h1></div>`;
    const buf2 = await HTMLtoDOCX(htmlWithStyle);
    fs.writeFileSync('test2.docx', buf2);
    console.log('test2.docx generated');

    const bufImage = fs.readFileSync('Logo.jpg');
    const base64 = `data:image/jpeg;base64,${bufImage.toString('base64')}`;
    const htmlWithImg = `<div><img src="${base64}" /></div>`;
    const buf3 = await HTMLtoDOCX(htmlWithImg);
    fs.writeFileSync('test3.docx', buf3);
    console.log('test3.docx generated');
  } catch (e) {
    console.error(e);
  }
}
run();

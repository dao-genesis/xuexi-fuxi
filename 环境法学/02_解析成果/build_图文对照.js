/**
 * 道法自然 · 图文对照生成器
 * 从 _doc.json 重建每个 PDF 的 1:1 图文对照 md
 * 每页：图片引用 + OCR 文字 紧邻对照
 */
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;

// 扫描所有子目录，找含 _doc.json 的
const dirs = fs.readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .filter(d => fs.existsSync(path.join(ROOT, d.name, '_doc.json')));

console.log(`找到 ${dirs.length} 个 PDF 解析目录`);

let totalPdf = 0, totalPages = 0;

for (const dir of dirs) {
  const dirName = dir.name;
  const dirPath = path.join(ROOT, dirName);
  const docPath = path.join(dirPath, '_doc.json');
  
  const doc = JSON.parse(fs.readFileSync(docPath, 'utf-8'));
  const pdfName = doc.pdf_name || dirName + '.pdf';
  const pageCount = doc.page_count || doc.pages.length;
  const pages = doc.pages;
  
  // 章节信息
  const chapterNum = doc.chapter_num;
  const chapterRaw = doc.chapter_raw;
  const lessonSeq = doc.lesson_seq;
  
  // 构建 md
  let md = '';
  md += `# ${dirName}\n\n`;
  md += `> PDF: \`${pdfName}\`\n`;
  md += `> 页数: ${pageCount}\n`;
  if (chapterNum) md += `> 章节: 第${chapterNum}章 ${chapterRaw || ''}\n`;
  if (lessonSeq) md += `> 课次: 第${lessonSeq}节\n`;
  md += `> 生成: 道法自然·图文对照\n\n`;
  
  for (const page of pages) {
    const idx = page.index;
    const img = page.image;
    const ocr = page.ocr_text || '';
    const score = page.ocr_score;
    const embedded = page.embedded_text;
    
    // 页码标记
    md += `---\n\n`;
    md += `## 第 ${idx} 页\n\n`;
    
    // 图片引用（相对路径，md 与图片同目录）
    md += `![第${idx}页](${img})\n\n`;
    
    // OCR 文字对照
    md += `**【图片内文字】**`;
    if (score !== undefined) {
      const pct = (score * 100).toFixed(1);
      const mark = score >= 0.95 ? '✓' : score >= 0.8 ? '⚠' : '✗';
      md += ` OCR置信度: ${pct}% ${mark}`;
    }
    md += `\n\n`;
    
    if (ocr.trim()) {
      md += `> ${ocr.trim().split('\n').join('\n> ')}\n\n`;
    } else {
      md += `> *(此页无OCR文字)*\n\n`;
    }
    
    // 如果有 embedded_text 且不同于 ocr_text，也列出
    if (embedded && embedded.trim() && embedded.trim() !== ocr.trim()) {
      md += `**【PDF内嵌文字】**\n\n`;
      md += `> ${embedded.trim().split('\n').join('\n> ')}\n\n`;
    }
  }
  
  // 写入
  const outPath = path.join(dirPath, '_图文对照.md');
  fs.writeFileSync(outPath, md, 'utf-8');
  
  totalPdf++;
  totalPages += pageCount;
  console.log(`✓ [${totalPdf}/${dirs.length}] ${dirName} · ${pageCount}页 → _图文对照.md`);
}

console.log(`\n完成: ${totalPdf} 个PDF · ${totalPages} 页 · 全部生成 _图文对照.md`);

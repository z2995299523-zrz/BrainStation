import katex from 'katex';

export function renderMarkdown(text: string): string {
  if (!text) return '';

  // Step 1: Extract and protect math expressions FIRST
  const mathBlocks: string[] = [];

  // Extract $$...$$ blocks
  let html = text.replace(/\$\$(.+?)\$\$/gs, (_, formula) => {
    const idx = mathBlocks.length;
    const clean = formula.trim().replace(/\\\\/g, '\\');
    try {
      mathBlocks.push(katex.renderToString(clean, { displayMode: true, throwOnError: false }));
    } catch {
      mathBlocks.push(`<div class="text-center font-mono">${clean}</div>`);
    }
    return `%%MATH_BLOCK_${idx}%%`;
  });

  // Extract $...$ inline
  html = html.replace(/\$(.+?)\$/g, (_, formula) => {
    const idx = mathBlocks.length;
    const clean = formula.trim().replace(/\\\\/g, '\\');
    try {
      mathBlocks.push(katex.renderToString(clean, { throwOnError: false }));
    } catch {
      mathBlocks.push(`<span class="font-mono text-blue-600">${clean}</span>`);
    }
    return `%%MATH_INLINE_${idx}%%`;
  });

  // Step 2: Process markdown on the non-math text
  html = html
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 rounded text-sm font-mono">$1</code>')
    // Headers
    .replace(/^### (.+)$/gm, '<h4 class="font-bold text-gray-800 dark:text-gray-200 mt-3 mb-1">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="font-bold text-lg text-gray-800 dark:text-gray-200 mt-4 mb-2">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="font-bold text-xl text-gray-800 dark:text-gray-200 mt-4 mb-2">$1</h2>')
    // List items
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    // Line breaks
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');

  // Step 3: Restore math expressions
  html = html.replace(/%%MATH_BLOCK_(\d+)%%/g, (_, idx) => mathBlocks[parseInt(idx)]);
  html = html.replace(/%%MATH_INLINE_(\d+)%%/g, (_, idx) => mathBlocks[parseInt(idx)]);

  return html;
}

var text = '在辅料当中，美纹纸的成本占比最大，费用有102万元，故考虑对其优化。优化前，排线工序一直选用宽幅 10cm 美纹纸，此外，由于板材的摩擦性不足，需要三条美纹纸将线缆固定在板材上，整体耗材成本偏高。[https://i.imgs.ovh/2026/09/17/2292d60d5c35ea0090decf79b6cfeb3f.png](https://i.imgs.ovh/2026/09/17/2292d60d5c35ea0090decf79b6cfeb3f.png)';

function parseMarkdown(text) {
    if (!text) return '';
    // 1) Markdown链接 [url](url) → <img>
    text = text.replace(/\[(https?:\/\/[^\]]+\.(?:png|jpg|jpeg|gif|webp))\]\((https?:\/\/[^\)]+\.(?:png|jpg|jpeg|gif|webp))\)/gi, function (_, url1, url2) {
        console.log('Captured URL1:', url1);
        console.log('Captured URL2:', url2);
        return '<br><img src="' + url1 + '" alt="配图" style="max-width:100%;margin:8px 0;border-radius:4px;" onerror="this.style.display=\'none\'">';
    });
    // 2) 裸图片URL → <img>
    text = text.replace(/https?:\/\/[^\s]+\.(?:png|jpg|jpeg|gif|webp)/gi, function (url) {
        return '<br><img src="' + url + '" alt="配图" style="max-width:100%;margin:8px 0;border-radius:4px;" onerror="this.style.display=\'none\'">';
    });
    // 3) Markdown加粗 **text** → <strong>text</strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    return text;
}

var result = parseMarkdown(text);
console.log('\n=== Final Result ===');
console.log(result);

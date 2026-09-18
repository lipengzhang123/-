var text = '[https://i.imgs.ovh/2026/09/17/2292d60d5c35ea0090decf79b6cfeb3f.png](https://i.imgs.ovh/2026/09/17/2292d60d5c35ea0090decf79b6cfeb3f.png)';

// 测试1: 完整正则
var re1 = /\[(https?:\/\/[^\]]+\.(?:png|jpg|jpeg|gif|webp))\]\((https?:\/\/[^\)]+\.(?:png|jpg|jpeg|gif|webp))\)/gi;
console.log('Test 1 (full regex):', re1.test(text));

// 重置lastIndex
re1.lastIndex = 0;
var match1 = text.match(re1);
console.log('Match result:', match1);

// 测试2: 只匹配前半部分 [url]
var re2 = /\[(https?:\/\/[^\]]+\.(?:png|jpg|jpeg|gif|webp))\]/gi;
console.log('Test 2 ([url] only):', re2.test(text));
re2.lastIndex = 0;
console.log('Match:', text.match(re2));

// 测试3: 简化版 - 不用字符类排除]
var re3 = /\[(https?:\/\/.+?\.(?:png|jpg|jpeg|gif|webp))\]\((https?:\/\/.+?\.(?:png|jpg|jpeg|gif|webp))\)/gi;
console.log('Test 3 (simplified .+?):', re3.test(text));
re3.lastIndex = 0;
console.log('Match:', text.match(re3));

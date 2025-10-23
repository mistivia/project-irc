(function() {
    'use strict';
    
    const targetUrlPattern = /https:\/\/raye\.mistivia\.com\/irclog\/([^/]+)\/(\d+)\/$/;
    
    const currentUrl = window.location.href;
    
    const match = currentUrl.match(targetUrlPattern);

    if (match) {
        let channel = match[1]; 
        let year = match[2]; 
        
        channel = channel.replace(/%23/g, '#');
        year = year.replace(/%23/g, '#');
        
        const links = document.querySelectorAll('a');
        
        links.forEach(link => {
            const originalHref = link.getAttribute('href');
            
            if (originalHref && originalHref.match(/^(\d{2}-\d{2}|\d{4}-\d{2}-\d{2}|[a-zA-Z0-9_-]+)\.txt$/)) {
                
                let datePart = originalHref.replace(/\.txt$/, '');
                
                datePart = datePart.replace(/%23/g, '#');
                const newHref = `https://raye.mistivia.com/irclog/view.html#${channel}/${year}/${datePart}`;
                
                link.setAttribute('href', newHref);
            }
        });
    }
})();

(function() {
    // Check if the title starts with "Index of"
    if (document.title.startsWith("Index of")) {
        // --- Mobile-Friendly Styles (CSS equivalent) ---
        var style = document.createElement('style');
        style.textContent = `
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 15px;
                background-color: #ffffff;
                color: #333;
		max-width: 900px;
            }
            h1 {
                font-size: 1.8em; /* 标题稍大 */
                margin-bottom: 15px;
                color: #2c3e50;
            }
            hr {
                border: 0;
                border-top: 1px solid #ddd;
                margin: 10px 0 15px 0;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                padding: 0;
                margin: 0;
            }

            /* 列表项链接样式 */
            a {
                display: block;
                padding: 12px 10px; /* 增加点击区域和间距 */
                font-size: 1.2em; /* 字体大一点 */
                text-decoration: none;
                color: #007aff;
                border-bottom: 1px solid #eee;
                transition: background-color 0.2s ease; /* 添加过渡效果 */
            }

            /* 鼠标悬停变色 (桌面端) */
            a:hover {
                background-color: #f0f8ff; /* 浅蓝色背景 */
                color: #005bb5; /* 链接颜色略深 */
            }

            /* 最后一个元素不显示底部分割线 */
            pre a:last-child {
                border-bottom: none;
            }

            /* 确保只显示文件名 */
            .filename-only {
                display: block !important;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                width: 100%;
            }
        `;
        document.head.appendChild(style);
	const standardContent = 'width=device-width, initial-scale=1.0, viewport-fit=cover';
	const newViewport = document.createElement('meta');
        newViewport.setAttribute('name', 'viewport');
        newViewport.setAttribute('content', standardContent);
        document.head.appendChild(newViewport);
	

        // --- Clean up the Listing (JavaScript DOM Manipulation) ---
        var pre = document.querySelector('pre');
        if (pre) {

            var links = pre.querySelectorAll('a');

            // 2. Clear the original <pre> content
            pre.textContent = '';

            links.forEach(function(link) {
                // Get the href and the filename text
                var filename = link.textContent.trim(); // Trim whitespace
                var href = link.getAttribute('href');

                // Create a new, clean anchor element
                var newLink = document.createElement('a');
                newLink.setAttribute('href', href);
                newLink.classList.add('filename-only');
                newLink.textContent = filename; // Only the filename

                // Append the clean link to the <pre> block
                pre.appendChild(newLink);
            });
        }
    }
})();

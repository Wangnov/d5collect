document.addEventListener('DOMContentLoaded', function () {
    let requestChart, visitorsChart;
    let isUpdating = false;

    function getPageData() {
        const dataElement = document.getElementById('page-data');
        if (dataElement) {
            try {
                return JSON.parse(dataElement.textContent);
            } catch (e) {
                console.error("解析页面数据时出错:", e);
                return null;
            }
        }
        return null;
    }

    // --- 动画与工具函数 ---
    function parseStatValue(text) {
        return parseFloat(String(text).replace(/[,天\s]/g, '')) || 0;
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const currentVal = start + progress * (end - start);

            if (obj.dataset.key === 'avg_matches') {
                obj.textContent = parseFloat(currentVal).toFixed(2);
            } else if (obj.dataset.key === 'period_days') {
                obj.textContent = `${Math.floor(currentVal)} 天`;
            } else {
                obj.textContent = Math.floor(currentVal).toLocaleString();
            }

            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                if (obj.dataset.key === 'avg_matches') {
                    obj.textContent = parseFloat(end).toFixed(2);
                } else if (obj.dataset.key === 'period_days') {
                    obj.textContent = `${end} 天`;
                } else {
                    obj.textContent = end.toLocaleString();
                }
            }
        };
        window.requestAnimationFrame(step);
    }

    function updateAnimatedList(listElement, newItemsHtml) {
        if (!listElement) return;
        const newItemsContainer = new DOMParser().parseFromString(`<ul>${newItemsHtml}</ul>`, "text/html").querySelector('ul');
        const newItems = Array.from(newItemsContainer.children);

        const existingItemsMap = new Map();
        Array.from(listElement.children).forEach(item => {
            if (item.dataset.id) existingItemsMap.set(item.dataset.id, item);
        });

        const newItemsMap = new Map();
        newItems.forEach(item => {
            if (item.dataset.id) newItemsMap.set(item.dataset.id, item);
        });

        existingItemsMap.forEach((item, id) => {
            if (!newItemsMap.has(id)) {
                item.classList.add('fade-out');
                setTimeout(() => item.remove(), 500);
            }
        });

        newItems.reverse().forEach(newItem => {
            const id = newItem.dataset.id;
            if (!id) return;

            const existingItem = existingItemsMap.get(id);

            if (existingItem) {
                if (existingItem.innerHTML !== newItem.innerHTML) {
                    existingItem.innerHTML = newItem.innerHTML;
                    existingItem.classList.add('flash-add');
                    setTimeout(() => existingItem.classList.remove('flash-add'), 1500);
                }
            } else {
                newItem.classList.add('flash-add');
                listElement.insertBefore(newItem, listElement.firstChild);
            }
        });
    }


    // --- 图表初始化 ---
    function initCharts(requestData, visitorsData) {
        const lineChartOptions = {
            responsive: true, maintainAspectRatio: false,
            scales: { x: { type: 'time', time: { unit: 'day', tooltipFormat: 'yyyy-MM-dd' }, grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#e5e7eb' } } },
            plugins: { legend: { display: false } }
        };

        requestChart = new Chart(document.getElementById('requestChart').getContext('2d'), {
            type: 'line',
            data: { datasets: [{ label: '每日请求数', data: requestData.map(item => ({ x: item.date, y: item.count })), fill: true, borderColor: 'rgb(79, 70, 229)', backgroundColor: 'rgba(79, 70, 229, 0.1)', tension: 0.3, pointRadius: 2 }] },
            options: lineChartOptions
        });

        visitorsChart = new Chart(document.getElementById('visitorsChart').getContext('2d'), {
            type: 'line',
            data: { datasets: [{ label: '独立访客数', data: visitorsData.map(item => ({ x: item.date, y: item.count })), fill: true, borderColor: 'rgb(34, 197, 94)', backgroundColor: 'rgba(34, 197, 94, 0.1)', tension: 0.3, pointRadius: 2 }] },
            options: lineChartOptions
        });
    }

    function initialLoadAnimation() {
        document.querySelectorAll('#stats-cards dd').forEach(ddElement => {
            const endValue = parseStatValue(ddElement.textContent);
            if (endValue > 0) {
                animateValue(ddElement, 0, endValue, 1000);
            }
        });
    }

    // --- 核心更新逻辑 ---
    async function updateDashboard() {
        if (isUpdating) return;
        isUpdating = true;

        const btn = document.getElementById('manual-refresh-btn');
        btn.disabled = true;
        document.getElementById('refresh-icon-container').classList.add('hidden');
        document.getElementById('spinner-icon-container').classList.remove('hidden');
        document.getElementById('refresh-text').textContent = '更新中...';

        try {
            const response = await fetch(window.location.href);

            if (response.redirected) {
                console.warn("会话可能已过期。正在重新加载页面...");
                window.location.reload();
                return;
            }

            if (!response.ok) {
                throw new Error(`网络响应错误: ${response.statusText}`);
            }

            const htmlText = await response.text();
            const newDoc = new DOMParser().parseFromString(htmlText, 'text/html');

            const newPageDataElement = newDoc.getElementById('page-data');
            if (!newPageDataElement) {
                console.warn("在刷新内容中未找到 'page-data' 脚本块，可能已登出。");
                window.location.reload(); // 重新加载以跳转到登录页
                return;
            }
            const newData = JSON.parse(newPageDataElement.textContent);
            const newStats = newData.stats;

            // 更新统计卡片
            newDoc.querySelectorAll('#stats-cards dd').forEach(newDd => {
                const key = newDd.dataset.key;
                const currentDd = document.querySelector(`#stats-cards dd[data-key="${key}"]`);
                if (currentDd) {
                    const oldValue = parseStatValue(currentDd.textContent);
                    const newValue = newStats[key] || (key === 'avg_matches' ? 0.0 : 0);
                    if (oldValue !== newValue) {
                        animateValue(currentDd, oldValue, newValue, 800);
                    }
                }
            });

            // 更新列表
            updateAnimatedList(document.getElementById('top-ips-list'), newDoc.getElementById('top-ips-list').innerHTML);
            updateAnimatedList(document.getElementById('recent-requests-list'), newDoc.getElementById('recent-requests-list').innerHTML);

            // 更新图表
            if (newStats.daily_stats) {
                requestChart.data.datasets[0].data = newStats.daily_stats.map(item => ({ x: item.date, y: item.count }));
                requestChart.update();
            }
            if (newStats.daily_unique_visitors) {
                visitorsChart.data.datasets[0].data = newStats.daily_unique_visitors.map(item => ({ x: item.date, y: item.count }));
                visitorsChart.update();
            }

        } catch (error) {
            console.error("Dashboard更新失败:", error);
            document.getElementById('refresh-text').textContent = '更新失败';
            setTimeout(() => {
                document.getElementById('refresh-text').textContent = '手动刷新';
            }, 2000);
        } finally {
            setTimeout(() => {
                btn.disabled = false;
                document.getElementById('refresh-icon-container').classList.remove('hidden');
                document.getElementById('spinner-icon-container').classList.add('hidden');
                document.getElementById('refresh-text').textContent = '手动刷新';
                isUpdating = false;
            }, 500);
        }
    }

    // --- 初始化与事件绑定 ---
    const pageData = getPageData();
    if (pageData) {
        initCharts(pageData.stats.daily_stats, pageData.stats.daily_unique_visitors);
        initialLoadAnimation();
        document.getElementById('manual-refresh-btn').addEventListener('click', updateDashboard);
        setInterval(updateDashboard, 6000); // 适当延长刷新间隔
    }
});
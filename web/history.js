// GitHub Trending Projects 历史记录页面
class HistoryPage {
    constructor() {
        this.historyData = [];
        this.init();
    }

    async init() {
        await this.loadHistory();
        this.renderHistory();
    }

    async loadHistory() {
        // 从 API 加载历史数据
        try {
            const response = await fetch('/api/history');
            if (response.ok) {
                const data = await response.json();
                this.historyData = data.history || [];
            } else {
                this.useMockData();
            }
        } catch (error) {
            console.log('加载历史数据失败，使用模拟数据:', error);
            this.useMockData();
        }
    }

    useMockData() {
        // 模拟历史数据
        this.historyData = [
            {
                id: '2026-W4',
                week: '2026年1月第4周',
                date: '2026-01-24',
                totalProjects: 8,
                categories: {
                    Java: 2,
                    Python: 4,
                    AI: 5
                },
                projects: [
                    { name: 'alibaba/spring-ai-alibaba', stars: 1100, trend: 'rising' },
                    { name: 'ultralytics/yolov5', stars: 45000, trend: 'stable' },
                    { name: 'langchain-ai/langchain', stars: 68000, trend: 'rising' },
                    { name: 'huggingface/transformers', stars: 115000, trend: 'stable' },
                    { name: 'comfyui/ComfyUI', stars: 52000, trend: 'rising' },
                    { name: 'ollama/ollama', stars: 78000, trend: 'rising' },
                    { name: 'TeamNewPipe/NewPipe', stars: 28800, trend: 'stable' },
                    { name: 'apache/dolphinscheduler', stars: 12100, trend: 'stable' }
                ]
            },
            {
                id: '2026-W3',
                week: '2026年1月第3周',
                date: '2026-01-17',
                totalProjects: 7,
                categories: {
                    Java: 2,
                    Python: 3,
                    AI: 4
                },
                projects: [
                    { name: 'langchain-ai/langchain', stars: 67000, trend: 'rising' },
                    { name: 'ollama/ollama', stars: 75000, trend: 'rising' },
                    { name: 'huggingface/transformers', stars: 114000, trend: 'stable' },
                    { name: 'ultralytics/yolov5', stars: 44800, trend: 'stable' },
                    { name: 'comfyui/ComfyUI', stars: 50000, trend: 'rising' },
                    { name: 'TeamNewPipe/NewPipe', stars: 28500, trend: 'stable' },
                    { name: 'apache/dolphinscheduler', stars: 11900, trend: 'stable' }
                ]
            },
            {
                id: '2026-W2',
                week: '2026年1月第2周',
                date: '2026-01-10',
                totalProjects: 6,
                categories: {
                    Java: 2,
                    Python: 3,
                    AI: 3
                },
                projects: [
                    { name: 'ollama/ollama', stars: 70000, trend: 'rising' },
                    { name: 'langchain-ai/langchain', stars: 65000, trend: 'rising' },
                    { name: 'huggingface/transformers', stars: 113000, trend: 'stable' },
                    { name: 'ultralytics/yolov5', stars: 44500, trend: 'stable' },
                    { name: 'TeamNewPipe/NewPipe', stars: 28200, trend: 'stable' },
                    { name: 'apache/dolphinscheduler', stars: 11700, trend: 'stable' }
                ]
            },
            {
                id: '2026-W1',
                week: '2026年1月第1周',
                date: '2026-01-03',
                totalProjects: 5,
                categories: {
                    Java: 1,
                    Python: 2,
                    AI: 3
                },
                projects: [
                    { name: 'huggingface/transformers', stars: 112000, trend: 'stable' },
                    { name: 'ollama/ollama', stars: 65000, trend: 'rising' },
                    { name: 'langchain-ai/langchain', stars: 63000, trend: 'rising' },
                    { name: 'ultralytics/yolov5', stars: 44000, trend: 'stable' },
                    { name: 'TeamNewPipe/NewPipe', stars: 28000, trend: 'stable' }
                ]
            }
        ];
    }

    renderHistory() {
        const container = document.getElementById('history-container');
        if (!container) return;

        if (this.historyData.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>📭 暂无历史记录</h3>
                    <p>历史记录将每周更新一次，请稍后再来查看</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        this.historyData.forEach(record => {
            const card = document.createElement('div');
            card.className = 'history-card';
            
            // 判断projects是完整对象还是只有名称
            const hasFullDetails = record.projects && record.projects.length > 0 && typeof record.projects[0] === 'object';
            
            const badges = [];
            if (hasFullDetails) {
                // 如果有完整详情，计算语言分布
                const langs = {};
                record.projects.forEach(p => {
                    const lang = p.language || 'Other';
                    langs[lang] = (langs[lang] || 0) + 1;
                });
                Object.entries(langs).slice(0, 3).forEach(([lang, count]) => {
                    const langClass = this.getLanguageClass(lang);
                    badges.push(`<span class="stat-badge badge-${langClass}">${lang}: ${count}</span>`);
                });
            } else if (record.categories) {
                // 兼容旧格式
                if (record.categories.Java > 0) {
                    badges.push(`<span class="stat-badge badge-java">Java: ${record.categories.Java}</span>`);
                }
                if (record.categories.Python > 0) {
                    badges.push(`<span class="stat-badge badge-python">Python: ${record.categories.Python}</span>`);
                }
                if (record.categories.AI > 0) {
                    badges.push(`<span class="stat-badge badge-ai">AI: ${record.categories.AI}</span>`);
                }
            }

            card.innerHTML = `
                <div class="history-header">
                    <div class="history-date">📅 ${record.week}</div>
                    <div class="history-stats">
                        ${badges.join('')}
                    </div>
                </div>
                <div class="project-list">
                    ${record.projects && record.projects.length > 0 ? record.projects.slice(0, 5).map(project => {
                        const name = typeof project === 'object' ? project.full_name : project;
                        const stars = typeof project === 'object' ? project.stars : 0;
                        const trend = typeof project === 'object' ? project.trend : 'stable';
                        const projectName = typeof project === 'object' ? project.name : project.split('/')[1];
                        return `
                            <div class="project-item">
                                <a href="project.html?project=${encodeURIComponent(projectName)}" class="project-name" style="color: #667eea; text-decoration: none;">${name}</a>
                                <div class="project-meta">
                                    <span>⭐ ${this.formatNumber(stars)}</span>
                                    <span class="trend-indicator trend-${trend}">${this.getTrendText(trend)}</span>
                                </div>
                            </div>
                        `;
                    }).join('') : '<p style="color: #a0aec0;">暂无项目数据</p>'}
                </div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <a href="report.html?id=${record.id}" class="report-link" style="display: inline-block; margin-right: 10px;">
                        📄 查看完整报告
                    </a>
                    <span style="color: #a0aec0; font-size: 0.85rem;">
                        共 ${record.total_projects || (record.projects ? record.projects.length : 0)} 个项目
                    </span>
                </div>
            `;

            container.appendChild(card);
        });
    }

    getLanguageClass(language) {
        const langMap = {
            'Java': 'java', 'Python': 'python', 'TypeScript': 'typescript',
            'JavaScript': 'javascript', 'Go': 'go', 'Rust': 'rust',
            'C++': 'cpp', 'C': 'c', 'Shell': 'other'
        };
        return langMap[language] || 'other';
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        }
        return num.toString();
    }

    getTrendText(trend) {
        switch (trend) {
            case 'rising': return '↗️ 上升';
            case 'falling': return '↘️ 下降';
            case 'stable': return '➡️ 稳定';
            default: return '• 持平';
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new HistoryPage();
});

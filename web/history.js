// GitHub Trending Projects 历史记录页面
class HistoryManager {
    constructor() {
        this.historyData = [];
        this.init();
    }

    async init() {
        await this.loadHistory();
        this.renderHistory();
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/history/');
            if (response.ok) {
                const data = await response.json();
                this.historyData = data.history || [];
            } else {
                this.useMockData();
            }
        } catch (error) {
            console.warn('加载历史数据失败:', error);
            this.useMockData();
        }
    }

    useMockData() {
        this.historyData = [];
    }

    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
        return num.toString();
    }

    getTrendEmoji(trend) {
        const icons = { 'rising': '↗️', 'falling': '↘️', 'steady': '➡️', 'stable': '✅' };
        return icons[trend] || '•';
    }

    renderHistory() {
        const container = document.getElementById('history-container');
        if (!container) return;

        if (!this.historyData || this.historyData.length === 0) {
            container.innerHTML = `
                <div class="no-history">
                    <h3>📭 暂无历史记录</h3>
                    <p>点击右上角"刷新数据"按钮生成第一份报告</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        this.historyData.forEach((record, index) => {
            const section = document.createElement('div');
            section.className = 'history-section';
            section.style.animationDelay = `${index * 0.15}s`;
            
            const projects = record.projects || [];
            // 兼容 total_projects 和 totalProjects
            const totalProjects = record.total_projects || record.totalProjects || projects.length;
            const displayDate = record.week || record.date || record.displayDate;
            
            section.innerHTML = `
                <div class="history-header">
                    <span class="history-date">📅 ${displayDate}</span>
                    <a href="report.html?id=${record.id}" class="report-link">📄 查看完整报告</a>
                </div>
                
                <div class="summary-content">
                    <h3>📊 本周亮点</h3>
                    <ul>
                        <li>收录了 ${totalProjects} 个热门开源项目</li>
                        <li>涵盖 AI/机器学习、Web开发等多个领域</li>
                        <li>每周持续更新，追踪技术前沿</li>
                    </ul>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">${totalProjects}</div>
                            <div class="stat-label">收录项目</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${this.formatNumber(projects.reduce((sum, p) => sum + (p.stars || 0), 0))}</div>
                            <div class="stat-label">总 Stars</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${this.getTopLanguage(projects)}</div>
                            <div class="stat-label">热门语言</div>
                        </div>
                    </div>
                </div>

                <h4 style="margin: 20px 0 15px 0;">🏆 本周 Top ${Math.min(projects.length, 5)} 项目</h4>
                <div class="projects-preview">
                    ${projects.slice(0, 5).map((project, i) => {
                        const name = project.full_name || project.name || '未知项目';
                        const shortName = name.split('/')[1] || name;
                        const stars = project.stars || 0;
                        const language = project.language || 'Other';
                        const trend = project.trend || 'stable';
                        const description = project.description || '';
                        const category = project.category || '';
                        
                        return `
                            <div class="project-item">
                                <a href="project.html?project=${encodeURIComponent(shortName)}" class="project-name" style="color: #667eea; text-decoration: none;">${name}</a>
                                <div class="project-stats">
                                    <span>⭐ ${this.formatNumber(stars)}</span>
                                    <span>${this.getTrendEmoji(trend)}</span>
                                </div>
                                ${description ? `
                                <p style="color: #a0aec0; font-size: 0.85rem; margin-top: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                    ${description.substring(0, 50)}${description.length > 50 ? '...' : ''}
                                </p>
                                ` : ''}
                                ${category ? `
                                <span class="language-tag ${this.getLanguageClass(language)}" style="margin-top: 8px; font-size: 0.75rem;">${category}</span>
                                ` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            `;

            container.appendChild(section);
        });
    }

    getTopLanguage(projects) {
        const langs = {};
        projects.forEach(p => {
            const lang = p.language || 'Other';
            langs[lang] = (langs[lang] || 0) + 1;
        });
        return Object.keys(langs).sort((a, b) => langs[b] - langs[a])[0] || '-';
    }

    getLanguageClass(language) {
        const langMap = {
            'Java': 'java', 'Python': 'python', 'TypeScript': 'typescript',
            'JavaScript': 'javascript', 'Go': 'go', 'Rust': 'rust',
            'C++': 'cpp', 'C': 'c', 'Shell': 'other'
        };
        return langMap[language] || 'other';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('loaded');
    new HistoryManager();
});

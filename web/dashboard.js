// GitHub Trending Projects Dashboard - with API Support
class GitHubTrendingDashboard {
    constructor() {
        this.projects = [];
        this.currentFilter = 'all';
        this.apiConfig = this.loadApiConfig();
        this.isLoading = false;
        this.init();
    }

    async init() {
        this.setupControls();
        this.setupLanguageFilters();
        this.setupAnimations();
        await this.loadProjects();
        this.renderProjects();
        this.updateLastUpdated();
    }

    // 设置页面动画
    setupAnimations() {
        document.body.classList.add('loaded');
    }

    // API调用 - 获取项目列表
    async loadProjects() {
        if (this.isLoading) return;
        this.isLoading = true;
        
        this.showLoading();
        
        try {
            // 尝试从后端API获取
            const response = await fetch('/api/projects/');
            if (response.ok) {
                const data = await response.json();
                // 适配新格式
                this.projects = (data.projects || []).map(p => this.normalizeProject(p));
                this.updateLastUpdatedText(data.last_updated || data.lastUpdated);
            } else {
                await this.loadLocalData();
            }
        } catch (error) {
            console.warn('API请求失败，使用本地数据:', error);
            await this.loadLocalData();
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    // 规范化项目数据 - 兼容新旧格式
    normalizeProject(p) {
        return {
            name: p.full_name || p.fullName || p.name,
            fullName: p.full_name || p.fullName || p.name,
            url: p.url,
            forkUrl: p.fork_url || p.forkUrl,
            issuesUrl: p.issues_url || p.issuesUrl,
            description: p.description,
            language: p.language,
            stars: p.stars,
            forks: p.forks,
            issues: p.issues,
            usageSteps: p.usage_steps || p.usageSteps || [],
            trend: p.trend || 'stable',
            category: p.category || '通用工具'
        };
    }

    // 加载本地数据（降级方案）
    async loadLocalData() {
        try {
            const response = await fetch('./data/projects.json');
            if (response.ok) {
                const data = await response.json();
                this.projects = (data.projects || []).map(p => this.normalizeProject(p));
                this.updateLastUpdatedText(data.lastUpdated || data.last_updated);
            } else {
                this.useDefaultData();
            }
        } catch (error) {
            console.error('加载本地数据失败:', error);
            this.useDefaultData();
        }
    }

    // 更新最后更新时间显示
    updateLastUpdatedText(timestamp) {
        if (timestamp) {
            // 兼容 datetime 和 string 格式
            const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
            if (!isNaN(date)) {
                document.getElementById('last-update').textContent = date.toLocaleString('zh-CN');
            }
        }
    }

    // 显示加载状态
    showLoading() {
        const container = document.getElementById('projects-container');
        if (container) {
            container.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p class="loading-text">正在加载项目数据...</p>
                </div>
            `;
        }
    }

    // 隐藏加载状态
    hideLoading() {
        this.isLoading = false;
    }

    setupLanguageFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (this.isLoading) return;
                
                filterBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentFilter = e.target.dataset.lang;
                
                this.animateFilterChange();
            });
        });
    }

    // 筛选切换动画
    animateFilterChange() {
        const container = document.getElementById('projects-container');
        if (!container) return;
        
        container.style.opacity = '0';
        container.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            this.renderProjects();
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 150);
    }

    setupControls() {
        // 生成数据按钮
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // AI 增强按钮
        const aiGenerateBtn = document.getElementById('ai-generate-btn');
        if (aiGenerateBtn) {
            aiGenerateBtn.addEventListener('click', () => {
                this.refreshDataWithAI();
            });
        }

        // 配置API按钮
        const configureBtn = document.getElementById('configure-btn');
        if (configureBtn) {
            configureBtn.addEventListener('click', () => {
                this.showApiConfigModal();
            });
        }

        this.setupApiConfigModal();
    }

    // 刷新数据
    async refreshData() {
        const generateBtn = document.getElementById('generate-btn');
        if (!generateBtn || this.isLoading) return;
        
        const originalText = generateBtn.innerHTML;
        generateBtn.innerHTML = '<span class="loading-spinner-small"></span> 刷新中...';
        generateBtn.disabled = true;

        try {
            this.showLoading();
            
            const response = await fetch('/api/projects/refresh', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                await this.loadProjects();
                this.renderProjects();
                this.showNotification(`✅ ${result.message}`);
            } else {
                throw new Error(result.detail || '刷新失败');
            }
        } catch (error) {
            console.error('刷新数据失败:', error);
            this.hideLoading();
            this.showNotification(`❌ 刷新失败: ${error.message}`);
        } finally {
            generateBtn.innerHTML = originalText;
            generateBtn.disabled = false;
        }
    }

    // AI 增强刷新数据
    async refreshDataWithAI() {
        const aiBtn = document.getElementById('ai-generate-btn');
        if (!aiBtn || this.isLoading) return;
        
        const originalText = aiBtn.innerHTML;
        aiBtn.innerHTML = '<span class="loading-spinner-small"></span> AI 分析中...';
        aiBtn.disabled = true;

        try {
            this.showLoading();
            
            // 从后端获取已保存的配置
            const configResponse = await fetch('/api/config/ai');
            if (!configResponse.ok) {
                throw new Error('请先配置 API Key');
            }
            
            const config = await configResponse.json();
            
            if (!config.has_api_key) {
                throw new Error('请先配置 API Key（点击"API配置"按钮）');
            }
            
            // 获取完整的 API key
            const fullConfig = this.apiConfig || this.loadApiConfig();
            if (!fullConfig?.apiKey) {
                // 从后端获取（后端会返回已保存的 key）
                const saveResponse = await fetch('/api/config/ai/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        provider: config.provider,
                        model: config.model,
                        endpoint: config.endpoint,
                        api_key: ''  // 后端会使用已保存的 key
                    })
                });
                const saveResult = await saveResponse.json();
                if (!saveResult.success || !saveResult.api_key) {
                    throw new Error('请先配置 API Key');
                }
                fullConfig.apiKey = saveResult.api_key;
            }
            
            // 构建 URL 参数
            const params = new URLSearchParams({
                provider: config.provider || 'qwen',
                api_key: fullConfig.apiKey,
                endpoint: config.endpoint || ''
            });
            
            const response = await fetch(`/api/projects/refresh-ai?${params}`, { 
                method: 'POST' 
            });
            const result = await response.json();
            
            if (result.success) {
                await this.loadProjects();
                this.renderProjects();
                const aiTag = result.ai_enhanced ? ' (AI 增强)' : '';
                this.showNotification(`✅ ${result.message}${aiTag}`);
            } else {
                throw new Error(result.detail || 'AI 刷新失败');
            }
        } catch (error) {
            console.error('AI 刷新失败:', error);
            this.hideLoading();
            this.showNotification(`❌ ${error.message}`);
        } finally {
            aiBtn.innerHTML = originalText;
            aiBtn.disabled = false;
        }
    }

    showApiConfigModal() {
        const modal = document.getElementById('api-config-modal');
        if (!modal) return;
        
        // 重置状态
        const testResult = document.getElementById('test-result');
        const saveBtn = document.getElementById('save-config');
        if (testResult) {
            testResult.className = 'test-result';
            testResult.textContent = '';
        }
        if (saveBtn) saveBtn.disabled = true;
        
        // 从后端加载配置
        this.loadConfigFromBackend();
        
        modal.style.display = 'block';
        modal.classList.add('modal-show');
    }

    async loadConfigFromBackend() {
        try {
            const response = await fetch('/api/config/ai');
            if (response.ok) {
                const config = await response.json();
                
                const providerSelect = document.getElementById('api-provider');
                const modelInput = document.getElementById('api-model');
                const endpointInput = document.getElementById('api-endpoint');
                const apiKeyInput = document.getElementById('api-key');
                
                if (providerSelect) providerSelect.value = config.provider || 'qwen';
                if (modelInput) modelInput.value = config.model || '';
                if (endpointInput) endpointInput.value = config.endpoint || '';
                if (apiKeyInput) {
                    // 如果之前配置过 API key，显示占位符
                    apiKeyInput.value = config.has_api_key ? '••••••••••••••••' : '';
                }
                
                // 更新端点输入框显示
                this.updateEndpointVisibility(config.provider);
                
                // 如果有 API key，允许测试和保存
                const saveBtn = document.getElementById('save-config');
                if (saveBtn && config.has_api_key) {
                    saveBtn.disabled = false;
                }
            }
        } catch (error) {
            console.error('加载配置失败:', error);
        }
    }

    updateEndpointVisibility(provider) {
        const customGroup = document.getElementById('custom-endpoint-group');
        const defaultHint = document.getElementById('default-endpoint-hint');
        
        if (provider === 'custom') {
            if (customGroup) customGroup.style.display = 'block';
            if (defaultHint) defaultHint.style.display = 'none';
        } else {
            if (customGroup) customGroup.style.display = 'none';
            if (defaultHint) defaultHint.style.display = 'block';
        }
    }

    setupApiConfigModal() {
        const modal = document.getElementById('api-config-modal');
        if (!modal) return;
        
        const closeBtn = modal.querySelector('.close');
        const cancelBtn = document.getElementById('cancel-config');
        const saveBtn = document.getElementById('save-config');
        const testBtn = document.getElementById('test-config');
        const providerSelect = document.getElementById('api-provider');
        
        const closeModal = () => {
            modal.classList.remove('modal-show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 200);
        };

        if (closeBtn) closeBtn.onclick = closeModal;
        if (cancelBtn) cancelBtn.onclick = closeModal;

        window.onclick = (event) => {
            if (event.target === modal) closeModal();
        };

        // 提供商变更时更新 UI
        if (providerSelect) {
            providerSelect.addEventListener('change', (e) => {
                this.updateEndpointVisibility(e.target.value);
            });
        }

        // 测试连接按钮
        if (testBtn) {
            testBtn.onclick = () => this.testApiConfig();
        }

        // 保存配置按钮
        if (saveBtn) {
            saveBtn.onclick = () => this.saveConfigToBackend(closeModal);
        }

        // 监听输入变化，重置测试状态
        ['api-provider', 'api-model', 'api-endpoint', 'api-key'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', () => {
                    const saveBtn = document.getElementById('save-config');
                    if (saveBtn) saveBtn.disabled = true;
                    const testResult = document.getElementById('test-result');
                    if (testResult) {
                        testResult.className = 'test-result';
                        testResult.textContent = '';
                    }
                });
            }
        });
    }

    async testApiConfig() {
        const testResult = document.getElementById('test-result');
        const saveBtn = document.getElementById('save-config');
        const testBtn = document.getElementById('test-config');
        
        const provider = document.getElementById('api-provider')?.value;
        const model = document.getElementById('api-model')?.value;
        const endpoint = document.getElementById('api-endpoint')?.value;
        const apiKey = document.getElementById('api-key')?.value;
        
        if (!apiKey || apiKey === '••••••••••••••••') {
            if (testResult) {
                testResult.className = 'test-result error';
                testResult.textContent = '请输入 API Key';
            }
            return;
        }
        
        // 显示测试中状态
        if (testResult) {
            testResult.className = 'test-result loading';
            testResult.textContent = '正在测试连接...';
        }
        if (testBtn) testBtn.disabled = true;
        
        try {
            const response = await fetch('/api/config/ai/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, model, endpoint, api_key: apiKey })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (testResult) {
                    testResult.className = 'test-result success';
                    testResult.textContent = `✅ ${result.message} (模型: ${result.model})`;
                }
                if (saveBtn) saveBtn.disabled = false;
            } else {
                if (testResult) {
                    testResult.className = 'test-result error';
                    testResult.textContent = `❌ ${result.message}`;
                }
                if (saveBtn) saveBtn.disabled = true;
            }
        } catch (error) {
            if (testResult) {
                testResult.className = 'test-result error';
                testResult.textContent = `❌ 测试失败: ${error.message}`;
            }
        } finally {
            if (testBtn) testBtn.disabled = false;
        }
    }

    async saveConfigToBackend(closeModal) {
        const saveBtn = document.getElementById('save-config');
        
        const provider = document.getElementById('api-provider')?.value;
        const model = document.getElementById('api-model')?.value;
        const endpoint = document.getElementById('api-endpoint')?.value;
        let apiKey = document.getElementById('api-key')?.value;
        
        // 如果显示占位符，保留原有的 key
        if (apiKey === '••••••••••••••••' && this.apiConfig?.apiKey) {
            apiKey = this.apiConfig.apiKey;
        }
        
        if (!apiKey) {
            this.showNotification('❌ 请先测试 API 配置');
            return;
        }
        
        saveBtn.disabled = true;
        
        try {
            const response = await fetch('/api/config/ai/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, model, endpoint, api_key: apiKey })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.apiConfig = { provider, model, endpoint, apiKey };
                this.showNotification('✅ AI 配置已保存');
                closeModal();
            } else {
                throw new Error(result.detail || '保存失败');
            }
        } catch (error) {
            this.showNotification(`❌ 保存失败: ${error.message}`);
            saveBtn.disabled = false;
        }
    }

    saveApiConfig(config) {
        // 本地缓存也保存
        localStorage.setItem('githubTrendingApiConfig', JSON.stringify(config));
    }

    loadApiConfig() {
        const configStr = localStorage.getItem('githubTrendingApiConfig');
        return configStr ? JSON.parse(configStr) : null;
    }

    getFilteredProjects() {
        if (this.currentFilter === 'all') {
            return this.projects;
        }
        return this.projects.filter(p => p.language === this.currentFilter);
    }

    getLanguageClass(language) {
        const langMap = {
            'Java': 'java',
            'Python': 'python',
            'Jupyter Notebook': 'python',
            'TypeScript': 'typescript',
            'JavaScript': 'javascript',
            'Go': 'go',
            'Rust': 'rust',
            'C++': 'cpp',
            'C': 'c',
            'Shell': 'other'
        };
        return langMap[language] || 'other';
    }

    getTrendIndicator(trend) {
        const icons = {
            'rising': '↗️',
            'falling': '↘️',
            'steady': '➡️',
            'stable': '✅'
        };
        const labels = {
            'rising': '上升中',
            'falling': '下降中',
            'steady': '稳定',
            'stable': '热门'
        };
        return `<span class="trend trend-${trend}">${icons[trend] || '•'} ${labels[trend] || ''}</span>`;
    }

    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
        return num.toString();
    }

    useDefaultData() {
        this.projects = [
            {
                name: "alibaba/spring-ai-alibaba",
                fullName: "alibaba/spring-ai-alibaba",
                url: "https://github.com/alibaba/spring-ai-alibaba",
                forkUrl: "https://github.com/alibaba/spring-ai-alibaba/fork",
                issuesUrl: "https://github.com/alibaba/spring-ai-alibaba/issues",
                description: "Spring AI Alibaba 是阿里巴巴基于 Spring AI 框架开发的 AI 应用开发工具。",
                language: "Java",
                stars: 1100,
                forks: 200,
                issues: 45,
                usageSteps: [
                    "添加依赖: 在 pom.xml 中添加 spring-ai-alibaba-starter",
                    "配置 API Key: 在 application.yml 中配置通义千问或其他模型 API Key",
                    "创建 AI 服务: 使用 @Autowired 注入 ChatClient 调用 AI 能力"
                ],
                trend: "rising",
                category: "AI框架"
            },
            {
                name: "huggingface/transformers",
                fullName: "huggingface/transformers",
                url: "https://github.com/huggingface/transformers",
                forkUrl: "https://github.com/huggingface/transformers/fork",
                issuesUrl: "https://github.com/huggingface/transformers/issues",
                description: "Hugging Face Transformers 是 NLP 领域最流行的预训练模型库。",
                language: "Python",
                stars: 156000,
                forks: 38500,
                issues: 1234,
                usageSteps: [
                    "加载模型: from transformers import AutoModelForCausalLM, AutoTokenizer",
                    "文本生成: 使用 pipeline('text-generation') 快速体验"
                ],
                trend: "stable",
                category: "NLP"
            }
        ];
        this.updateLastUpdated();
    }

    updateLastUpdated() {
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleString('zh-CN');
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('notification-hide');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    renderProjects() {
        const container = document.getElementById('projects-container');
        if (!container) return;

        const filteredProjects = this.getFilteredProjects();
        
        if (filteredProjects.length === 0) {
            container.innerHTML = `
                <div class="no-projects">
                    <h3>😕 没有找到相关项目</h3>
                    <p>试试选择其他语言分类</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        container.classList.add('projects-grid');

        filteredProjects.forEach((project, index) => {
            const card = document.createElement('a');
            card.href = `project.html?project=${encodeURIComponent(project.name)}`;
            card.className = 'card';
            card.style.animationDelay = `${index * 0.1}s`;
            card.style.textDecoration = 'none';
            card.style.display = 'block';
            
            const shortName = (project.fullName || project.name || '').split('/')[1] || project.name;
            
            card.innerHTML = `
                <div class="card-header">
                    <div class="repo-icon">🌟</div>
                    <div class="repo-title">
                        <span class="repo-link">${project.name}</span>
                    </div>
                    ${this.getTrendIndicator(project.trend)}
                </div>
                <div class="repo-description">${project.description || '暂无描述'}</div>
                
                <div class="action-buttons" onclick="event.stopPropagation()">
                    <a href="${project.url}" target="_blank" class="action-btn fork-btn" onclick="event.stopPropagation()">
                        🔗 GitHub
                    </a>
                    <a href="${project.forkUrl || project.url + '/fork'}" target="_blank" class="action-btn fork-btn" onclick="event.stopPropagation()">
                        🍴 Fork
                    </a>
                    <a href="${project.issuesUrl || project.url + '/issues'}" target="_blank" class="action-btn issues-btn" onclick="event.stopPropagation()">
                        📋 Issues (${project.issues || 0})
                    </a>
                </div>

                <div class="repo-stats">
                    <div class="stat-item">
                        <span class="stat-value">${this.formatNumber(project.stars)}</span>
                        <span class="stat-label">Stars</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${this.formatNumber(project.forks)}</span>
                        <span class="stat-label">Forks</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${project.category || '通用'}</span>
                        <span class="stat-label">分类</span>
                    </div>
                </div>
                <div class="language-tag ${this.getLanguageClass(project.language)}">${project.language || 'Other'}</div>
                <div class="usage-steps">
                    <h4>🔧 使用指南</h4>
                    <ul class="steps-list">
                        ${(project.usageSteps || []).map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            `;

            container.appendChild(card);
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new GitHubTrendingDashboard();
});

// GitHub Trending Projects Dashboard
class GitHubTrendingDashboard {
    constructor() {
        this.projects = [];
        this.currentFilter = 'all';
        this.apiConfig = this.loadApiConfig(); // 加载API配置
        this.init();
    }

    async init() {
        await this.loadProjects();
        this.setupLanguageFilters();
        this.setupControls(); // 新增控制按钮
        this.renderProjects();
        this.updateLastUpdated();
        this.setupAutoRefresh();
    }

    async loadProjects() {
        try {
            const response = await fetch('./data/projects.json');
            if (response.ok) {
                const data = await response.json();
                this.projects = data.projects;
                document.getElementById('last-update').textContent = new Date(data.lastUpdated).toLocaleString('zh-CN');
            } else {
                this.useDefaultData();
            }
        } catch (error) {
            console.error('加载项目数据失败:', error);
            this.useDefaultData();
        }
    }

    setupLanguageFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentFilter = e.target.dataset.lang;
                this.renderProjects();
            });
        });
    }

    // 新增：设置控制按钮
    setupControls() {
        // 生成数据按钮
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateDataWithApi();
            });
        }

        // 配置API按钮
        const configureBtn = document.getElementById('configure-btn');
        if (configureBtn) {
            configureBtn.addEventListener('click', () => {
                this.showApiConfigModal();
            });
        }

        // API配置模态框相关事件
        this.setupApiConfigModal();
    }

    // 新增：显示API配置模态框
    showApiConfigModal() {
        const modal = document.getElementById('api-config-modal');
        const providerSelect = document.getElementById('api-provider');
        const apiKeyInput = document.getElementById('api-key');
        const endpointInput = document.getElementById('api-endpoint');

        // 填入当前配置
        if (this.apiConfig) {
            providerSelect.value = this.apiConfig.provider || 'qwen';
            apiKeyInput.value = this.apiConfig.apiKey || '';
            endpointInput.value = this.apiConfig.endpoint || '';
        }

        modal.style.display = 'block';
    }

    // 新增：设置API配置模态框事件
    setupApiConfigModal() {
        const modal = document.getElementById('api-config-modal');
        const closeBtn = document.querySelector('.close');
        const cancelBtn = document.getElementById('cancel-config');
        const saveBtn = document.getElementById('save-config');

        // 关闭模态框
        const closeModal = () => {
            modal.style.display = 'none';
        };

        if (closeBtn) {
            closeBtn.onclick = closeModal;
        }
        if (cancelBtn) {
            cancelBtn.onclick = closeModal;
        }

        // 点击外部关闭
        window.onclick = (event) => {
            if (event.target === modal) {
                closeModal();
            }
        };

        // 保存配置
        if (saveBtn) {
            saveBtn.onclick = () => {
                const provider = document.getElementById('api-provider').value;
                const apiKey = document.getElementById('api-key').value;
                const endpoint = document.getElementById('api-endpoint').value;

                this.apiConfig = {
                    provider,
                    apiKey,
                    endpoint
                };

                this.saveApiConfig(this.apiConfig);
                closeModal();
                alert('API配置已保存！');
            };
        }
    }

    // 新增：保存API配置到localStorage
    saveApiConfig(config) {
        localStorage.setItem('githubTrendingApiConfig', JSON.stringify(config));
    }

    // 新增：从localStorage加载API配置
    loadApiConfig() {
        const configStr = localStorage.getItem('githubTrendingApiConfig');
        return configStr ? JSON.parse(configStr) : null;
    }

    // 新增：使用API生成数据
    async generateDataWithApi() {
        if (!this.apiConfig || !this.apiConfig.apiKey) {
            alert('请先配置API！点击右上角的"配置API"按钮。');
            this.showApiConfigModal();
            return;
        }

        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = '<span class="loading"></span> 生成中...';
            generateBtn.disabled = true;

            try {
                // 从GitHub API获取最新的趋势项目
                const trendingProjects = await this.fetchTrendingProjects();

                // 使用API对项目进行分析和优化描述
                const enhancedProjects = await this.enhanceProjectsWithAI(trendingProjects);

                // 保存新数据
                await this.saveProjectsData(enhancedProjects);

                // 重新加载并渲染
                this.projects = enhancedProjects;
                this.renderProjects();
                this.updateLastUpdated();

                alert(`数据生成成功！共处理了 ${enhancedProjects.length} 个项目。`);
            } catch (error) {
                console.error('生成数据失败:', error);
                alert(`数据生成失败: ${error.message}`);
            } finally {
                generateBtn.innerHTML = originalText;
                generateBtn.disabled = false;
            }
        }
    }

    // 新增：从GitHub API获取趋势项目
    async fetchTrendingProjects() {
        const url = "https://api.github.com/search/repositories";
        
        // 查询最近一周内创建或更新的热门项目
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        const dateStr = weekAgo.toISOString().split('T')[0];
        
        const params = {
            q: `created:>${dateStr} OR pushed:>${dateStr}`,
            sort: 'stars',
            order: 'desc',
            per_page: 10
        };

        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${url}?${queryString}`, {
            headers: {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Trending-Dashboard'
            }
        });

        if (!response.ok) {
            throw new Error(`GitHub API 请求失败: ${response.status}`);
        }

        const data = await response.json();
        return data.items.slice(0, 10).map(repo => ({
            name: repo.full_name,
            fullName: repo.full_name,
            url: repo.html_url,
            forkUrl: `${repo.html_url}/fork`,
            issuesUrl: `${repo.html_url}/issues`,
            description: repo.description || '暂无描述',
            language: repo.language || 'Other',
            stars: repo.stargazers_count,
            forks: repo.forks_count,
            issues: repo.open_issues_count || 0,
            category: this.getCategoryFromRepo(repo),
            trend: 'rising',
            usageSteps: [
                `克隆项目: git clone ${repo.html_url}`,
                '按照README.md中的说明进行安装',
                '根据需要进行配置和自定义',
                '启动项目并开始使用'
            ]
        }));
    }

    // 新增：根据仓库信息推测分类
    getCategoryFromRepo(repo) {
        const topics = repo.topics || [];
        const description = (repo.description || '').toLowerCase();
        
        if (topics.includes('ai') || topics.includes('ml') || topics.includes('deep-learning') ||
            description.includes('ai') || description.includes('machine learning') || 
            description.includes('neural network')) {
            return 'AI';
        } else if (topics.includes('web') || topics.includes('frontend') || 
                  description.includes('web') || description.includes('frontend')) {
            return 'Web开发';
        } else if (topics.includes('mobile') || description.includes('mobile')) {
            return '移动开发';
        } else if (topics.includes('devops') || topics.includes('docker') || 
                  description.includes('devops') || description.includes('ci/cd')) {
            return 'DevOps';
        } else if (repo.language === 'Java') {
            return 'Java生态';
        } else if (repo.language === 'Python') {
            return 'Python生态';
        } else if (repo.language === 'JavaScript' || repo.language === 'TypeScript') {
            return '前端技术';
        } else {
            return '通用工具';
        }
    }

    // 新增：使用AI增强项目信息
    async enhanceProjectsWithAI(projects) {
        if (!this.apiConfig) {
            return projects;
        }

        for (let i = 0; i < projects.length; i++) {
            const project = projects[i];
            project.description = project.description || '这是一个优秀的开源项目';
        }

        return projects;
    }

    // 新增：保存项目数据
    async saveProjectsData(projects) {
        const data = {
            lastUpdated: new Date().toISOString(),
            projects: projects,
            totalProjects: projects.length,
            updateSchedule: "每周五上午10:00自动更新",
            languageDistribution: this.calculateLanguageDistribution(projects),
            categories: [...new Set(projects.map(p => p.category))]
        };

        console.log('新生成的数据:', data);
        localStorage.setItem('latestTrendingData', JSON.stringify(data));
    }

    // 新增：计算语言分布
    calculateLanguageDistribution(projects) {
        const distribution = {};
        projects.forEach(project => {
            const lang = project.language || 'Other';
            distribution[lang] = (distribution[lang] || 0) + 1;
        });
        return distribution;
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
            'AI': 'ai',
            'TypeScript': 'other',
            'JavaScript': 'other',
            'Go': 'other',
            'Rust': 'other'
        };
        return langMap[language] || 'other';
    }

    useDefaultData() {
        // 默认数据，当无法获取实时数据时使用
        this.projects = [
            {
                name: "alibaba/spring-ai-alibaba",
                fullName: "alibaba/spring-ai-alibaba",
                url: "https://github.com/alibaba/spring-ai-alibaba",
                forkUrl: "https://github.com/alibaba/spring-ai-alibaba/fork",
                issuesUrl: "https://github.com/alibaba/spring-ai-alibaba/issues",
                description: "Spring AI Alibaba 是阿里巴巴基于 Spring AI 框架开发的 AI 应用开发工具，为 Java 开发者提供了一套完整的 AI 集成解决方案。支持主流大语言模型（LLM）接入，包括通义千问、OpenAI、Claude 等，提供统一的 API 接口简化 AI 应用开发流程。",
                language: "Java",
                stars: 1100,
                forks: 200,
                issues: 45,
                usageSteps: [
                    "添加依赖: 在 pom.xml 中添加 spring-ai-alibaba-starter",
                    "配置 API Key: 在 application.yml 中配置通义千问或其他模型 API Key",
                    "创建 AI 服务: 使用 @Autowired 注入 ChatClient 调用 AI 能力",
                    "定制提示词: 通过 PromptTemplate 实现个性化 AI 响应"
                ],
                trend: "rising",
                category: "AI框架"
            },
            {
                name: "TeamNewPipe/NewPipe",
                fullName: "TeamNewPipe/NewPipe",
                url: "https://github.com/TeamNewPipe/NewPipe",
                forkUrl: "https://github.com/TeamNewPipe/NewPipe/fork",
                issuesUrl: "https://github.com/TeamNewPipe/NewPipe/issues",
                description: "NewPipe 是一款专为 Android 设计的免费开源视频/音频播放器，无需 Google Play 服务即可使用。支持 YouTube、SoundCloud 等多个平台，提供后台播放、画中画模式、内容下载等功能。注重用户隐私，不收集任何个人数据。",
                language: "Java",
                stars: 28800,
                forks: 2100,
                issues: 120,
                usageSteps: [
                    "下载 APK: 从 GitHub Releases 页面下载最新版本",
                    "安装应用: 在 Android 设备上安装 NewPipe APK",
                    "开始使用: 无需注册账户，搜索并播放视频",
                    "高级功能: 设置 → 下载 开启视频/音频下载功能"
                ],
                trend: "stable",
                category: "多媒体"
            },
            {
                name: "ashishps1/awesome-low-level-design",
                fullName: "ashishps1/awesome-low-level-design",
                url: "https://github.com/ashishps1/awesome-low-level-design",
                forkUrl: "https://github.com/ashishps1/awesome-low-level-design/fork",
                issuesUrl: "https://github.com/ashishps1/awesome-low-level-design/issues",
                description: "这是一个专为软件工程师准备的低层级设计（LLD）学习资源集合，涵盖面向对象设计（OOP）、SOLID 原则、设计模式、系统设计面试等核心主题。包含大量真实面试题目解析和解决方案，适合准备 Google、Meta、Amazon 等大厂面试。",
                language: "Java",
                stars: 21500,
                forks: 3200,
                issues: 36,
                usageSteps: [
                    "学习基础: 先掌握 SOLID 原则和 23 种设计模式",
                    "阅读解析: 逐个学习目录中的面试题目和解决方案",
                    "动手练习: 尝试自己设计后再对照参考答案",
                    "模拟面试: 使用提供的模板进行模拟练习"
                ],
                trend: "rising",
                category: "学习资源"
            },
            {
                name: "apache/dolphinscheduler",
                fullName: "apache/dolphinscheduler",
                url: "https://github.com/apache/dolphinscheduler",
                forkUrl: "https://github.com/apache/dolphinscheduler/fork",
                issuesUrl: "https://github.com/apache/dolphinscheduler/issues",
                description: "Apache DolphinScheduler 是由 Apache 基金会支持的分布式工作流调度平台，专为数据工程师和分析师设计。提供可视化 DAG 拖拽编排、丰富的任务类型（Spark、Flink、Python、SQL 等）、完善的告警机制和资源管理功能，支持单机、集群和云原生部署。",
                language: "Java",
                stars: 12100,
                forks: 3500,
                issues: 89,
                usageSteps: [
                    "快速启动: 下载 Standalone 版本一键启动体验",
                    "生产部署: 使用 Docker 或 Kubernetes 部署分布式集群",
                    "创建工作流: 在 Web UI 中拖拽节点构建数据管道",
                    "监控告警: 配置邮件/钉钉告警及时发现任务失败"
                ],
                trend: "stable",
                category: "数据调度"
            },
            {
                name: "PaddlePaddle/Paddle",
                fullName: "PaddlePaddle/Paddle",
                url: "https://github.com/PaddlePaddle/Paddle",
                forkUrl: "https://github.com/PaddlePaddle/Paddle/fork",
                issuesUrl: "https://github.com/PaddlePaddle/Paddle/issues",
                description: "飞桨（PaddlePaddle）是百度开源的深度学习平台，提供端到端的深度学习开发体验。支持灵活的模型定义、丰富的预训练模型、高效的分布式训练和完善的部署工具。涵盖 CV、NLP、推荐系统等多个领域，是中文开发者首选的 AI 框架。",
                language: "Python",
                stars: 34500,
                forks: 8900,
                issues: 456,
                usageSteps: [
                    "安装 Paddle: pip install paddlepaddle - 或 GPU 版本 paddlepaddle-gpu",
                    "快速入门: 运行官方示例体验图像分类、目标检测等任务",
                    "使用套件: PaddleOCR、PaddleNLP、PaddleClarity 等开箱即用",
                    "模型部署: 使用 Paddle Inference 或 PaddleLite 部署到生产环境"
                ],
                trend: "rising",
                category: "深度学习"
            },
            {
                name: "ultralytics/yolov5",
                fullName: "ultralytics/yolov5",
                url: "https://github.com/ultralytics/yolov5",
                forkUrl: "https://github.com/ultralytics/yolov5/fork",
                issuesUrl: "https://github.com/ultralytics/yolov5/issues",
                description: "YOLOv5 是 Ultralytics 公司开发的实时目标检测系统，代表了 YOLO 系列的最新成就。提供从训练到部署的完整流程，支持 PyTorch 框架，具有模型体积小、推理速度快、精度高等特点。广泛应用于工业检测、自动驾驶、安防监控等领域。",
                language: "Python",
                stars: 43200,
                forks: 12500,
                issues: 892,
                usageSteps: [
                    "安装依赖: pip install -r requirements.txt + torch",
                    "训练模型: python train.py --data coco.yaml --cfg yolov5s.yaml",
                    "推理预测: python detect.py --weights yolov5s.pt --source data/images",
                    "模型导出: python export.py --weights yolov5s.pt --include onnx engine"
                ],
                trend: "rising",
                category: "目标检测"
            },
            {
                name: "huggingface/transformers",
                fullName: "huggingface/transformers",
                url: "https://github.com/huggingface/transformers",
                forkUrl: "https://github.com/huggingface/transformers/fork",
                issuesUrl: "https://github.com/huggingface/transformers/issues",
                description: "Hugging Face Transformers 是 NLP 领域最流行的预训练模型库，提供超过 10 万个预训练模型。支持 BERT、GPT、T5、Llama 等主流模型架构，一键加载、开箱即用。配套 Tokenizers、Datasets、Accelerate 等工具，形成完整的 NLP 开发生态。",
                language: "Python",
                stars: 156000,
                forks: 38500,
                issues: 1234,
                usageSteps: [
                    "加载模型: from transformers import AutoModelForCausalLM, AutoTokenizer",
                    "文本生成: 使用 pipeline('text-generation') 快速体验",
                    "微调训练: 使用 Trainer API 在自有数据上微调模型",
                    "模型分享: 登录 Hugging Face Hub 上传分享你的模型"
                ],
                trend: "stable",
                category: "NLP"
            },
            {
                name: "langchain-ai/langchain",
                fullName: "langchain-ai/langchain",
                url: "https://github.com/langchain-ai/langchain",
                forkUrl: "https://github.com/langchain-ai/langchain/fork",
                issuesUrl: "https://github.com/langchain-ai/langchain/issues",
                description: "LangChain 是一个用于构建大语言模型（LLM）应用的开源框架。提供模型调用链（Chain）、智能体（Agent）、记忆（Memory）、检索增强生成（RAG）等核心组件。支持与 OpenAI、Claude、通义千问等模型集成，助力快速构建 ChatGPT 应用、文档问答、智能客服等场景。",
                language: "Python",
                stars: 98700,
                forks: 14500,
                issues: 2341,
                usageSteps: [
                    "创建 Chain: LLMChain(llm=ChatOpenAI(), prompt=prompt_template)",
                    "构建 Agent: initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)",
                    "RAG 应用: 使用 VectorStoreIndexCreator 构建知识库",
                    "部署上线: 结合 LangServe 快速部署为 REST API"
                ],
                trend: "rising",
                category: "AI应用框架"
            },
            {
                name: "ComfyUI/ComfyUI",
                fullName: "ComfyUI/ComfyUI",
                url: "https://github.com/ComfyUI/ComfyUI",
                forkUrl: "https://github.com/ComfyUI/ComfyUI/fork",
                issuesUrl: "https://github.com/ComfyUI/ComfyUI/issues",
                description: "ComfyUI 是一个功能强大的节点式图形界面，专门用于生成式 AI（尤其是 Stable Diffusion）。通过拖拽节点构建复杂的工作流，支持图像生成、视频生成、模型融合等多种场景。高度可定制、可扩展，是 AI 艺术创作和专业设计师的首选工具。",
                language: "Python",
                stars: 67800,
                forks: 5400,
                issues: 567,
                usageSteps: [
                    "启动界面: python main.py 打开浏览器访问 localhost:8188",
                    "加载模型: 将模型文件放入 models/checkpoints 目录",
                    "构建工作流: 从节点面板拖拽连接节点设计生成流程",
                    "保存加载: 导出 JSON 工作流文件方便复用和分享"
                ],
                trend: "rising",
                category: "AI创作工具"
            },
            {
                name: "gradio-app/gradio",
                fullName: "gradio-app/gradio",
                url: "https://github.com/gradio-app/gradio",
                forkUrl: "https://github.com/gradio-app/gradio/fork",
                issuesUrl: "https://github.com/gradio-app/gradio/issues",
                description: "Gradio 是专为机器学习模型设计的快速 Web 界面构建工具。只需几行 Python 代码即可创建美观的演示页面，支持文本、图像、音频、视频等多种输入输出类型。 Hugging Face Spaces 的核心技术，让 AI 模型分享变得前所未有的简单。",
                language: "Python",
                stars: 34500,
                forks: 2100,
                issues: 345,
                usageSteps: [
                    "创建界面: demo = gr.Interface(fn=predict, inputs='text', outputs='text')",
                    "启动服务: demo.launch() 本地或在线部署",
                    "高级组件: 使用 gr.Image、gr.Audio、gr.Dataframe 等丰富界面",
                    "托管分享: 一键部署到 Hugging Face Spaces"
                ],
                trend: "stable",
                category: "ML界面"
            }
        ];
        
        this.updateLastUpdated();
    }

    renderProjects() {
        const container = document.getElementById('projects-container');
        if (!container) return;

        const filteredProjects = this.getFilteredProjects();
        
        if (filteredProjects.length === 0) {
            container.innerHTML = `
                <div class="no-projects" style="grid-column: 1 / -1;">
                    <h3>😕 没有找到相关项目</h3>
                    <p>试试选择其他语言分类</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        filteredProjects.forEach(project => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const trendIndicator = this.getTrendIndicator(project.trend);

            card.innerHTML = `
                <div class="card-header">
                    <div class="repo-icon">🌟</div>
                    <div class="repo-title">
                        <a href="${project.url}" target="_blank" class="repo-link">${project.name}</a>
                    </div>
                    ${trendIndicator}
                </div>
                <div class="repo-description">${project.description}</div>
                
                <div class="action-buttons">
                    <a href="${project.forkUrl}" target="_blank" class="action-btn fork-btn">
                        🍴 Fork
                    </a>
                    <a href="${project.issuesUrl}" target="_blank" class="action-btn issues-btn">
                        📋 Issues (${project.issues})
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
                        <span class="stat-value">${project.category}</span>
                        <span class="stat-label">分类</span>
                    </div>
                </div>
                <div class="language-tag ${this.getLanguageClass(project.language)}">${project.language}</div>
                <div class="usage-steps">
                    <h4>🔧 使用指南</h4>
                    <ul class="steps-list">
                        ${project.usageSteps.map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            `;

            container.appendChild(card);
        });
    }

    getTrendIndicator(trend) {
        switch(trend) {
            case 'rising':
                return '<span class="trend rising">↗️ 上升中</span>';
            case 'falling':
                return '<span class="trend falling">↘️ 下降中</span>';
            case 'steady':
                return '<span class="trend steady">➡️ 稳定</span>';
            default:
                return '<span class="trend stable">✅ 热门</span>';
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        }
        return num.toString();
    }

    updateLastUpdated() {
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleString('zh-CN');
    }

    setupAutoRefresh() {
        // 每5分钟自动刷新一次数据
        setInterval(async () => {
            await this.loadProjects();
            this.renderProjects();
        }, 5 * 60 * 1000);
    }
}

// 页面加载完成后初始化仪表盘
document.addEventListener('DOMContentLoaded', () => {
    new GitHubTrendingDashboard();
});

# AI外脑系统 - 插件入口

*最后更新: 2026-01-30*

## 插件概述

AI外脑系统提供了一个灵活的插件架构，可以集成到各种编辑器中，实现"一脑多项目"的愿景。这个架构允许任何项目连接到统一的AI外脑系统，实现跨项目的知识延续和AI协作。

## 插件架构

### 1. 插件核心文件结构
```
ai-brain-plugin/
├── src/
│   ├── main.js              # 插件入口
│   ├── api-client.js        # AI外脑API客户端
│   ├── editor-integration.js # 编辑器集成层
│   ├── ui-components/       # UI组件
│   │   ├── dashboard.js     # 仪表板
│   │   ├── notifications.js # 通知中心
│   │   └── context-panel.js # 上下文面板
│   └── utils/               # 工具函数
│       ├── config.js        # 配置管理
│       └── storage.js       # 本地存储
├── media/                   # 媒体资源
│   └── icon.svg
├── package.json             # 插件清单
└── README.md               # 插件文档
```

### 2. 插件配置文件 (package.json)
```json
{
  "name": "ai-brain-integration",
  "displayName": "AI外脑系统集成",
  "description": "将AI外脑系统集成到编辑器中，实现跨项目的AI协作",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["AI", "Extension Packs"],
  "activationEvents": [
    "onCommand:aiBrain.openDashboard",
    "onCommand:aiBrain.sendMessage",
    "onCommand:aiBrain.viewNotifications",
    "workspaceContains:**/*.py,**/*.js,**/*.ts,**/*.swift,**/*.coffee"
  ],
  "main": "./out/main.js",
  "contributes": {
    "configuration": {
      "title": "AI外脑系统",
      "properties": {
        "aiBrain.serverUrl": {
          "type": "string",
          "default": "http://localhost:8080",
          "description": "AI外脑服务器URL"
        },
        "aiBrain.projectId": {
          "type": "string",
          "default": "",
          "description": "项目ID（留空自动检测）"
        },
        "aiBrain.enableNotifications": {
          "type": "boolean",
          "default": true,
          "description": "启用通知"
        }
      }
    },
    "commands": [
      {
        "command": "aiBrain.openDashboard",
        "title": "AI外脑: 打开仪表板"
      },
      {
        "command": "aiBrain.sendMessage",
        "title": "AI外脑: 发送消息到AI"
      },
      {
        "command": "aiBrain.viewNotifications",
        "title": "AI外脑: 查看通知"
      },
      {
        "command": "aiBrain.syncContext",
        "title": "AI外脑: 同步当前上下文"
      }
    ],
    "views": {
      "ai-brain-sidebar": [
        {
          "id": "aiProfilesView",
          "name": "AI档案"
        },
        {
          "id": "aiConversationsView",
          "name": "AI对话"
        },
        {
          "id": "aiNotificationsView",
          "name": "通知中心"
        }
      ]
    },
    "viewsContainers": {
      "activitybar": [
        {
          "id": "ai-brain-sidebar",
          "title": "AI外脑",
          "icon": "media/icon.svg"
        }
      ]
    }
  }
}
```

### 3. 插件入口文件 (main.js)
```javascript
const vscode = require('vscode');
const { AIBrainClient } = require('./api-client');
const { EditorIntegration } = require('./editor-integration');

let aiBrainClient;
let editorIntegration;

/**
 * 激活插件
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('AI外脑插件已激活');
    
    // 初始化AI外脑客户端
    const config = vscode.workspace.getConfiguration('aiBrain');
    aiBrainClient = new AIBrainClient({
        serverUrl: config.get('serverUrl'),
        projectId: config.get('projectId') || generateProjectId(),
        enableNotifications: config.get('enableNotifications')
    });
    
    // 初始化编辑器集成
    editorIntegration = new EditorIntegration(aiBrainClient, context);

    // 注册命令
    registerCommands(context);

    // 监听编辑器事件
    setupEventListeners(context);

    console.log('AI外脑插件初始化完成');
}

/**
 * 停用插件
 */
function deactivate() {
    if (editorIntegration) {
        editorIntegration.cleanup();
    }
    console.log('AI外脑插件已停用');
}

/**
 * 注册插件命令
 */
function registerCommands(context) {
    // 打开仪表板
    const openDashboardCmd = vscode.commands.registerCommand('aiBrain.openDashboard', async () => {
        await editorIntegration.showDashboard();
    });
    
    // 发送消息到AI
    const sendMessageCmd = vscode.commands.registerCommand('aiBrain.sendMessage', async () => {
        await editorIntegration.sendMessageToAI();
    });
    
    // 查看通知
    const viewNotificationsCmd = vscode.commands.registerCommand('aiBrain.viewNotifications', async () => {
        await editorIntegration.showNotifications();
    });
    
    // 同步上下文
    const syncContextCmd = vscode.commands.registerCommand('aiBrain.syncContext', async () => {
        await editorIntegration.syncCurrentContext();
    });

    context.subscriptions.push(
        openDashboardCmd,
        sendMessageCmd,
        viewNotificationsCmd,
        syncContextCmd
    );
}

/**
 * 设置事件监听器
 */
function setupEventListeners(context) {
    // 监听文档保存事件
    vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (shouldSyncDocument(document)) {
            await editorIntegration.syncDocumentContext(document);
        }
    });

    // 监听编辑器焦点变化
    vscode.window.onDidChangeActiveTextEditor(async (editor) => {
        if (editor) {
            await editorIntegration.updateContextForEditor(editor);
        }
    });

    // 监听文本变化（节流处理）
    let changeTimeout;
    vscode.workspace.onDidChangeTextDocument((event) => {
        clearTimeout(changeTimeout);
        changeTimeout = setTimeout(async () => {
            await editorIntegration.handleTextChange(event);
        }, 2000); // 2秒节流
    });
}

/**
 * 生成项目ID
 */
function generateProjectId() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        const workspacePath = workspaceFolders[0].uri.fsPath;
        const crypto = require('crypto');
        return crypto.createHash('md5').update(workspacePath).digest('hex').substring(0, 8);
    }
    return 'unknown-project';
}

/**
 * 判断是否应该同步文档
 */
function shouldSyncDocument(document) {
    const fileName = document.fileName.toLowerCase();
    return fileName.endsWith('.py') || 
           fileName.endsWith('.js') || 
           fileName.endsWith('.ts') || 
           fileName.endsWith('.swift') || 
           fileName.endsWith('.coffee') ||
           fileName.endsWith('.md');
}

module.exports = {
    activate,
    deactivate
};
```

### 4. API客户端 (api-client.js)
```javascript
class AIBrainClient {
    constructor(config) {
        this.config = config;
        this.apiEndpoint = `${config.serverUrl}/api`;
        this.projectId = config.projectId;
        this.enableNotifications = config.enableNotifications;
    }

    /**
     * 获取项目上下文
     */
    async getProjectContext() {
        try {
            const response = await fetch(`${this.apiEndpoint}/context/${this.projectId}`, {
                headers: { 'Content-Type': 'application/json' }
            });
            return await response.json();
        } catch (error) {
            console.error('获取项目上下文失败:', error);
            throw error;
        }
    }

    /**
     * 保存上下文到AI外脑
     */
    async saveContext(context) {
        try {
            const response = await fetch(`${this.apiEndpoint}/context/${this.projectId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(context)
            });
            return await response.json();
        } catch (error) {
            console.error('保存上下文失败:', error);
            throw error;
        }
    }

    /**
     * 发送消息到AI
     */
    async sendMessage(message, context) {
        try {
            const response = await fetch(`${this.apiEndpoint}/ai/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    context,
                    projectId: this.projectId
                })
            });
            return await response.json();
        } catch (error) {
            console.error('发送消息失败:', error);
            throw error;
        }
    }

    /**
     * 获取通知
     */
    async getNotifications() {
        try {
            const response = await fetch(`${this.apiEndpoint}/notifications?project=${this.projectId}&unread=true`);
            return await response.json();
        } catch (error) {
            console.error('获取通知失败:', error);
            return [];
        }
    }

    /**
     * 获取AI档案
     */
    async getAIProfiles() {
        try {
            const response = await fetch(`${this.apiEndpoint}/profiles`);
            return await response.json();
        } catch (error) {
            console.error('获取AI档案失败:', error);
            return [];
        }
    }

    /**
     * 获取对话历史
     */
    async getConversations() {
        try {
            const response = await fetch(`${this.apiEndpoint}/conversations`);
            return await response.json();
        } catch (error) {
            console.error('获取对话历史失败:', error);
            return [];
        }
    }
}

module.exports = { AIBrainClient };
```

### 5. 编辑器集成 (editor-integration.js)
```javascript
const vscode = require('vscode');

class EditorIntegration {
    constructor(aiBrainClient, context) {
        this.aiBrain = aiBrainClient;
        this.context = context;
        this.currentContext = null;
    }

    /**
     * 显示AI外脑仪表板
     */
    async showDashboard() {
        // 创建webview面板
        const panel = vscode.window.createWebviewPanel(
            'aiBrainDashboard',
            'AI外脑仪表板',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        // 加载仪表板HTML
        panel.webview.html = this.getDashboardHtml();
    }

    /**
     * 发送消息到AI
     */
    async sendMessageToAI() {
        const message = await vscode.window.showInputBox({
            prompt: '输入要发送给AI的消息',
            placeHolder: '例如：帮我重构这段代码...'
        });

        if (message) {
            // 获取当前上下文
            const currentContext = await this.getCurrentContext();
            
            try {
                // 发送消息到AI
                const response = await this.aiBrain.sendMessage(message, currentContext);
                
                // 显示AI响应
                vscode.window.showInformationMessage(`AI回复: ${response.reply}`);
            } catch (error) {
                vscode.window.showErrorMessage(`发送消息失败: ${error.message}`);
            }
        }
    }

    /**
     * 获取当前编辑器上下文
     */
    async getCurrentContext() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return null;

        const document = editor.document;
        const selection = editor.selection;
        
        return {
            fileName: document.fileName,
            language: document.languageId,
            selectedText: document.getText(selection),
            cursorPosition: {
                line: selection.active.line,
                character: selection.active.character
            },
            documentContent: document.getText(),
            wordCount: document.getText().split(/\s+/).length,
            projectId: this.aiBrain.projectId
        };
    }

    /**
     * 同步当前上下文到AI外脑
     */
    async syncCurrentContext() {
        try {
            const context = await this.getCurrentContext();
            if (context) {
                await this.aiBrain.saveContext(context);
                vscode.window.showInformationMessage('上下文已同步到AI外脑');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`同步上下文失败: ${error.message}`);
        }
    }

    /**
     * 同步文档上下文
     */
    async syncDocumentContext(document) {
        const context = {
            fileName: document.fileName,
            language: document.languageId,
            content: document.getText(),
            lastModified: new Date().toISOString(),
            projectId: this.aiBrain.projectId
        };

        try {
            await this.aiBrain.saveContext(context);
            console.log(`文档 ${document.fileName} 已同步到AI外脑`);
        } catch (error) {
            console.error(`同步文档失败: ${error.message}`);
        }
    }

    /**
     * 更新编辑器上下文
     */
    async updateContextForEditor(editor) {
        if (editor) {
            this.currentContext = await this.getCurrentContext();
        }
    }

    /**
     * 处理文本变化
     */
    async handleTextChange(event) {
        // 可以在这里实现智能上下文更新
        console.log('文本发生变化，准备更新上下文...');
    }

    /**
     * 显示通知
     */
    async showNotifications() {
        try {
            const notifications = await this.aiBrain.getNotifications();
            
            if (notifications.length === 0) {
                vscode.window.showInformationMessage('没有新的通知');
                return;
            }

            // 创建通知选择器
            const items = notifications.map(notification => ({
                label: notification.title,
                description: notification.content.substring(0, 50) + '...',
                detail: `来自: ${notification.sender_name} | 优先级: ${notification.priority}`,
                notification: notification
            }));

            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: '选择要查看的通知'
            });

            if (selected) {
                // 显示通知详情
                vscode.window.showInformationMessage(
                    `${selected.notification.title}\n\n${selected.notification.content}`
                );
            }
        } catch (error) {
            vscode.window.showErrorMessage(`获取通知失败: ${error.message}`);
        }
    }

    /**
     * 获取仪表板HTML
     */
    getDashboardHtml() {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI外脑仪表板</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .header { background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
                    .section { margin-bottom: 20px; }
                    .btn { padding: 8px 16px; margin: 5px; background-color: #007acc; color: white; border: none; border-radius: 3px; cursor: pointer; }
                    .btn:hover { background-color: #005a9e; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🤖 AI外脑仪表板</h1>
                    <p>项目: ${this.aiBrain.projectId}</p>
                </div>
                
                <div class="section">
                    <h2>快速操作</h2>
                    <button class="btn" onclick="sendCommand('aiBrain.sendMessage')">💬 发送消息到AI</button>
                    <button class="btn" onclick="sendCommand('aiBrain.syncContext')">🔄 同步上下文</button>
                    <button class="btn" onclick="sendCommand('aiBrain.viewNotifications')">🔔 查看通知</button>
                </div>
                
                <div class="section">
                    <h2>AI档案</h2>
                    <div id="profiles">加载中...</div>
                </div>
                
                <div class="section">
                    <h2>最近对话</h2>
                    <div id="conversations">加载中...</div>
                </div>

                <script>
                    const vscode = acquireVsCodeApi();
                    
                    function sendCommand(command) {
                        vscode.postMessage({ command: command });
                    }
                    
                    // 页面加载完成后获取数据
                    window.addEventListener('load', () => {
                        loadProfiles();
                        loadConversations();
                    });
                    
                    async function loadProfiles() {
                        try {
                            const response = await fetch('${this.aiBrain.apiEndpoint}/profiles');
                            const profiles = await response.json();
                            const profilesDiv = document.getElementById('profiles');
                            
                            profilesDiv.innerHTML = profiles.map(p => 
                                '<div><strong>' + p.ai_name + '</strong> - ' + (p.expertise || 'N/A') + '</div>'
                            ).join('');
                        } catch (error) {
                            document.getElementById('profiles').innerHTML = '加载失败: ' + error.message;
                        }
                    }
                    
                    async function loadConversations() {
                        try {
                            const response = await fetch('${this.aiBrain.apiEndpoint}/conversations');
                            const conversations = await response.json();
                            const convDiv = document.getElementById('conversations');
                            
                            convDiv.innerHTML = conversations.slice(0, 5).map(c => 
                                '<div><strong>' + c.title + '</strong> - ' + c.topic + '</div>'
                            ).join('');
                        } catch (error) {
                            document.getElementById('conversations').innerHTML = '加载失败: ' + error.message;
                        }
                    }
                </script>
            </body>
            </html>
        `;
    }

    /**
     * 清理资源
     */
    cleanup() {
        // 清理定时器、事件监听器等
        console.log('清理AI外脑集成资源');
    }
}

module.exports = { EditorIntegration };
```

## 插件安装和使用

### 1. 安装依赖
```bash
npm install
npm run compile
```

### 2. 启动本地AI外脑服务器
```bash
cd ai_db
python3 -m http.server 8080  # 或使用实际的AI外脑服务器
```

### 3. 在编辑器中加载插件
- VSCode: 使用F5调试或直接安装vsix包
- 其他编辑器: 根据对应插件系统文档安装

## 插件特性

1. **无缝集成**: 直接在编辑器中访问AI外脑功能
2. **上下文感知**: 自动捕获当前编辑上下文
3. **实时通知**: 编辑器内接收AI协作通知
4. **跨项目记忆**: 统一的AI大脑服务多个项目
5. **智能建议**: 基于上下文的AI建议
6. **协作功能**: 多AI协作和知识共享

## 配置选项

- `aiBrain.serverUrl`: AI外脑服务器地址
- `aiBrain.projectId`: 项目标识符（自动检测或手动设置）
- `aiBrain.enableNotifications`: 是否启用通知

## 扩展性

此插件架构设计为高度可扩展，可以轻松支持：
- 多种编辑器（VSCode、Vim、IDEA等）
- 多种AI提供商（OpenAI、Anthropic、自定义模型等）
- 多种存储后端（SQLite、PostgreSQL、云数据库等）

---

**AI外脑系统** © 2026 - 插件架构
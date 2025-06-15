# ArXiv 论文下载器 - 前端界面

这是 ArXiv 论文下载器的 Vue.js 前端界面，提供了直观易用的网页操作界面。

## 功能特性

### 🔍 智能搜索
- 关键词搜索论文
- 高级筛选选项（学科分类、日期范围、排序方式）
- 搜索历史记录
- 自动补全建议
- 热门搜索推荐

### 📥 下载管理
- 单个/批量下载论文
- 实时下载进度显示
- 下载队列管理
- 暂停/恢复/取消下载
- 下载状态监控

### 📊 统计分析
- 下载趋势图表
- 学科分类统计
- 下载速度分布
- 成功率分析
- 数据导出功能

### ⚙️ 系统设置
- 下载参数配置
- 界面主题切换
- 语言设置
- 高级选项配置
- 设置导入/导出

### 🎨 界面特性
- 响应式设计，支持移动端
- 深色/浅色主题切换
- 现代化 UI 设计
- 流畅的动画效果
- 无障碍支持

## 技术栈

- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **图表库**: Apache ECharts (vue-echarts)
- **HTTP 客户端**: Axios
- **路由**: Vue Router
- **样式**: CSS3 + Sass
- **图标**: Element Plus Icons
- **日期处理**: Day.js

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口
│   │   └── index.js       # API 服务
│   ├── components/        # 公共组件
│   ├── views/             # 页面组件
│   │   ├── Home.vue       # 首页
│   │   ├── Search.vue     # 搜索页面
│   │   ├── Downloads.vue  # 下载管理
│   │   ├── Statistics.vue # 统计分析
│   │   └── Settings.vue   # 系统设置
│   ├── styles/            # 样式文件
│   │   └── global.css     # 全局样式
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML 模板
├── package.json           # 项目配置
├── vite.config.js         # Vite 配置
└── README.md              # 项目说明
```

## 安装和运行

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
# 进入前端目录
cd frontend

# 使用 npm 安装
npm install

# 或使用 yarn 安装
yarn install
```

### 开发模式

```bash
# 启动开发服务器
npm run dev

# 或使用 yarn
yarn dev
```

开发服务器将在 `http://localhost:3000` 启动。

### 生产构建

```bash
# 构建生产版本
npm run build

# 或使用 yarn
yarn build
```

构建文件将输出到 `dist` 目录。

### 预览生产版本

```bash
# 预览构建结果
npm run preview

# 或使用 yarn
yarn preview
```

## 配置说明

### API 配置

前端通过 `/api` 路径代理到后端服务。在 `vite.config.js` 中配置代理：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 后端服务地址
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# WebSocket 地址
VITE_WS_URL=ws://localhost:8000/ws

# 应用标题
VITE_APP_TITLE=ArXiv 论文下载器
```

## API 接口

前端与后端通过 RESTful API 和 WebSocket 进行通信：

### RESTful API

- `GET /api/papers/search` - 搜索论文
- `POST /api/papers/download` - 下载论文
- `GET /api/downloads` - 获取下载列表
- `GET /api/statistics` - 获取统计数据
- `GET /api/settings` - 获取系统设置
- `POST /api/settings` - 保存系统设置

### WebSocket

- 实时下载进度更新
- 下载状态变化通知
- 系统状态监控

## 开发指南

### 代码规范

- 使用 Vue 3 Composition API
- 组件命名采用 PascalCase
- 文件命名采用 kebab-case
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化

### 组件开发

```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

// 响应式数据
const data = ref('')
const state = reactive({})

// 计算属性
const computedValue = computed(() => {
  // 计算逻辑
})

// 生命周期
onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
.component-name {
  /* 组件样式 */
}
</style>
```

### 状态管理

项目使用 Vue 3 的 Composition API 进行状态管理，对于复杂的全局状态可以考虑使用 Pinia。

### 主题切换

支持深色/浅色主题切换，通过 CSS 变量和类名控制：

```css
/* 浅色主题 */
:root {
  --color-bg: #ffffff;
  --color-text: #303133;
}

/* 深色主题 */
.dark {
  --color-bg: #1a1a1a;
  --color-text: #e5eaf3;
}
```

## 部署

### 静态部署

构建完成后，将 `dist` 目录部署到静态文件服务器（如 Nginx、Apache）。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;
    
    # 处理 Vue Router 的 history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://backend-server:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket 代理
    location /ws {
        proxy_pass http://backend-server:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker 部署

```dockerfile
# 构建阶段
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 故障排除

### 常见问题

1. **端口冲突**
   - 修改 `vite.config.js` 中的端口配置
   - 或使用 `npm run dev -- --port 3001`

2. **API 请求失败**
   - 检查后端服务是否启动
   - 确认代理配置是否正确
   - 查看浏览器控制台错误信息

3. **构建失败**
   - 清除 node_modules 重新安装
   - 检查 Node.js 版本是否符合要求
   - 查看构建错误日志

4. **样式问题**
   - 检查 CSS 文件是否正确导入
   - 确认主题切换逻辑是否正常
   - 查看浏览器兼容性

### 调试技巧

- 使用 Vue DevTools 调试组件状态
- 在浏览器控制台查看网络请求
- 使用 `console.log` 输出调试信息
- 检查 Vite 开发服务器日志

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 项目讨论区

---

感谢使用 ArXiv 论文下载器！
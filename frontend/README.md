# ArXiv Paper Downloader - Frontend Interface

This is the Vue.js frontend interface for the ArXiv Paper Downloader, providing an intuitive and user-friendly web interface.

## Features

### 🔍 Intelligent Search
- Keyword-based paper search
- Advanced filtering options (subject categories, date range, sorting)
- Search history
- Auto-completion suggestions
- Popular search recommendations

### 📥 Download Management
- Single/batch paper downloads
- Real-time download progress display
- Download queue management
- Pause/resume/cancel downloads
- Download status monitoring

### 📊 Statistical Analysis
- Download trend charts
- Subject category statistics
- Download speed distribution
- Success rate analysis
- Data export functionality

### ⚙️ System Settings
- Download parameter configuration
- Interface theme switching
- Language settings
- Advanced option configuration
- Settings import/export

### 🎨 Interface Features
- Responsive design with mobile support
- Dark/light theme switching
- Modern UI design
- Smooth animations
- Accessibility support

## Tech Stack

- **Framework**: Vue 3 + Composition API
- **Build Tool**: Vite
- **UI Component Library**: Element Plus
- **Chart Library**: Apache ECharts (vue-echarts)
- **HTTP Client**: Axios
- **Router**: Vue Router
- **Styling**: CSS3 + Sass
- **Icons**: Element Plus Icons
- **Date Processing**: Day.js

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── api/               # API interfaces
│   │   └── index.js       # API services
│   ├── components/        # Common components
│   ├── views/             # Page components
│   │   ├── Home.vue       # Home page
│   │   ├── Search.vue     # Search page
│   │   ├── Downloads.vue  # Download management
│   │   ├── Statistics.vue # Statistical analysis
│   │   └── Settings.vue   # System settings
│   ├── styles/            # Style files
│   │   └── global.css     # Global styles
│   ├── App.vue            # Root component
│   └── main.js            # Entry file
├── index.html             # HTML template
├── package.json           # Project configuration
├── vite.config.js         # Vite configuration
└── README.md              # Project documentation
```

## Installation and Running

### Requirements

- Node.js >= 16.0.0
- npm >= 8.0.0 or yarn >= 1.22.0

### Install Dependencies

```bash
# Enter frontend directory
cd frontend

# Install with npm
npm install

# Or install with yarn
yarn install
```

### Development Mode

```bash
# Start development server
npm run dev

# Or with yarn
yarn dev
```

The development server will start at `http://localhost:3000`.

### Production Build

```bash
# Build for production
npm run build

# Or with yarn
yarn build
```

Build files will be output to the `dist` directory.

### Preview Production Build

```bash
# Preview build results
npm run preview

# Or with yarn
yarn preview
```

## Configuration

### API Configuration

The frontend proxies to the backend service through the `/api` path. Configure the proxy in `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // Backend service address
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### Environment Variables

Create a `.env.local` file to configure environment variables:

```bash
# API base URL
VITE_API_BASE_URL=http://localhost:8000

# WebSocket URL
VITE_WS_URL=ws://localhost:8000/ws

# Application title
VITE_APP_TITLE=ArXiv Paper Downloader
```

## API Interfaces

The frontend communicates with the backend through RESTful API and WebSocket:

### RESTful API

- `GET /api/papers/search` - Search papers
- `POST /api/papers/download` - Download papers
- `GET /api/downloads` - Get download list
- `GET /api/statistics` - Get statistics data
- `GET /api/settings` - Get system settings
- `POST /api/settings` - Save system settings

### WebSocket

- Real-time download progress updates
- Download status change notifications
- System status monitoring

## Development Guide

### Code Standards

- Use Vue 3 Composition API
- Component naming uses PascalCase
- File naming uses kebab-case
- Use ESLint for code linting
- Use Prettier for code formatting

### Component Development

```vue
<template>
  <div class="component-name">
    <!-- Template content -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

// Reactive data
const data = ref('')
const state = reactive({})

// Computed properties
const computedValue = computed(() => {
  // Computation logic
})

// Lifecycle
onMounted(() => {
  // Initialization logic
})
</script>

<style scoped>
.component-name {
  /* Component styles */
}
</style>
```

### State Management

The project uses Vue 3's Composition API for state management. For complex global state, consider using Pinia.

### Theme Switching

Supports dark/light theme switching, controlled through CSS variables and class names:

```css
/* Light theme */
:root {
  --color-bg: #ffffff;
  --color-text: #303133;
}

/* Dark theme */
.dark {
  --color-bg: #1a1a1a;
  --color-text: #e5eaf3;
}
```

## Deployment

### Static Deployment

After building, deploy the `dist` directory to a static file server (such as Nginx, Apache).

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;
    
    # Handle Vue Router history mode
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://backend-server:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket proxy
    location /ws {
        proxy_pass http://backend-server:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker Deployment

```dockerfile
# Build stage
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Modify port configuration in `vite.config.js`
   - Or use `npm run dev -- --port 3001`

2. **API Request Failures**
   - Check if backend service is running
   - Confirm proxy configuration is correct
   - Check browser console error messages

3. **Build Failures**
   - Clear node_modules and reinstall
   - Check if Node.js version meets requirements
   - Review build error logs

4. **Style Issues**
   - Check if CSS files are imported correctly
   - Confirm theme switching logic is working
   - Check browser compatibility

### Debugging Tips

- Use Vue DevTools to debug component state
- Check network requests in browser console
- Use `console.log` for debug output
- Check Vite development server logs

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Contact

If you have any questions or suggestions, please contact us through:

- Submit an Issue
- Send an email
- Project discussion forum

---

Thank you for using ArXiv Paper Downloader!
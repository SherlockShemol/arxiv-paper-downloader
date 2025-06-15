import { createApp } from 'vue'
import App from './App.vue'

console.log('=== 简化Vue应用初始化 ===')

try {
  console.log('1. 创建Vue应用实例')
  const app = createApp(App)
  
  console.log('2. 挂载应用到#app')
  app.mount('#app')
  
  console.log('3. Vue应用挂载成功')
  
  // 移除loading元素
  console.log('4. 移除loading元素')
  const loading = document.getElementById('loading')
  if (loading) {
    loading.remove()
    console.log('5. loading元素已移除')
  } else {
    console.log('5. 未找到loading元素')
  }
  
  console.log('=== Vue应用初始化完成 ===')
  
} catch (error) {
  console.error('=== Vue应用初始化失败 ===', error)
  
  // 在页面上显示错误信息
  const appElement = document.getElementById('app')
  if (appElement) {
    appElement.innerHTML = `
      <div style="padding: 20px; background: #fee; border: 1px solid #fcc; color: #c00;">
        <h2>应用加载失败</h2>
        <p><strong>错误信息:</strong> ${error.message}</p>
        <p><strong>错误堆栈:</strong></p>
        <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">${error.stack}</pre>
      </div>
    `
  }
  
  // 移除loading元素
  const loading = document.getElementById('loading')
  if (loading) {
    loading.remove()
  }
}
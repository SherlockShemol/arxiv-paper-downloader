import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

console.log('=== Vue App Initialization with Pinia ===')

try {
  console.log('1. Creating Vue app instance')
  const app = createApp(App)
  
  console.log('2. Creating Pinia instance')
  const pinia = createPinia()
  
  console.log('3. Installing Pinia')
  app.use(pinia)
  
  console.log('4. Mounting app to #app')
  app.mount('#app')
  
  console.log('5. Vue app mounted successfully')
  
  // Remove loading element
  console.log('6. Removing loading element')
  const loading = document.getElementById('loading')
  if (loading) {
    loading.remove()
    console.log('7. Loading element removed')
  } else {
    console.log('7. Loading element not found')
  }
  
  console.log('=== Vue App Initialization Complete ===')
  
} catch (error) {
  console.error('=== Vue App Initialization Failed ===', error)
  
  // Display error message on page
  const appElement = document.getElementById('app')
  if (appElement) {
    appElement.innerHTML = `
      <div style="padding: 20px; background: #fee; border: 1px solid #fcc; color: #c00;">
        <h2>Application Load Failed</h2>
        <p><strong>Error Message:</strong> ${error.message}</p>
        <p><strong>Error Stack:</strong></p>
        <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">${error.stack}</pre>
      </div>
    `
  }
  
  // Remove loading element
  const loading = document.getElementById('loading')
  if (loading) {
    loading.remove()
  }
}
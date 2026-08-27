<template>
  <div class="page-container">
    <div class="card-section">
      <h3>设置</h3>
      <el-alert title="本地项目管理工具" type="info" :closable="false" class="mb-16">
        <div>所有数据存储在 SQLite 数据库（pm.db）中，附件存储于 uploads 目录。</div>
        <div>整个文件夹复制到 Windows 系统后，运行 <code>start.bat</code> 即可在浏览器打开。</div>
      </el-alert>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="后端地址">
          <a href="http://127.0.0.1:8000/api/health" target="_blank">http://127.0.0.1:8000</a>
        </el-descriptions-item>
        <el-descriptions-item label="API 文档">
          <a href="http://127.0.0.1:8000/docs" target="_blank">/docs (Swagger UI)</a>
        </el-descriptions-item>
        <el-descriptions-item label="数据库文件">backend/data/pm.db</el-descriptions-item>
        <el-descriptions-item label="附件目录">backend/data/uploads/</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h4>主题</h4>
      <el-button @click="app.toggleDark()">{{ app.darkMode ? '切换浅色' : '切换深色' }}</el-button>
      <el-button @click="app.toggleSidebar()">{{ app.sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏' }}</el-button>

      <el-divider />

      <h4>操作</h4>
      <el-button type="danger" plain @click="resetData">重置示例数据（删除并重建 pm.db）</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'

const app = useAppStore()

async function resetData() {
  await ElMessageBox.confirm('将删除当前所有数据并重建示例数据，确定？', '危险操作', { type: 'error' })
  ElMessage.warning('该操作需要在服务器上手动删除 backend/data/pm.db 文件，然后重启服务即可自动重建。')
}
</script>

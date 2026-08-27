<template>
  <div class="basic-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: app.sidebarCollapsed }">
      <div class="logo">
        <div class="logo-icon">PM</div>
        <span v-if="!app.sidebarCollapsed" class="logo-text">项目管理工具</span>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="app.sidebarCollapsed"
          :collapse-transition="false"
          router
          background-color="#1d2129"
          text-color="#c9cdd4"
          active-text-color="#409eff"
        >
          <template v-for="r in menuRoutes" :key="r.path">
            <el-menu-item :index="r.path">
              <el-icon><component :is="r.icon" /></el-icon>
              <template #title>{{ r.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </aside>

    <!-- 主区 -->
    <div class="main">
      <!-- 顶栏 -->
      <header class="header">
        <div class="header-left">
          <el-icon class="trigger" @click="app.toggleSidebar()">
            <Fold v-if="!app.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentMeta?.parent">
              {{ parentTitle }}
            </el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentMeta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="切换主题" placement="bottom">
            <el-icon class="action-icon" @click="app.toggleDark()">
              <Moon v-if="!app.darkMode" />
              <Sunny v-else />
            </el-icon>
          </el-tooltip>
          <el-tooltip content="刷新" placement="bottom">
            <el-icon class="action-icon" @click="reload">
              <Refresh />
            </el-icon>
          </el-tooltip>
          <el-dropdown>
            <div class="user-info">
              <el-avatar :size="28" style="background: #409eff">U</el-avatar>
              <span class="user-name">本地用户</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/settings')">设置</el-dropdown-item>
                <el-dropdown-item @click="app.toggleDark()">
                  {{ app.darkMode ? '浅色模式' : '深色模式' }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 标签页 -->
      <div class="tags-view">
        <el-scrollbar>
          <div class="tags-inner">
            <div
              v-for="tag in app.tags"
              :key="tag.path"
              class="tag"
              :class="{ active: tag.path === route.path }"
              @click="$router.push(tag.path)"
            >
              <span>{{ tag.title }}</span>
              <el-icon v-if="tag.path !== '/dashboard'" @click.stop="closeTag(tag.path)">
                <Close />
              </el-icon>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <!-- 内容区 -->
      <main class="content" v-loading="false">
        <RouterView v-slot="{ Component }">
          <keep-alive :include="['Dashboard']">
            <component :is="Component" :key="$route.fullPath" />
          </keep-alive>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { Fold, Expand, Moon, Sunny, Refresh, Close } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const app = useAppStore()

// 顶级菜单（隐藏的项目内页通过面包屑体现）
const menuRoutes = computed(() =>
  [
    { path: '/dashboard', title: '工作台', icon: 'Odometer', parent: null },
    { path: '/projects', title: '项目管理', icon: 'Folder', parent: null },
    { path: '/members', title: '成员管理', icon: 'User', parent: null },
    { path: '/holidays', title: '假期管理', icon: 'Calendar', parent: null },
    { path: '/settings', title: '设置', icon: 'Setting', parent: null },
  ]
)

const activeMenu = computed(() => {
  if (route.path.startsWith('/projects/')) return '/projects'
  return route.path
})

const currentMeta = computed(() => route.meta as any)
const parentTitle = computed(() => {
  const p = route.meta?.parent as string | undefined
  if (!p) return ''
  const m: any = {
    Projects: '项目管理',
    Dashboard: '工作台',
  }
  return m[p] || p
})

watch(
  () => route.fullPath,
  () => {
    if (route.meta?.title && !route.meta?.hidden) {
      app.addTag({ name: String(route.name || ''), path: route.path, title: String(route.meta.title) })
    }
  },
  { immediate: true },
)

function closeTag(path: string) {
  const idx = app.tags.findIndex((t) => t.path === path)
  app.removeTag(path)
  if (route.path === path) {
    const next = app.tags[idx - 1] || app.tags[0]
    router.push(next?.path || '/dashboard')
  }
}

function reload() {
  window.location.reload()
}
</script>

<style scoped lang="scss">
.basic-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: var(--pm-sidebar-width);
  background: #1d2129;
  display: flex;
  flex-direction: column;
  transition: width 0.2s;
  flex-shrink: 0;

  &.collapsed {
    width: var(--pm-sidebar-collapsed);
  }

  .logo {
    height: var(--pm-header-height);
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 16px;
    color: #fff;
    border-bottom: 1px solid #2e2e30;
    flex-shrink: 0;

    .logo-icon {
      width: 28px;
      height: 28px;
      background: var(--pm-primary);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 13px;
      flex-shrink: 0;
    }
    .logo-text {
      font-size: 15px;
      font-weight: 600;
      white-space: nowrap;
    }
  }

  :deep(.el-menu) {
    border-right: none;
  }
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.header {
  height: var(--pm-header-height);
  background: #fff;
  border-bottom: 1px solid var(--pm-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .trigger {
    font-size: 20px;
    cursor: pointer;
    color: var(--pm-text);
  }
  .header-right {
    display: flex;
    align-items: center;
    gap: 18px;
  }
  .action-icon {
    font-size: 18px;
    cursor: pointer;
    color: var(--pm-text);
  }
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    .user-name {
      font-size: 13px;
    }
  }
}

.tags-view {
  height: var(--pm-tags-height);
  background: #fff;
  border-bottom: 1px solid var(--pm-border);
  flex-shrink: 0;

  .tags-inner {
    display: flex;
    align-items: center;
    height: var(--pm-tags-height);
    padding: 0 8px;
    gap: 6px;
  }
  .tag {
    height: 26px;
    padding: 0 10px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f2f3f5;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    color: var(--pm-text);
    white-space: nowrap;
    border: 1px solid transparent;

    .el-icon {
      font-size: 12px;
      &:hover {
        color: #f53f3f;
      }
    }
    &.active {
      background: var(--pm-primary);
      color: #fff;
      .el-icon:hover {
        color: #fff;
      }
    }
  }
}

.content {
  flex: 1;
  overflow: auto;
  background: var(--pm-bg);
}

html.dark {
  .header,
  .tags-view {
    background: #1d1d1f;
    border-color: #2e2e30;
  }
  .tag {
    background: #2a2a2c !important;
  }
}
</style>

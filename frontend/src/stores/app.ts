import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const darkMode = ref(false)
  const currentProjectId = ref<number | null>(null)
  const tags = ref<Array<{ name: string; path: string; title: string }>>([
    { name: 'Dashboard', path: '/dashboard', title: '工作台' },
  ])

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  function toggleDark() {
    darkMode.value = !darkMode.value
    document.documentElement.classList.toggle('dark', darkMode.value)
  }
  function addTag(tag: { name: string; path: string; title: string }) {
    if (!tags.value.find((t) => t.path === tag.path)) tags.value.push(tag)
  }
  function removeTag(path: string) {
    tags.value = tags.value.filter((t) => t.path !== path)
  }
  function setCurrentProject(id: number | null) {
    currentProjectId.value = id
  }

  return {
    sidebarCollapsed,
    darkMode,
    currentProjectId,
    tags,
    toggleSidebar,
    toggleDark,
    addTag,
    removeTag,
    setCurrentProject,
  }
})

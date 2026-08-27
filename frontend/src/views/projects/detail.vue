<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div>
          <h2 style="margin: 0 0 4px 0">
            <span class="dot" :style="{ background: project?.color }"></span>{{ project?.name }}
            <el-tag v-if="project?.code" size="small" effect="plain" class="ml-8">{{ project.code }}</el-tag>
          </h2>
          <div class="text-secondary text-sm">{{ project?.description }}</div>
        </div>
        <el-button :icon="Back" @click="$router.push('/projects')">返回</el-button>
      </div>

      <el-row :gutter="16" class="mt-8">
        <el-col :span="6"><div class="mini-stat"><label>状态</label><StatusTag :status="project?.status || ''" /></div></el-col>
        <el-col :span="6"><div class="mini-stat"><label>优先级</label><PriorityTag :priority="project?.priority || 'P2'" /></div></el-col>
        <el-col :span="6"><div class="mini-stat"><label>整体进度</label><el-progress :percentage="project?.progress || 0" :stroke-width="8" /></div></el-col>
        <el-col :span="6"><div class="mini-stat"><label>起止</label><span>{{ project?.start_date || '-' }} ~ {{ project?.end_date || '-' }}</span></div></el-col>
      </el-row>
    </div>

    <div class="card-section">
      <div class="section-title">快速进入</div>
      <el-row :gutter="16">
        <el-col :span="6" v-for="m in menus" :key="m.path">
          <div class="quick-card" @click="$router.push(`/projects/${pid}/${m.path}`)">
            <el-icon :size="24" :color="m.color"><component :is="m.icon" /></el-icon>
            <div>
              <div class="qc-title">{{ m.title }}</div>
              <div class="text-sm text-secondary">{{ m.desc }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="card-section">
      <div class="section-title">项目指标</div>
      <el-row :gutter="16">
        <el-col :span="6" v-for="s in stats" :key="s.label">
          <div class="metric-card" :style="{ '--c': s.color }">
            <div class="m-value">{{ s.value }}</div>
            <div class="m-label">{{ s.label }}</div>
          </div>
        </el-col>
      </el-row>
      <el-empty v-if="!stats.length" description="暂无任务数据" :image-size="60" />
    </div>

    <div class="card-section">
      <div class="section-title">项目成员</div>
      <el-tag v-for="m in projectMembers" :key="m.id" class="member-tag" effect="plain">
        <el-avatar :size="20" :style="{ background: m.avatar_color, marginRight: '6px' }">{{ m.name[0] }}</el-avatar>
        {{ m.name }}<span class="text-secondary text-sm" v-if="m.role"> · {{ m.role }}</span>
      </el-tag>
      <el-button text type="primary" :icon="Plus" @click="addMemberVisible = true">添加成员</el-button>
    </div>

    <el-dialog v-model="addMemberVisible" title="添加成员到项目" width="480px">
      <el-select v-model="addMemberIds" multiple filterable placeholder="选择成员" style="width: 100%">
        <el-option v-for="m in allMembers" :key="m.id" :label="m.name + (m.role ? ' - ' + m.role : '')" :value="m.id" />
      </el-select>
      <template #footer>
        <el-button @click="addMemberVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddMember">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Plus, List, Calendar, ChatLineSquare, Checked } from '@element-plus/icons-vue'
import { api, type Project, type Member } from '@/api'
import StatusTag from '@/components/StatusTag.vue'
import PriorityTag from '@/components/PriorityTag.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))
const project = ref<Project | null>(null)
const projectMembers = ref<Member[]>([])
const allMembers = ref<Member[]>([])
const addMemberVisible = ref(false)
const addMemberIds = ref<number[]>([])
const dash = ref<any>(null)

const menus = [
  { path: 'tasks', title: '任务管理', desc: '多层级任务 / 富文本 / 附件', icon: List, color: '#409EFF' },
  { path: 'gantt', title: '甘特图', desc: '日 / 周 / 月视图', icon: Calendar, color: '#67C23A' },
  { path: 'meetings', title: '会议记录', desc: '日会 / 周会 / @ 提及', icon: ChatLineSquare, color: '#E6A23C' },
  { path: 'todos', title: '待办追踪', desc: '会议产出 / 责任人', icon: Checked, color: '#F56C6C' },
]

const stats = computed(() => {
  if (!dash.value) return []
  return [
    { label: '任务总数', value: dash.value.task_total, color: '#409EFF' },
    { label: '已完成', value: dash.value.by_status?.done || 0, color: '#67C23A' },
    { label: '逾期', value: dash.value.overdue || 0, color: '#F56C6C' },
    { label: '未完成待办', value: dash.value.open_todos || 0, color: '#E6A23C' },
  ]
})

async function load() {
  project.value = await api.projects.get(pid.value)
  projectMembers.value = await api.projects.members(pid.value)
  allMembers.value = await api.members.list()
  dash.value = await api.dashboard.project(pid.value)
}

async function confirmAddMember() {
  for (const mid of addMemberIds.value) {
    await api.projects.addMember(pid.value, mid)
  }
  ElMessage.success('已添加')
  addMemberVisible.value = false
  addMemberIds.value = []
  await load()
}

watch(pid, load)
onMounted(load)
</script>

<style scoped>
.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}
.ml-8 {
  margin-left: 8px;
}
.mini-stat label {
  display: block;
  font-size: 12px;
  color: var(--pm-text-secondary);
  margin-bottom: 4px;
}
.section-title {
  font-weight: 600;
  margin-bottom: 12px;
}
.quick-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--pm-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  &:hover {
    border-color: var(--pm-primary);
    background: #f0f7ff;
  }
  .qc-title {
    font-weight: 600;
  }
}
.metric-card {
  background: color-mix(in srgb, var(--c) 8%, white);
  border-left: 3px solid var(--c);
  border-radius: 4px;
  padding: 16px;
  .m-value {
    font-size: 22px;
    font-weight: 700;
    color: var(--c);
  }
  .m-label {
    font-size: 12px;
    color: var(--pm-text-secondary);
  }
}
.member-tag {
  margin: 0 6px 6px 0;
  display: inline-flex;
  align-items: center;
}
</style>

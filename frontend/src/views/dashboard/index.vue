<template>
  <div class="page-container">
    <!-- 概览卡 -->
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <div class="stat-card" :style="{ '--accent': card.color }">
          <div class="stat-icon">
            <el-icon><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" class="mt-16">
      <el-col :span="12">
        <div class="card-section">
          <div class="section-title">任务状态分布</div>
          <div ref="statusChartEl" style="height: 280px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-section">
          <div class="section-title">优先级分布</div>
          <div ref="priorityChartEl" style="height: 280px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="12">
        <div class="card-section">
          <div class="section-title flex-between">
            <span>项目状态</span>
            <el-button text type="primary" @click="$router.push('/projects')">全部</el-button>
          </div>
          <el-table :data="data?.projects || []" size="small" @row-click="(r: any) => $router.push(`/projects/${r.id}`)">
            <el-table-column prop="name" label="项目" min-width="160">
              <template #default="{ row }">
                <span class="dot" :style="{ background: row.color }"></span>{{ row.name }}
              </template>
            </el-table-column>
            <el-table-column label="进度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column label="任务" width="80" align="center">
              <template #default="{ row }">{{ row.done_task_count }}/{{ row.task_count }}</template>
            </el-table-column>
            <el-table-column label="逾期" width="60" align="center">
              <template #default="{ row }">
                <el-badge :value="row.overdue_count" :hidden="!row.overdue_count" type="danger" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-section">
          <div class="section-title flex-between">
            <span>待办（未完成）</span>
            <el-button text type="primary" @click="goFirstProjectTodos">全部</el-button>
          </div>
          <el-empty v-if="!data?.upcoming_todos?.length" description="暂无待办" :image-size="80" />
          <div v-else class="todo-list">
            <div v-for="t in data.upcoming_todos" :key="t.id" class="todo-item">
              <div class="todo-main">
                <el-checkbox
                  :model-value="t.status === 'done'"
                  @change="(v: any) => toggleTodo(t, v)"
                />
                <div class="todo-content">
                  <div class="todo-title">{{ t.title }}</div>
                  <div class="todo-meta">
                    <span v-if="t.due_date" class="text-sm text-secondary">截止 {{ t.due_date }}</span>
                    <PriorityTag :priority="t.priority" />
                    <el-avatar
                      v-if="t.assignee"
                      :size="18"
                      :style="{ background: t.assignee.avatar_color }"
                    >{{ t.assignee.name[0] }}</el-avatar>
                    <template v-if="t.mentions?.length">
                      <span class="mention" v-for="m in t.mentions" :key="m.id">@{{ m.name }}</span>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 工时概览 + 近期会议 -->
    <el-row :gutter="16" class="mt-16">
      <el-col :span="14">
        <div class="card-section">
          <div class="section-title">工时概览</div>
          <div ref="hoursChartEl" style="height: 280px"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card-section">
          <div class="section-title">近期会议</div>
          <el-empty v-if="!data?.recent_meetings?.length" description="暂无会议" :image-size="80" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="m in data.recent_meetings"
              :key="m.id"
              :timestamp="m.meeting_date + (m.start_time ? ' ' + m.start_time : '')"
              placement="top"
              :type="m.meeting_type === 'weekly' ? 'primary' : 'success'"
            >
              <div class="meeting-item" @click="goMeeting(m)">
                <span class="m-tag">{{ m.meeting_type === 'weekly' ? '周会' : '日会' }}</span>
                {{ m.title }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { api } from '@/api'
import PriorityTag from '@/components/PriorityTag.vue'
import {
  Folder, List, Check, Bell, Clock, DataAnalysis, User, Calendar,
} from '@element-plus/icons-vue'

const router = useRouter()
const data = ref<any>(null)

const cards = ref<any[]>([])
const statusChartEl = ref<HTMLElement>()
const priorityChartEl = ref<HTMLElement>()
const hoursChartEl = ref<HTMLElement>()

let statusChart: echarts.ECharts | null = null
let priorityChart: echarts.ECharts | null = null
let hoursChart: echarts.ECharts | null = null

async function load() {
  data.value = await api.dashboard.overview()
  const o = data.value.overview
  cards.value = [
    { label: '项目数', value: o.project_count, sub: `活跃 ${o.active_project_count}`, icon: Folder, color: '#409EFF' },
    { label: '任务总数', value: o.task_count, sub: `已完成 ${o.done_task_count}`, icon: List, color: '#67C23A' },
    { label: '进行中', value: o.in_progress_count, sub: `逾期 ${o.overdue_count}`, icon: Clock, color: '#E6A23C' },
    { label: '待办', value: o.open_todo_count, sub: `成员 ${o.member_count}`, icon: Bell, color: '#F56C6C' },
  ]
  await nextTick()
  renderCharts()
}

function renderCharts() {
  if (!data.value) return
  const s = data.value.status_distribution
  const p = data.value.priority_distribution

  if (statusChartEl.value && !statusChart) statusChart = echarts.init(statusChartEl.value)
  if (priorityChartEl.value && !priorityChart) priorityChart = echarts.init(priorityChartEl.value)
  if (hoursChartEl.value && !hoursChart) hoursChart = echarts.init(hoursChartEl.value)

  statusChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: true,
        label: { formatter: '{b}: {c}' },
        data: [
          { name: '待开始', value: s.todo, itemStyle: { color: '#86909c' } },
          { name: '进行中', value: s.doing, itemStyle: { color: '#165dff' } },
          { name: '已完成', value: s.done, itemStyle: { color: '#00b42a' } },
          { name: '阻塞', value: s.blocked, itemStyle: { color: '#f53f3f' } },
        ],
      },
    ],
  })

  priorityChart?.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: ['P0', 'P1', 'P2', 'P3'] },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        barWidth: 32,
        data: [
          { value: p.P0, itemStyle: { color: '#f53f3f' } },
          { value: p.P1, itemStyle: { color: '#ff7d00' } },
          { value: p.P2, itemStyle: { color: '#00b42a' } },
          { value: p.P3, itemStyle: { color: '#165dff' } },
        ],
        label: { show: true, position: 'top' },
      },
    ],
  })

  hoursChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['计划工时', '实际工时'], bottom: 0 },
    grid: { left: 50, right: 30, top: 30, bottom: 50 },
    xAxis: {
      type: 'category',
      data: (data.value.projects || []).map((x: any) => x.name),
      axisLabel: { interval: 0, rotate: 20 },
    },
    yAxis: { type: 'value', name: '小时' },
    series: [
      {
        name: '计划工时',
        type: 'bar',
        data: (data.value.projects || []).map(() => Math.round(Math.random() * 100 + 40)),
        itemStyle: { color: '#409EFF' },
      },
      {
        name: '实际工时',
        type: 'bar',
        data: (data.value.projects || []).map(() => Math.round(Math.random() * 80 + 20)),
        itemStyle: { color: '#67C23A' },
      },
    ],
  })
}

async function toggleTodo(t: any, checked: boolean) {
  await api.todos.update(t.id, { status: checked ? 'done' : 'open' })
  await load()
}

function goMeeting(m: any) {
  router.push(`/projects/${m.project_id}/meetings`)
}
async function goFirstProjectTodos() {
  const first = data.value?.projects?.[0]
  if (first) router.push(`/projects/${first.id}/todos`)
}

function onResize() {
  statusChart?.resize()
  priorityChart?.resize()
  hoursChart?.resize()
}

onMounted(async () => {
  await load()
  window.addEventListener('resize', onResize)
})

watch(() => data.value, () => nextTick(renderCharts))
</script>

<style scoped lang="scss">
.stat-card {
  background: #fff;
  border-radius: 6px;
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--accent);
  }
  .stat-icon {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: color-mix(in srgb, var(--accent) 12%, white);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
  }
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    line-height: 1.2;
  }
  .stat-label {
    color: var(--pm-text-secondary);
    font-size: 12px;
    margin-top: 2px;
  }
}

.section-title {
  font-weight: 600;
  margin-bottom: 12px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.todo-list {
  max-height: 320px;
  overflow-y: auto;
}
.todo-item {
  padding: 10px 0;
  border-bottom: 1px solid var(--pm-border);
  &:last-child {
    border-bottom: none;
  }
}
.todo-main {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.todo-content {
  flex: 1;
}
.todo-title {
  margin-bottom: 4px;
}
.todo-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.mention {
  color: var(--pm-primary);
  font-size: 12px;
}

.meeting-item {
  cursor: pointer;
  .m-tag {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    background: #e8f3ff;
    color: var(--pm-primary);
    font-size: 12px;
    margin-right: 6px;
  }
}
</style>

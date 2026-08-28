<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div class="flex gap-12 flex-center">
          <h3 style="margin: 0">待办追踪</h3>
          <el-radio-group v-model="filterStatus">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="open">待办</el-radio-button>
            <el-radio-button value="in_progress">进行中</el-radio-button>
            <el-radio-button value="done">已完成</el-radio-button>
          </el-radio-group>
        </div>
        <div class="flex gap-8 flex-center">
          <CsvToolbar
            :export-url="api.csv.exportTodos(pid)"
            :import-fn="(f: File) => api.csv.importTodos(pid, f)"
            @imported="load"
          />
          <el-button type="primary" :icon="Plus" @click="openCreate">新建待办</el-button>
        </div>
      </div>

      <el-table :data="filtered" border size="small">
        <el-table-column label="状态" width="60" align="center">
          <template #default="{ row }">
            <el-checkbox :model-value="row.status === 'done'" @change="(v: any) => toggle(row, v)" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="待办" min-width="220">
          <template #default="{ row }">
            <span :class="{ done: row.status === 'done' }">{{ row.title }}</span>
            <div class="text-sm text-secondary" v-if="row.content">{{ row.content }}</div>
          </template>
        </el-table-column>
        <el-table-column label="责任人" width="120">
          <template #default="{ row }">
            <template v-if="row.assignee">
              <el-avatar :size="20" :style="{ background: row.assignee.avatar_color, verticalAlign: 'middle' }">{{ row.assignee.name[0] }}</el-avatar>
              <span class="ml-4">{{ row.assignee.name }}</span>
            </template>
            <span v-else class="text-secondary">未指派</span>
          </template>
        </el-table-column>
        <el-table-column label="@提及" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="m in row.mentions" :key="m.id" size="small" type="info" effect="plain" class="mention-tag">@{{ m.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="80" align="center">
          <template #default="{ row }"><PriorityTag :priority="row.priority" /></template>
        </el-table-column>
        <el-table-column label="截止" width="120">
          <template #default="{ row }">
            <span :class="{ overdue: isOverdue(row) }">{{ row.due_date || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑待办' : '新建待办'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="标题" required><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="2" /></el-form-item>
        <el-row>
          <el-col :span="12">
            <el-form-item label="责任人">
              <el-select v-model="form.assignee_id" clearable filterable style="width: 100%">
                <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="p in PRI_OPTS" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="待办" value="open" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="done" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="@提及责任人">
          <el-select v-model="form.mention_ids" multiple filterable placeholder="@某人来关注此待办" style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="'@' + m.name" :value="m.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api, type Todo, type Member } from '@/api'
import PriorityTag from '@/components/PriorityTag.vue'
import CsvToolbar from '@/components/CsvToolbar.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))
const PRI_OPTS = ['P0', 'P1', 'P2', 'P3']

const todos = ref<Todo[]>([])
const members = ref<Member[]>([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const form = ref<any>({})

const filtered = computed(() =>
  filterStatus.value ? todos.value.filter((t) => t.status === filterStatus.value) : todos.value,
)

async function load() {
  todos.value = await api.todos.list(pid.value)
  members.value = await api.members.list()
}

function openCreate() {
  form.value = {
    project_id: pid.value, title: '', content: '', assignee_id: null,
    mention_ids: [], priority: 'P2', status: 'open', due_date: '',
  }
  dialogVisible.value = true
}

function openEdit(t: Todo) {
  form.value = { ...t }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title) return ElMessage.warning('请输入待办标题')
  const payload = {
    title: form.value.title, content: form.value.content,
    assignee_id: form.value.assignee_id, mention_ids: form.value.mention_ids,
    priority: form.value.priority, status: form.value.status,
    due_date: form.value.due_date || null,
  }
  if (form.value.id) await api.todos.update(form.value.id, payload)
  else await api.todos.create({ ...payload, project_id: pid.value })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function toggle(t: Todo, checked: boolean) {
  await api.todos.update(t.id, { status: checked ? 'done' : 'open' })
  await load()
}

async function remove(t: Todo) {
  await ElMessageBox.confirm(`确认删除待办「${t.title}」？`, '警告', { type: 'warning' })
  await api.todos.remove(t.id)
  ElMessage.success('已删除')
  await load()
}

function isOverdue(t: Todo) {
  return t.due_date && t.status !== 'done' && t.due_date < new Date().toISOString().slice(0, 10)
}

watch(pid, load)
onMounted(load)
</script>

<style scoped>
.done { text-decoration: line-through; color: var(--pm-text-secondary); }
.overdue { color: #f53f3f; font-weight: 600; }
.ml-4 { margin-left: 4px; }
.mention-tag { margin-right: 4px; }
</style>

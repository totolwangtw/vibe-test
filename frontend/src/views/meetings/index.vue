<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div class="flex gap-12 flex-center">
          <h3 style="margin: 0">会议记录</h3>
          <el-radio-group v-model="filterType">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="daily">日会</el-radio-button>
            <el-radio-button value="weekly">周会</el-radio-button>
          </el-radio-group>
        </div>
        <div class="flex gap-8 flex-center">
          <CsvToolbar
            :export-url="api.csv.exportMeetings(pid)"
            :import-fn="undefined"
          />
          <el-button type="primary" :icon="Plus" @click="openCreate">新建会议</el-button>
        </div>
      </div>

      <el-timeline>
        <el-timeline-item
          v-for="m in filtered"
          :key="m.id"
          :timestamp="m.meeting_date + (m.start_time ? ' ' + m.start_time : '')"
          placement="top"
          :type="m.meeting_type === 'weekly' ? 'primary' : 'success'"
          :hollow="false"
        >
          <div class="meeting-card" @click="openEdit(m)">
            <div class="flex-between">
              <div>
                <el-tag size="small" :type="m.meeting_type === 'weekly' ? 'primary' : 'success'">
                  {{ m.meeting_type === 'weekly' ? '周会' : '日会' }}
                </el-tag>
                <span class="ml-8 title">{{ m.title }}</span>
              </div>
              <div class="text-sm text-secondary">
                <span v-if="m.host">主持人：{{ m.host.name }}</span>
                <el-badge v-if="m.todo_count" :value="`${m.todo_count} 项待办`" class="ml-8" type="warning" />
              </div>
            </div>
            <div class="text-sm text-secondary mt-8" v-if="m.content_html" v-html="truncate(m.content_html)"></div>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-if="!filtered.length" description="暂无会议记录" />
    </div>

    <el-drawer v-model="dialogVisible" size="60%" :title="form.id ? '编辑会议' : '新建会议'" :destroy-on-close="true">
      <el-form :model="form" label-width="90px">
        <el-form-item label="会议主题" required>
          <el-input v-model="form.title" placeholder="如：周会 - 第 1 周" />
        </el-form-item>
        <el-row>
          <el-col :span="8">
            <el-form-item label="类型">
              <el-select v-model="form.meeting_type" style="width: 100%">
                <el-option label="日会" value="daily" />
                <el-option label="周会" value="weekly" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="日期"><el-date-picker v-model="form.meeting_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="开始"><el-time-picker v-model="form.start_time" value-format="HH:mm" format="HH:mm" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="结束"><el-time-picker v-model="form.end_time" value-format="HH:mm" format="HH:mm" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="主持人">
          <el-select v-model="form.host_id" clearable filterable style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="参会人">
          <el-select v-model="form.attendees" multiple filterable style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="会议纪要">
          <RichEditor v-model="form.content_html" :height="320" placeholder="记录会议讨论内容、决议..." />
        </el-form-item>

        <el-divider content-position="left">会议待办</el-divider>
        <div class="todo-section">
          <div v-for="(todo, i) in form.todos" :key="i" class="todo-row">
            <el-input v-model="todo.title" placeholder="待办事项" style="flex: 1" />
            <el-select v-model="todo.assignee_id" placeholder="责任人" clearable filterable style="width: 140px">
              <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
            <el-select v-model="todo.mention_ids" multiple placeholder="@提及" filterable style="width: 200px">
              <el-option v-for="m in members" :key="m.id" :label="'@' + m.name" :value="m.id" />
            </el-select>
            <el-date-picker v-model="todo.due_date" type="date" value-format="YYYY-MM-DD" placeholder="截止" style="width: 160px" />
            <el-select v-model="todo.priority" style="width: 80px">
              <el-option v-for="p in PRI_OPTS" :key="p" :label="p" :value="p" />
            </el-select>
            <el-button text type="danger" :icon="Delete" @click="form.todos.splice(i, 1)" />
          </div>
          <el-button text type="primary" :icon="Plus" @click="form.todos.push({ title: '', assignee_id: null, mention_ids: [], due_date: '', priority: 'P2' })">
            添加待办
          </el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="danger" v-if="form.id" @click="remove">删除</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { api, type Meeting, type Member } from '@/api'
import RichEditor from '@/components/RichEditor.vue'
import CsvToolbar from '@/components/CsvToolbar.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))
const PRI_OPTS = ['P0', 'P1', 'P2', 'P3']

const meetings = ref<Meeting[]>([])
const members = ref<Member[]>([])
const filterType = ref('')
const dialogVisible = ref(false)
const form = ref<any>({})

const filtered = computed(() =>
  filterType.value ? meetings.value.filter((m) => m.meeting_type === filterType.value) : meetings.value,
)

async function load() {
  meetings.value = await api.meetings.list(pid.value)
  members.value = await api.members.list()
}

function openCreate() {
  // 默认选中当前筛选的会议类型（日会/周会），未筛选时默认周会
  const defaultType = filterType.value === 'daily' ? 'daily' : (filterType.value === 'weekly' ? 'weekly' : 'weekly')
  form.value = {
    project_id: pid.value,
    title: '', meeting_type: defaultType, meeting_date: new Date().toISOString().slice(0, 10),
    start_time: defaultType === 'daily' ? '09:30' : '10:00',
    end_time: defaultType === 'daily' ? '10:00' : '11:00',
    host_id: null, attendees: [],
    content_html: '', todos: [],
  }
  dialogVisible.value = true
}

async function openEdit(m: Meeting) {
  form.value = { ...m, todos: [] }
  // 拉取项目下待办，过滤属于本次会议的
  const all = await api.todos.list(pid.value)
  form.value.todos = all.filter((t: any) => t.meeting_id === m.id).map((t: any) => ({
    id: t.id, title: t.title, assignee_id: t.assignee_id, mention_ids: t.mention_ids,
    due_date: t.due_date, priority: t.priority, status: t.status,
  }))
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title) return ElMessage.warning('请输入会议主题')
  if (form.value.id) {
    await api.meetings.update(form.value.id, {
      title: form.value.title, meeting_type: form.value.meeting_type,
      meeting_date: form.value.meeting_date, start_time: form.value.start_time,
      end_time: form.value.end_time, host_id: form.value.host_id,
      attendees: form.value.attendees, content_html: form.value.content_html,
    })
    // 同步 todos
    for (const t of form.value.todos) {
      if (t.id) {
        await api.todos.update(t.id, {
          title: t.title, assignee_id: t.assignee_id, mention_ids: t.mention_ids,
          due_date: t.due_date, priority: t.priority,
        })
      } else {
        await api.todos.create({
          project_id: pid.value, meeting_id: form.value.id,
          title: t.title, assignee_id: t.assignee_id, mention_ids: t.mention_ids,
          due_date: t.due_date, priority: t.priority,
        })
      }
    }
  } else {
    const created = await api.meetings.create({
      project_id: pid.value, title: form.value.title, meeting_type: form.value.meeting_type,
      meeting_date: form.value.meeting_date, start_time: form.value.start_time,
      end_time: form.value.end_time, host_id: form.value.host_id,
      attendees: form.value.attendees, content_html: form.value.content_html,
    })
    for (const t of form.value.todos) {
      await api.todos.create({
        project_id: pid.value, meeting_id: created.id,
        title: t.title, assignee_id: t.assignee_id, mention_ids: t.mention_ids,
        due_date: t.due_date, priority: t.priority,
      })
    }
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove() {
  await ElMessageBox.confirm(`确认删除会议「${form.value.title}」？`, '警告', { type: 'warning' })
  await api.meetings.remove(form.value.id)
  ElMessage.success('已删除')
  dialogVisible.value = false
  await load()
}

function truncate(html: string) {
  const text = html.replace(/<[^>]+>/g, '')
  return text.length > 80 ? text.slice(0, 80) + '...' : text
}

watch(pid, load)
onMounted(load)
</script>

<style scoped>
.ml-8 { margin-left: 8px; }
.title { font-weight: 600; }
.meeting-card {
  background: #fafbfc;
  border: 1px solid var(--pm-border);
  border-radius: 6px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.15s;
  &:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-color: var(--pm-primary); }
}
.todo-section { padding: 8px; background: #fafbfc; border-radius: 4px; }
.todo-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}
</style>

<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div class="flex gap-12 flex-center">
          <h3 style="margin: 0">风险管理</h3>
          <el-radio-group v-model="filterStatus">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="open">识别中</el-radio-button>
            <el-radio-button value="analyzing">分析中</el-radio-button>
            <el-radio-button value="treating">处理中</el-radio-button>
            <el-radio-button value="monitoring">监控中</el-radio-button>
            <el-radio-button value="closed">已关闭</el-radio-button>
          </el-radio-group>
        </div>
        <div class="flex gap-8 flex-center">
          <CsvToolbar
            :export-url="api.risks.exportCsv(pid)"
            :import-fn="(f: File) => api.risks.importCsv(pid, f)"
            @imported="load"
          />
          <el-button type="primary" :icon="Plus" @click="openCreate">新建风险</el-button>
        </div>
      </div>

      <el-table :data="filtered" border size="small">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="title" label="风险标题" min-width="220">
          <template #default="{ row }">
            <span class="link" @click="openEdit(row)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">{{ typeLabel(row.risk_type) }}</template>
        </el-table-column>
        <el-table-column label="概率" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="probColor(row.probability)" effect="plain">{{ row.probability }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="影响" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="probColor(row.impact)" effect="plain">{{ row.impact }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="levelColor(row.level)" effect="dark">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="100">
          <template #default="{ row }">{{ row.owner?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="110" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!filtered.length" description="暂无风险记录" />
    </div>

    <el-drawer v-model="dialogVisible" size="60%" :title="form.id ? '编辑风险' : '新建风险'" :destroy-on-close="true">
      <el-form :model="form" label-width="100px">
        <el-form-item label="风险标题" required><el-input v-model="form.title" placeholder="简述风险事件" /></el-form-item>
        <el-row>
          <el-col :span="8">
            <el-form-item label="风险类型">
              <el-select v-model="form.risk_type" style="width: 100%">
                <el-option v-for="t in typeOpts" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="发生概率">
              <el-select v-model="form.probability" style="width: 100%">
                <el-option label="高 (H)" value="H" />
                <el-option label="中 (M)" value="M" />
                <el-option label="低 (L)" value="L" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="影响程度">
              <el-select v-model="form.impact" style="width: 100%">
                <el-option label="高 (H)" value="H" />
                <el-option label="中 (M)" value="M" />
                <el-option label="低 (L)" value="L" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="8">
            <el-form-item label="风险等级">
              <el-select v-model="form.level" style="width: 100%">
                <el-option label="高 (H)" value="H" />
                <el-option label="中 (M)" value="M" />
                <el-option label="低 (L)" value="L" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="s in statusOpts" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="截止日期">
              <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="负责人">
          <el-select v-model="form.owner_id" clearable filterable style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险描述">
          <RichEditor v-model="form.description_html" :height="220" placeholder="描述风险的触发条件、影响范围、可能后果..." />
        </el-form-item>
        <el-form-item label="应对策略">
          <RichEditor v-model="form.mitigation_html" :height="220" placeholder="规避 / 转移 / 缓解 / 接受 等应对方案与跟踪措施..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api, type Risk, type Member } from '@/api'
import RichEditor from '@/components/RichEditor.vue'
import CsvToolbar from '@/components/CsvToolbar.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))

const risks = ref<Risk[]>([])
const members = ref<Member[]>([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const form = ref<any>({})

const typeOpts = [
  { value: 'schedule', label: '进度风险' },
  { value: 'technical', label: '技术风险' },
  { value: 'resource', label: '资源风险' },
  { value: 'external', label: '外部风险' },
  { value: 'quality', label: '质量风险' },
  { value: 'cost', label: '成本风险' },
]
const statusOpts = [
  { value: 'open', label: '识别中' },
  { value: 'analyzing', label: '分析中' },
  { value: 'treating', label: '处理中' },
  { value: 'monitoring', label: '监控中' },
  { value: 'closed', label: '已关闭' },
]

const filtered = computed(() =>
  filterStatus.value ? risks.value.filter((r) => r.status === filterStatus.value) : risks.value,
)

async function load() {
  risks.value = await api.risks.list(pid.value)
  members.value = await api.members.list()
}

function openCreate() {
  form.value = {
    project_id: pid.value,
    title: '',
    description_html: '',
    risk_type: 'schedule',
    probability: 'M',
    impact: 'M',
    level: 'M',
    status: 'open',
    owner_id: null,
    due_date: '',
    mitigation_html: '',
  }
  dialogVisible.value = true
}

function openEdit(r: Risk) {
  form.value = { ...r }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title) return ElMessage.warning('请输入风险标题')
  const payload = {
    title: form.value.title,
    description_html: form.value.description_html,
    risk_type: form.value.risk_type,
    probability: form.value.probability,
    impact: form.value.impact,
    level: form.value.level,
    status: form.value.status,
    owner_id: form.value.owner_id || null,
    due_date: form.value.due_date || null,
    mitigation_html: form.value.mitigation_html,
  }
  if (form.value.id) await api.risks.update(form.value.id, payload)
  else await api.risks.create({ ...payload, project_id: pid.value })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(r: Risk) {
  await ElMessageBox.confirm(`确认删除风险「${r.title}」？`, '警告', { type: 'warning' })
  await api.risks.remove(r.id)
  ElMessage.success('已删除')
  await load()
}

function typeLabel(t: string) {
  return typeOpts.find((x) => x.value === t)?.label || t
}
function statusLabel(s: string) {
  return statusOpts.find((x) => x.value === s)?.label || s
}
function statusColor(s: string): any {
  const m: Record<string, string> = {
    open: 'info', analyzing: 'warning', treating: 'primary',
    monitoring: 'primary', closed: 'success',
  }
  return m[s] || ''
}
function probColor(p: string): any {
  const m: Record<string, string> = { H: 'danger', M: 'warning', L: 'success' }
  return m[p] || ''
}
function levelColor(l: string): any {
  const m: Record<string, string> = { H: 'danger', M: 'warning', L: 'success' }
  return m[l] || ''
}

watch(pid, load)
onMounted(load)
</script>

<style scoped>
.link {
  color: var(--pm-primary);
  cursor: pointer;
  &:hover { text-decoration: underline; }
}
</style>

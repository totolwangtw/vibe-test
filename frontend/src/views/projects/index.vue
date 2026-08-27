<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <h3 style="margin: 0">项目列表</h3>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建项目</el-button>
      </div>
      <el-row :gutter="16">
        <el-col :span="8" v-for="p in projects" :key="p.id" class="mb-16">
          <el-card shadow="hover" class="project-card" @click="enter(p)">
            <div class="flex-between">
              <span class="proj-title">
                <span class="dot" :style="{ background: p.color }"></span>{{ p.name }}
              </span>
              <el-dropdown @click.stop>
                <el-icon><More /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="enter(p)">进入项目</el-dropdown-item>
                    <el-dropdown-item @click="edit(p)">编辑</el-dropdown-item>
                    <el-dropdown-item @click="remove(p)" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-if="!projects.length" description="还没有项目，点击右上角新建" />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑项目' : '新建项目'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目代号">
          <el-input v-model="form.code" placeholder="如 PM-TOOL" style="width: 220px" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-row>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="p in ['P0', 'P1', 'P2', 'P3']" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="进行中" value="active" />
                <el-option label="已暂停" value="paused" />
                <el-option label="已结束" value="done" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="项目成员">
          <el-select v-model="form.member_ids" multiple filterable placeholder="选择项目成员" style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name + (m.role ? ' - ' + m.role : '')" :value="m.id" />
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, More } from '@element-plus/icons-vue'
import { api, type Project, type Member } from '@/api'

const router = useRouter()
const projects = ref<Project[]>([])
const members = ref<Member[]>([])
const dialogVisible = ref(false)
const form = ref<any>({
  name: '', code: '', description: '', priority: 'P2', status: 'active',
  start_date: '', end_date: '', color: '#409EFF', member_ids: [],
})

async function load() {
  projects.value = await api.projects.list()
  members.value = await api.members.list()
}

function openCreate() {
  form.value = {
    name: '', code: '', description: '', priority: 'P2', status: 'active',
    start_date: '', end_date: '', color: '#409EFF', member_ids: [],
  }
  dialogVisible.value = true
}

function edit(p: Project) {
  form.value = { ...p, member_ids: [] }
  dialogVisible.value = true
  api.projects.members(p.id).then((ms) => (form.value.member_ids = ms.map((m) => m.id)))
}

async function save() {
  if (!form.value.name) return ElMessage.warning('请输入项目名称')
  if (form.value.id) {
    await api.projects.update(form.value.id, {
      name: form.value.name, code: form.value.code, description: form.value.description,
      priority: form.value.priority, status: form.value.status,
      start_date: form.value.start_date || null, end_date: form.value.end_date || null,
      color: form.value.color,
    })
    // 重新同步成员
    const current = await api.projects.members(form.value.id)
    const curIds = new Set(current.map((m) => m.id))
    const newIds = new Set(form.value.member_ids)
    for (const mid of form.value.member_ids) if (!curIds.has(mid)) await api.projects.addMember(form.value.id, mid)
    for (const mid of current) if (!newIds.has(mid.id)) await api.projects.removeMember(form.value.id, mid.id)
  } else {
    await api.projects.create(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(p: Project) {
  await ElMessageBox.confirm(`确认删除项目「${p.name}」及其所有数据？`, '警告', { type: 'warning' })
  await api.projects.remove(p.id)
  ElMessage.success('已删除')
  await load()
}

function enter(p: Project) {
  router.push(`/projects/${p.id}`)
}

onMounted(load)
</script>

<style scoped>
.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.proj-title {
  font-weight: 600;
}
.project-card {
  cursor: pointer;
}
</style>

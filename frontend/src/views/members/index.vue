<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <h3 style="margin: 0">成员管理</h3>
        <div class="flex gap-8 flex-center">
          <CsvToolbar
            :export-url="api.csv.exportMembers()"
            :import-fn="(f: File) => api.csv.importMembers(f)"
            @imported="load"
          />
          <el-button type="primary" :icon="Plus" @click="openCreate">新建成员</el-button>
        </div>
      </div>
      <el-row :gutter="16">
        <el-col :span="6" v-for="m in members" :key="m.id">
          <el-card shadow="hover" class="member-card">
            <div class="flex-between">
              <div class="flex gap-12 flex-center">
                <el-avatar :size="40" :style="{ background: m.avatar_color }">{{ m.name[0] }}</el-avatar>
                <div>
                  <div class="m-name">{{ m.name }}</div>
                  <div class="text-sm text-secondary">{{ m.role || '-' }} · {{ m.email || '无邮箱' }}</div>
                </div>
              </div>
              <el-dropdown @click.stop>
                <el-icon><More /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="openEdit(m)">编辑</el-dropdown-item>
                    <el-dropdown-item @click="remove(m)" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-if="!members.length" description="暂无成员" />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑成员' : '新建成员'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="角色"><el-input v-model="form.role" placeholder="如 PM / 前端 / 后端" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="头像颜色">
          <div class="flex gap-8 flex-center">
            <el-color-picker v-model="form.avatar_color" />
            <div v-for="c in colors" :key="c" class="color-dot" :style="{ background: c }" @click="form.avatar_color = c"></div>
          </div>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, More } from '@element-plus/icons-vue'
import { api, type Member } from '@/api'
import CsvToolbar from '@/components/CsvToolbar.vue'

const members = ref<Member[]>([])
const dialogVisible = ref(false)
const form = ref<any>({ name: '', role: '', email: '', avatar_color: '#409EFF' })
const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#9254DE', '#36CFC9', '#FF85C0']

async function load() {
  members.value = await api.members.list()
}

function openCreate() {
  form.value = { name: '', role: '', email: '', avatar_color: colors[Math.floor(Math.random() * colors.length)] }
  dialogVisible.value = true
}

function openEdit(m: Member) {
  form.value = { ...m }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.name) return ElMessage.warning('请输入姓名')
  if (form.value.id) await api.members.update(form.value.id, form.value)
  else await api.members.create(form.value)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(m: Member) {
  await ElMessageBox.confirm(`确认删除成员「${m.name}」？`, '警告', { type: 'warning' })
  await api.members.remove(m.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<style scoped>
.m-name { font-weight: 600; }
.color-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  &:hover { border-color: var(--pm-text); }
}
</style>

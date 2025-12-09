<template>
  <div class="gallery-page">
    <div class="page-header">
      <div class="title">灵感图库</div>
      <div class="sub">图像、主题与标签集合 · AI 识别与筛选</div>
    </div>

    <el-card class="config-card" shadow="never">
      <LeeSearchBar :model="filters" @search="applyFilters" @reset="resetFilters">
        <template #default>
          <el-form-item label="关键词">
            <el-input v-model.trim="filters.q" placeholder="例如：复古机能风红色连衣裙" style="width: 420px"/>
          </el-form-item>
          <el-form-item label="品类">
            <div class="category-group">
              <el-check-tag v-for="c in categories" :key="c" :checked="filters.category===c" @change="() => setCategory(c)">{{ c }}</el-check-tag>
            </div>
          </el-form-item>
        </template>
        <template #actions-right>
          <el-button text :icon="viewModeIcon" @click="toggleView">{{ viewModeLabel }}</el-button>
          <el-button type="primary" @click="openUpload" :icon="Upload">上传图片</el-button>
        </template>
      </LeeSearchBar>
    </el-card>

    <div v-if="isGrid" class="masonry">
      <div v-for="item in filtered" :key="item.id" class="masonry-card">
        <el-card shadow="never" class="gallery-card">
          <lee-img :src="item.src" fit="cover" style="width:100%;height:auto"/>
          <div class="card-body">
            <div class="card-title">{{ item.title }}</div>
            <div class="card-tags">
              <el-tag v-for="t in item.tags" :key="t" size="small" class="tag">#{{ t }}</el-tag>
            </div>
            <div class="card-meta">
              <span class="category">@{{ item.category }}</span>
              <span class="date">{{ item.date }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <el-table v-else :data="filtered" border style="width:100%">
      <el-table-column label="预览" width="160">
        <template #default="{ row }">
          <lee-img :src="row.src" fit="cover" style="width:140px;height:100px;border-radius:8px"/>
        </template>
      </el-table-column>
      <el-table-column label="标题" prop="title" min-width="200"/>
      <el-table-column label="标签" min-width="220">
        <template #default="{ row }">
          <el-tag v-for="t in row.tags" :key="t" size="small" class="tag">#{{ t }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="品类" prop="category" width="120"/>
      <el-table-column label="日期" prop="date" width="120"/>
    </el-table>

    <el-dialog v-model="uploadVisible" title="上传图片" :width="640" destroy-on-close>
      <div class="upload-form">
        <single-picture v-model="uploadForm.src" :width="420" :height="260" :cropper="true" :apiObj="Api.apiSysImgUpload"/>
        <el-form :model="uploadForm" label-width="80px" class="meta-form">
          <el-form-item label="标题"><el-input v-model="uploadForm.title"/></el-form-item>
          <el-form-item label="品类">
            <el-select v-model="uploadForm.category" style="width:240px">
              <el-option v-for="c in categories" :key="c" :label="c" :value="c"/>
            </el-select>
          </el-form-item>
          <el-form-item label="标签">
            <el-select v-model="uploadForm.tags" multiple filterable allow-create default-first-option style="width:100%"/>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="uploadVisible=false">取消</el-button>
        <el-button type="primary" :disabled="!uploadForm.src || !uploadForm.title" @click="saveUpload">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LeeSearchBar from '@/components/leeSearchBar.vue'
import singlePicture from '@/components/upload/single-picture.vue'
import leeImg from '@/components/image/leeImage.vue'
import Api from '@/api/api.js'
import { Upload, List, Grid } from '@element-plus/icons-vue'

const categories = ['全部','Dresses','Outerwear','Tops','Bottoms','Accessories']

const filters = ref({ q: '', category: '全部' })

const items = ref([
  { id: 1, title: 'Vintage floral midi dress', category: 'Dresses', tags: ['floral','summer'], date: '2023-09-15', src: 'https://cdn.pixabay.com/photo/2023/12/13/11/42/woman-8446800_960_720.png' },
  { id: 2, title: 'Straight leg vintage wash jeans', category: 'Bottoms', tags: ['denim','vintage'], date: '2023-10-12', src: 'https://cdn.pixabay.com/photo/2025/11/11/16/43/16-43-22-580_1280.jpg' },
  { id: 3, title: 'Red silk satin evening dress', category: 'Dresses', tags: ['evening','silk'], date: '2023-11-01', src: 'https://cdn.pixabay.com/photo/2025/10/26/13/00/ai-generated-9917901_1280.png' },
  { id: 4, title: 'Cropped biker jacket with silver hardware', category: 'Outerwear', tags: ['leather','edgy'], date: '2023-10-01', src: 'https://cdn.pixabay.com/photo/2025/10/12/07/32/italy-9889149_1280.jpg' },
  { id: 5, title: 'Neutral utility bomber', category: 'Outerwear', tags: ['utility','city'], date: '2023-08-22', src: 'https://cdn.pixabay.com/photo/2025/10/02/16/48/moon-9868832_1280.png' },
])

const filtered = computed(() => {
  const q = filters.value.q.toLowerCase()
  const cat = filters.value.category
  return items.value.filter(i =>
    (cat==='全部' || i.category===cat) &&
    (!q || i.title.toLowerCase().includes(q) || i.tags.some(t => t.toLowerCase().includes(q)))
  )
})

function setCategory(c){ filters.value.category = c }
function applyFilters(){ }
function resetFilters(){ filters.value = { q: '', category: '全部' } }

const uploadVisible = ref(false)
const uploadForm = ref({ src: '', title: '', category: 'Dresses', tags: [] })
function openUpload(){ uploadVisible.value = true }
function saveUpload(){
  const id = Math.max(...items.value.map(i=>i.id)) + 1
  const d = new Date().toISOString().slice(0,10)
  items.value.unshift({ id, src: uploadForm.value.src, title: uploadForm.value.title, category: uploadForm.value.category, tags: [...uploadForm.value.tags], date: d })
  uploadForm.value = { src: '', title: '', category: 'Dresses', tags: [] }
  uploadVisible.value = false
}

const isGrid = ref(true)
const viewModeIcon = computed(() => isGrid.value ? Grid : List)
const viewModeLabel = computed(() => isGrid.value ? '瀑布流' : '列表')
function toggleView(){ isGrid.value = !isGrid.value }
</script>

<style scoped>
.gallery-page{ display:flex; flex-direction:column; gap:12px; padding:10px }
.page-header{ display:flex; flex-direction:column; gap:4px }
.page-header .title{ font-size:20px; font-weight:700 }
.page-header .sub{ font-size:13px; color: var(--el-text-color-secondary) }
.config-card :deep(.el-card__body){ padding-top:8px }
.category-group{ display:flex; gap:8px; flex-wrap:wrap }
.category-group .el-check-tag{ padding:6px 12px; border-radius:999px }
.masonry{ column-count:3; column-gap:14px }
@media (max-width: 1200px){ .masonry{ column-count:2 } }
@media (max-width: 768px){ .masonry{ column-count:1 } }
.masonry-card{ break-inside: avoid; margin-bottom:14px }
.gallery-card :deep(.el-card__body){ padding:0 }
.card-body{ padding:10px }
.card-title{ font-size:14px; font-weight:600; margin-bottom:6px }
.card-tags{ display:flex; gap:6px; flex-wrap:wrap }
.tag{ margin-bottom:6px }
.card-meta{ display:flex; justify-content:space-between; font-size:12px; color: var(--el-text-color-secondary); margin-top:6px }
.upload-form{ display:flex; gap:16px; align-items:flex-start }
.meta-form{ flex:1 }
</style>

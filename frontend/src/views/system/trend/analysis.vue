<template>
  <div class="trend-page">
    <el-card class="info-card" shadow="never">
      <div class="info-content">
        <el-icon class="info-icon"><TrendCharts /></el-icon>
        <div class="info-text">
          <div class="title">AI 驱动的趋势预测</div>
          <div class="desc">输入季节与目标市场信息，生成基于 AI 分析的流行趋势报告，包括色彩企划、关键词趋势、单品推荐等。</div>
        </div>
      </div>
    </el-card>

    <el-card class="config-card" shadow="never">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          <span>Report Configuration</span>
        </div>
      </div>
      <LeeSearchBar :model="form" @search="generate" @reset="reset">
        <template #default>
          <el-form-item label="季节">
            <el-select v-model="form.season" placeholder="选择季节" style="width: 220px">
              <el-option v-for="s in seasons" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="品类">
            <el-select v-model="form.category" placeholder="选择品类" style="width: 220px">
              <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="场景">
            <el-select v-model="form.scene" placeholder="选择场景" style="width: 220px">
              <el-option v-for="sc in scenes" :key="sc" :label="sc" :value="sc" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标群体">
            <el-select v-model="form.audience" placeholder="选择人群" style="width: 220px">
              <el-option v-for="g in groups" :key="g.value" :label="g.label" :value="g.label" />
            </el-select>
          </el-form-item>
          <el-form-item label="风格/主题">
            <el-select v-model="form.theme" filterable placeholder="选择主题" style="width: 260px">
              <el-option v-for="t in themes" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
        </template>
        <template #actions-right>
          <el-button type="primary" @click="generate" :loading="generating" class="generate-btn">
            <el-icon><Connection /></el-icon>
            生成报告
          </el-button>
        </template>
      </LeeSearchBar>
    </el-card>

    <el-card v-if="report" class="summary-card" shadow="never">
      <div class="hashes">
        <el-tag v-for="h in report.hashes" :key="h" size="small" class="hash">{{ h }}</el-tag>
      </div>
      <div class="summary-title">{{ report.title }}</div>
      <div class="summary-sub">{{ report.subtitle }}</div>
      <div class="summary-desc">{{ report.description }}</div>
      <div class="summary-tags">
        <el-tag v-for="t in report.tags" :key="t" class="tag" effect="light">{{ t }}</el-tag>
      </div>
    </el-card>

    <el-card v-if="report" class="palette-card" shadow="never">
      <div class="palette-header">
        <el-icon><Brush /></el-icon>
        <span>色彩企划</span>
      </div>
      <div class="palette-list">
        <div v-for="c in report.palette" :key="c.hex" class="palette-item">
          <div class="swatch" :style="{ background: c.hex }"></div>
          <div class="palette-meta">
            <div class="name">{{ c.name }}</div>
            <div class="desc">{{ c.desc }}</div>
            <div class="hex">{{ c.hex }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
  </template>

<script setup>
import { ref } from 'vue'
import LeeSearchBar from '@/components/leeSearchBar.vue'
import { TrendCharts, Connection, Brush } from '@element-plus/icons-vue'

const seasons = [
  '2025 Spring/Summer',
  '2025 Fall/Winter',
  '2026 Spring/Summer'
]
const categories = ['女装', '男装', '童装', '运动']
const scenes = ['日常', '通勤', '度假', '户外']
const groups = [
  { label: 'Z世代 (18-27)', value: 'Z' },
  { label: '千禧代 (28-40)', value: 'Y' },
  { label: '成熟人群 (41+)', value: 'M' }
]
const themes = ['Minimalist Utility', 'Urban Outdoor', 'Soft Retro', 'Tech Minimal']

const form = ref({
  season: seasons[0],
  category: '女装',
  scene: '日常',
  audience: groups[0].label,
  theme: themes[0]
})

const report = ref(null)
const generating = ref(false)

function reset() {
  form.value = {
    season: seasons[0],
    category: '女装',
    scene: '日常',
    audience: groups[0].label,
    theme: themes[0]
  }
  report.value = null
}

function generate() {
  generating.value = true
  setTimeout(() => {
    const theme = form.value.theme
    const paletteMap = {
      'Minimalist Utility': [
        { name: '米白', desc: '百搭基础', hex: '#EEE9DD' },
        { name: '冰川灰', desc: '#9AAAB7', hex: '#9AAAB7' },
        { name: '古绿灰', desc: '自然沉稳', hex: '#6B7D5F' },
        { name: '玄黑色', desc: '都市沉郁', hex: '#2C3E50' },
        { name: '环保棕', desc: '可持续风格', hex: '#988B7E' }
      ],
      'Urban Outdoor': [
        { name: '霞橙', desc: '活力点缀', hex: '#FF7F50' },
        { name: '松针绿', desc: '自然能量', hex: '#2E8B57' },
        { name: '岩灰', desc: '稳重底色', hex: '#70757A' },
        { name: '雾蓝', desc: '通勤友好', hex: '#8AAAC5' },
        { name: '土褐', desc: '户外质感', hex: '#7A6B5D' }
      ],
      'Soft Retro': [
        { name: '奶油白', desc: '柔和底色', hex: '#F2E9E4' },
        { name: '雾粉', desc: '复古气息', hex: '#D8A7B1' },
        { name: '雾紫', desc: '优雅延展', hex: '#9E7FA8' },
        { name: '灰蓝', desc: '平衡层次', hex: '#7C8EA6' },
        { name: '茶褐', desc: '复古点题', hex: '#8B6D5C' }
      ],
      'Tech Minimal': [
        { name: '亮白', desc: '科技洁净', hex: '#F5F7FA' },
        { name: '冷灰', desc: '理性基调', hex: '#A3AAB7' },
        { name: '钛蓝', desc: '科技感', hex: '#3A6EA5' },
        { name: '石墨黑', desc: '功能对比', hex: '#1F2937' },
        { name: '电光绿', desc: '未来点缀', hex: '#00C853' }
      ]
    }
    const palette = paletteMap[theme] || paletteMap['Minimalist Utility']
    report.value = {
      hashes: [
        `#${form.value.season}`,
        '#AI洞察',
        `#${form.value.scene}`,
        `#${form.value.category}`
      ],
      title: '都市机能漫游',
      subtitle: `${form.value.season}${form.value.category}${form.value.scene}风格预测`,
      description:
        '为都市代女性打造的都市风格趋势，兼容极简美学与实用主义，感受极简细腻，适应城市与户外双重场景。',
      tags: ['功能性', '简约', '自然', '实用性', '都市日常'],
      palette
    }
    generating.value = false
  }, 400)
}
</script>

<style scoped>
.trend-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 10px;
}
.info-card {
  border-radius: 10px;
}
.info-content {
  display: flex;
  align-items: center;
  gap: 12px;
}
.info-icon {
  font-size: 22px;
  color: var(--el-color-primary);
}
.info-text .title {
  font-size: 16px;
  font-weight: 600;
}
.info-text .desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.config-card :deep(.el-card__body) {
  padding-top: 8px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}
.generate-btn {
  width: 160px;
}
.summary-card {
  border-radius: 10px;
}
.hashes {
  display: flex;
  gap: 8px;
}
.hash {
  margin-bottom: 8px;
}
.summary-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 6px;
}
.summary-sub {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.summary-desc {
  font-size: 14px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}
.summary-tags {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.palette-card {
  border-radius: 10px;
}
.palette-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  margin-bottom: 12px;
}
.palette-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}
.palette-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.swatch {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.05) inset;
}
.palette-meta .name {
  font-size: 14px;
  font-weight: 600;
}
.palette-meta .desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.palette-meta .hex {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>

<template>
  <!-- 공통 DataTable (Phase 2-C Post: Admin v2 리팩토링 기반) -->
  <div class="bg-white rounded-xl shadow-sm overflow-hidden">
    <!-- 상단 툴바 -->
    <div v-if="$slots.toolbar || searchable || exportable" class="p-3 border-b flex items-center gap-2 flex-wrap">
      <input
        v-if="searchable"
        v-model="search"
        @input="onSearchDebounced"
        :placeholder="searchPlaceholder"
        class="px-3 py-1.5 border rounded text-sm w-full md:w-64"
      />
      <slot name="toolbar" :rows="filtered" />
      <div class="ml-auto flex items-center gap-2">
        <button v-if="exportable" @click="exportCsv" :disabled="!filtered.length" class="px-3 py-1.5 bg-green-500 hover:bg-green-600 text-white rounded text-xs font-semibold disabled:opacity-50">
          📥 CSV
        </button>
        <button v-if="bulkActions?.length" :disabled="!selectedRows.length" @click="showBulk = !showBulk" class="px-3 py-1.5 bg-amber-100 hover:bg-amber-200 text-amber-800 rounded text-xs disabled:opacity-50">
          ⚡ 일괄 ({{ selectedRows.length }})
        </button>
      </div>
    </div>

    <!-- 일괄 액션 드롭다운 -->
    <div v-if="showBulk && bulkActions?.length && selectedRows.length" class="bg-amber-50 border-b p-2 flex gap-2 flex-wrap">
      <button
        v-for="action in bulkActions" :key="action.key"
        @click="handleBulk(action)"
        :class="['px-3 py-1 rounded text-xs font-semibold', action.danger ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-white hover:bg-gray-100 border']"
      >{{ action.label }}</button>
    </div>

    <!-- 테이블 -->
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
          <tr>
            <th v-if="bulkActions?.length" class="px-3 py-2 w-10">
              <input type="checkbox" :checked="allSelected" @change="toggleAll" />
            </th>
            <th
              v-for="col in columns" :key="col.key"
              @click="col.sortable && sort(col.key)"
              :class="['px-3 py-2 text-left', col.sortable ? 'cursor-pointer hover:text-amber-600' : '', col.class]"
            >
              {{ col.label }}
              <span v-if="col.sortable && sortKey === col.key" class="ml-1">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th v-if="$slots.actions" class="px-3 py-2 text-center w-32">액션</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td :colspan="totalColumns" class="p-8 text-center text-gray-400">로딩 중...</td></tr>
          <tr v-else-if="!paged.length"><td :colspan="totalColumns" class="p-10 text-center text-gray-500">{{ emptyText }}</td></tr>
          <tr v-for="row in paged" :key="rowKey(row)" class="border-t hover:bg-amber-50 transition" v-else>
            <td v-if="bulkActions?.length" class="px-3 py-2">
              <input type="checkbox" :checked="isSelected(row)" @change="toggleRow(row)" />
            </td>
            <td v-for="col in columns" :key="col.key" :class="['px-3 py-2', col.class]">
              <slot :name="`cell-${col.key}`" :row="row" :value="getCell(row, col.key)">
                {{ formatCell(row, col) }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="px-3 py-2 text-center">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 페이지네이션 -->
    <div v-if="pageSize && filtered.length > pageSize" class="p-3 border-t flex items-center justify-between text-xs text-gray-500">
      <span>{{ filtered.length.toLocaleString() }}건 중 {{ pageStart + 1 }}~{{ pageEnd }}</span>
      <div class="flex items-center gap-1">
        <button @click="page = Math.max(1, page - 1)" :disabled="page === 1" class="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-30">‹</button>
        <span class="px-2">{{ page }} / {{ totalPages }}</span>
        <button @click="page = Math.min(totalPages, page + 1)" :disabled="page === totalPages" class="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-30">›</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },        // [{ key, label, sortable, format, class }]
  loading: { type: Boolean, default: false },
  searchable: { type: Boolean, default: true },
  searchKeys: { type: Array, default: () => [] },  // 검색 대상 key (비면 모든 string 필드)
  searchPlaceholder: { type: String, default: '검색...' },
  exportable: { type: Boolean, default: false },
  pageSize: { type: Number, default: 50 },
  emptyText: { type: String, default: '데이터 없음' },
  rowKeyField: { type: String, default: 'id' },
  bulkActions: { type: Array, default: null },
})

const emit = defineEmits(['bulk-action'])

const search = ref('')
const sortKey = ref(null)
const sortDir = ref('asc')
const page = ref(1)
const selectedIds = ref(new Set())
const showBulk = ref(false)

let searchTimeout = null
function onSearchDebounced() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { page.value = 1 }, 200)
}

const filtered = computed(() => {
  let out = props.rows
  if (search.value) {
    const q = search.value.toLowerCase()
    const keys = props.searchKeys.length ? props.searchKeys : props.columns.map(c => c.key)
    out = out.filter(r => keys.some(k => String(getCell(r, k) ?? '').toLowerCase().includes(q)))
  }
  if (sortKey.value) {
    const k = sortKey.value
    const d = sortDir.value === 'asc' ? 1 : -1
    out = [...out].sort((a, b) => {
      const va = getCell(a, k), vb = getCell(b, k)
      if (va === vb) return 0
      return (va > vb ? 1 : -1) * d
    })
  }
  return out
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / props.pageSize)))
const pageStart = computed(() => (page.value - 1) * props.pageSize)
const pageEnd = computed(() => Math.min(filtered.value.length, pageStart.value + props.pageSize))
const paged = computed(() => props.pageSize ? filtered.value.slice(pageStart.value, pageEnd.value) : filtered.value)

const totalColumns = computed(() => props.columns.length + (props.bulkActions?.length ? 1 : 0) + 1)

function getCell(row, key) {
  return key.split('.').reduce((o, k) => o?.[k], row)
}
function formatCell(row, col) {
  const v = getCell(row, col.key)
  if (col.format) return col.format(v, row)
  return v ?? '-'
}
function rowKey(row) { return row[props.rowKeyField] ?? JSON.stringify(row) }

function sort(key) {
  if (sortKey.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortKey.value = key; sortDir.value = 'asc' }
}

function isSelected(row) { return selectedIds.value.has(rowKey(row)) }
function toggleRow(row) {
  const k = rowKey(row)
  if (selectedIds.value.has(k)) selectedIds.value.delete(k)
  else selectedIds.value.add(k)
  selectedIds.value = new Set(selectedIds.value)
}
function toggleAll() {
  if (allSelected.value) selectedIds.value = new Set()
  else selectedIds.value = new Set(paged.value.map(rowKey))
}
const allSelected = computed(() => paged.value.length > 0 && paged.value.every(r => selectedIds.value.has(rowKey(r))))
const selectedRows = computed(() => props.rows.filter(r => selectedIds.value.has(rowKey(r))))

function handleBulk(action) {
  if (action.confirm && !confirm(action.confirm)) return
  emit('bulk-action', { key: action.key, rows: selectedRows.value })
  selectedIds.value = new Set()
  showBulk.value = false
}

function exportCsv() {
  const cols = props.columns.map(c => c.key)
  const header = props.columns.map(c => JSON.stringify(c.label || c.key)).join(',')
  const body = filtered.value.map(r => cols.map(k => JSON.stringify(getCell(r, k) ?? '')).join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + header + '\n' + body], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `export_${Date.now()}.csv`; a.click()
  URL.revokeObjectURL(url)
}

watch(() => props.rows, () => { page.value = 1; selectedIds.value = new Set() })
</script>

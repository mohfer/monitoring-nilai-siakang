<template>
    <div @click.self="$emit('close')"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4 backdrop-blur-sm transition-opacity">
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg border border-gray-100 dark:border-gray-700 transform transition-all animate-in fade-in zoom-in duration-200">
            <div class="p-6 pb-0">
                <h2 class="text-2xl font-bold mb-6 dark:text-white flex items-center gap-2">
                    <Edit3 v-if="task" class="text-blue-600" />
                    <Plus v-else class="text-blue-600" />
                    <span v-if="task">Edit Monitor</span>
                    <span v-else>New Monitor</span>
                </h2>
            </div>

            <form @submit.prevent="save" class="p-6 pt-0">
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Friendly
                            Name</label>
                        <input v-model="form.name" required placeholder="e.g. My Semester 5" class="input-field" />
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Login
                                ID</label>
                            <input v-model="form.login_id" required class="input-field" placeholder="NIM/Email" />
                        </div>
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
                            <div class="relative">
                                <input v-model="form.password" :type="showPassword ? 'text' : 'password'" required
                                    class="input-field pr-10" placeholder="••••••" />
                                <button type="button" @click="showPassword = !showPassword"
                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 block h-fit w-fit">
                                    <Eye v-if="!showPassword" :size="16" />
                                    <EyeOff v-else :size="16" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label
                            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center justify-between">
                            Telegram Chat ID
                            <a href="https://t.me/userinfobot" target="_blank"
                                class="text-xs text-blue-500 hover:underline flex items-center gap-1">
                                <HelpCircle :size="12" /> Find ID
                            </a>
                        </label>
                        <input v-model="form.chat_id" required class="input-field" placeholder="123456789" />
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex justify-between items-center">
                                Semester Code
                                <button type="button" @click="fetchSemesters" :disabled="isLoadingSemesters"
                                    class="text-xs text-blue-500 hover:text-blue-700 dark:hover:text-blue-400 no-underline hover:underline flex items-center gap-1 cursor-pointer disabled:opacity-50">
                                    <span v-if="isLoadingSemesters">Loading...</span>
                                    <span v-else class="flex items-center gap-1">
                                        <RefreshCw :size="10" /> Fetch
                                    </span>
                                </button>
                            </label>

                            <div v-if="semestersList.length > 0" class="relative">
                                <select v-model="form.target_semester_code"
                                    class="input-field appearance-none cursor-pointer">
                                    <option value="">-- Auto Select --</option>
                                    <option v-for="sem in semestersList" :key="sem.code" :value="sem.code">
                                        {{ sem.title }}
                                    </option>
                                </select>
                                <ChevronDown :size="14"
                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                            </div>
                            <input v-else v-model="form.target_semester_code" placeholder="Optional (or click Fetch)"
                                class="input-field" />
                            <p v-if="fetchError" class="text-xs text-red-500 mt-1">{{ fetchError }}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Interval
                                (sec)</label>
                            <input v-model.number="form.interval" type="number" min="60" class="input-field" />
                        </div>
                    </div>
                </div>

                <div class="mt-8 flex justify-end gap-3 pt-4 border-t border-gray-100 dark:border-gray-700">
                    <button type="button" @click="$emit('close')"
                        class="px-5 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg font-medium transition flex items-center gap-2">
                        <X :size="18" /> Cancel
                    </button>
                    <button type="submit"
                        class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md hover:shadow-lg transition font-medium flex items-center gap-2">
                        <Save :size="18" /> Save Monitor
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { X, Save, Edit3, Plus, HelpCircle, Eye, EyeOff, RefreshCw, ChevronDown } from 'lucide-vue-next'

const props = defineProps(['task'])
const emit = defineEmits(['close', 'save'])

const showPassword = ref(false)
const isLoadingSemesters = ref(false)
const semestersList = ref([])
const fetchError = ref('')

const form = ref({
    name: '',
    login_id: '',
    password: '',
    chat_id: '',
    target_semester_code: '',
    interval: 300
})

watch(() => props.task, (newVal) => {
    semestersList.value = []
    fetchError.value = ''
    if (newVal) {
        form.value = { ...newVal }
    } else {
        form.value = {
            name: '',
            login_id: '',
            password: '',
            chat_id: '',
            target_semester_code: '',
            interval: 300
        }
    }
}, { immediate: true })

const fetchSemesters = async () => {
    if (!form.value.login_id || !form.value.password) {
        fetchError.value = "Please enter Login ID and Password first."
        return
    }

    isLoadingSemesters.value = true
    fetchError.value = ''
    semestersList.value = []

    try {
        const res = await axios.post('/api/check-semesters', {
            login_id: form.value.login_id,
            password: form.value.password
        })
        semestersList.value = res.data.semesters
        if (semestersList.value.length === 0) {
            fetchError.value = "No semesters found."
        }
    } catch (e) {
        fetchError.value = e.response?.data?.detail || "Failed to fetch semesters"
    } finally {
        isLoadingSemesters.value = false
    }
}

const save = () => {
    emit('save', form.value)
}
</script>

<style scoped>
.input-field {
    @apply w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 transition dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 focus:outline-none;
}
</style>

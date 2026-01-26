<template>
    <div @click.self="$emit('close')"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4 backdrop-blur-sm transition-opacity">
        <div
            class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg border border-gray-100 dark:border-gray-700 transform transition-all animate-in fade-in zoom-in duration-200 max-h-[90vh] overflow-y-auto custom-scrollbar">
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
                        <input v-model="form.name" required placeholder="e.g. My Monitor" class="input-field" />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Monitor
                            Type</label>
                        <div class="flex gap-4">
                            <label class="flex items-center gap-2 cursor-pointer">
                                <input type="radio" v-model="form.monitor_type" value="nilai"
                                    class="text-blue-600 focus:ring-blue-500">
                                <span class="text-gray-700 dark:text-gray-300">Nilai (Grades)</span>
                            </label>
                            <label class="flex items-center gap-2 cursor-pointer">
                                <input type="radio" v-model="form.monitor_type" value="krs"
                                    class="text-blue-600 focus:ring-blue-500">
                                <span class="text-gray-700 dark:text-gray-300">KRS (Plans)</span>
                            </label>
                        </div>
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

                    <div class="pt-2">
                        <label
                            class="block text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2 border-b border-gray-100 dark:border-gray-700 pb-2">
                            <Bell :size="18" class="text-blue-600 dark:text-blue-500" />
                            Notifications
                        </label>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Telegram Chat ID
                                </label>
                                <div class="relative group">
                                    <input v-model="form.chat_id" class="input-field pl-10" placeholder="123456789" />
                                </div>
                                <a href="https://t.me/userinfobot" target="_blank"
                                    class="text-xs text-blue-500 hover:text-blue-600 dark:text-blue-400 hover:underline mt-1.5 inline-flex items-center gap-1">
                                    Find ID
                                    <ExternalLink :size="10" />
                                </a>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    WhatsApp Number
                                </label>
                                <div class="relative group">
                                    <input v-model="form.whatsapp_number" class="input-field pl-10"
                                        placeholder="628... or Group ID" />
                                </div>
                                <div class="flex justify-between items-center mt-1.5">
                                    <p class="text-xs text-gray-400 dark:text-gray-500">
                                        Number (628...)
                                    </p>
                                    <a href="https://waha.devlike.pro/swagger/#/%F0%9F%91%A5%20Groups/GroupsController_getGroups"
                                        target="_blank"
                                        class="text-xs text-blue-500 hover:text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1">
                                        Find Group ID
                                        <ExternalLink :size="10" />
                                    </a>
                                </div>
                            </div>
                        </div>

                        <div v-if="!form.chat_id && !form.whatsapp_number"
                            class="mt-3 flex items-start gap-2 text-xs text-amber-600 dark:text-amber-500 bg-amber-50 dark:bg-amber-900/20 p-2.5 rounded-lg border border-amber-100 dark:border-amber-900/30">
                            <AlertCircle :size="14" class="mt-0.5 shrink-0" />
                            <span>Required: Please fill at least one channel to receive alerts.</span>
                        </div>
                    </div>

                    <div v-if="form.monitor_type === 'krs'">
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Target Courses <span class="text-xs text-gray-500">(Names only, one per line)</span>
                        </label>
                        <textarea v-model="form.target_courses_text" rows="4" class="input-field font-mono text-sm"
                            placeholder="Pemrograman Berorientasi Objek&#10;Data Mining&#10;..."></textarea>
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
import { X, Save, Edit3, Plus, HelpCircle, Eye, EyeOff, RefreshCw, ChevronDown, Bell, Send, MessageCircle, AlertCircle, ExternalLink } from 'lucide-vue-next'

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
    whatsapp_number: '',
    target_semester_code: '',
    interval: 300,
    monitor_type: 'nilai',
    target_courses_text: ''
})

watch(() => props.task, (newVal) => {
    semestersList.value = []
    fetchError.value = ''
    if (newVal) {
        let tcText = '';
        if (newVal.target_courses) {
            try {
                const arr = JSON.parse(newVal.target_courses);
                tcText = Array.isArray(arr) ? arr.join('\n') : newVal.target_courses;
            } catch {
                tcText = newVal.target_courses;
            }
        }

        form.value = {
            ...newVal,
            monitor_type: newVal.monitor_type || 'nilai',
            whatsapp_number: newVal.whatsapp_number || '',
            target_courses_text: tcText
        }
    } else {
        form.value = {
            name: '',
            login_id: '',
            password: '',
            chat_id: '',
            whatsapp_number: '',
            target_semester_code: '',
            interval: 300,
            monitor_type: 'nilai',
            target_courses_text: ''
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
    const payload = { ...form.value }

    if (!payload.chat_id && !payload.whatsapp_number) {
        alert("Please provide at least a Telegram Chat ID or WhatsApp Number.")
        return
    }

    const lines = payload.target_courses_text
        ? payload.target_courses_text.split('\n').map(l => l.trim()).filter(l => l)
        : [];
    payload.target_courses = JSON.stringify(lines);

    delete payload.target_courses_text;

    emit('save', payload)
}
</script>

<style scoped>
.input-field {
    @apply w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 transition dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 focus:outline-none;
}
</style>

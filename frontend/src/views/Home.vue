<template>
  <v-row justify="center">
    <v-col cols="12" md="8" lg="6">
      <v-card class="mx-auto" elevation="8">
        <v-card-title class="text-h4 text-center py-4 bg-primary text-white">
          PDF to Text Converter
        </v-card-title>
        
        <v-card-text class="pa-6">
          <div class="text-body-1 text-center mb-6 text-grey-darken-1">
            Upload your PDF file and we'll convert it to searchable text
          </div>
          
          <v-file-input
            v-model="file"
            accept=".pdf"
            label="Select or drop your PDF file"
            prepend-icon="mdi-file-pdf-box"
            :loading="uploading"
            :disabled="uploading"
            @change="onFileChange"
            variant="outlined"
            show-size
            class="mb-4"
          ></v-file-input>

          <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            class="mb-4"
          >
            {{ error }}
          </v-alert>

          <v-alert
            v-if="success"
            type="success"
            variant="tonal"
            class="mb-4"
          >
            {{ success }}
          </v-alert>

          <v-btn
            block
            color="primary"
            size="large"
            :loading="uploading"
            :disabled="!file"
            @click="uploadFile"
            class="mt-4"
          >
            <v-icon left class="mr-2">mdi-cloud-upload</v-icon>
            Convert to Text
          </v-btn>
        </v-card-text>
      </v-card>

      <!-- Conversion Status -->
      <v-card 
        v-if="conversionId" 
        class="mt-6" 
        elevation="8"
      >
        <v-card-title class="text-h6 py-4 bg-secondary text-white">
          <v-icon left class="mr-2">mdi-progress-clock</v-icon>
          Conversion Status
        </v-card-title>
        
        <v-card-text class="pa-6">
          <v-progress-linear
            v-if="status === 'processing'"
            indeterminate
            color="primary"
            class="mb-4"
          ></v-progress-linear>
          
          <div v-if="status === 'processing'" class="text-center text-body-1 mb-4">
            Converting your PDF... Please wait
          </div>
          
          <div v-if="status === 'completed'" class="text-center">
            <v-icon
              color="success"
              size="48"
              class="mb-4"
            >
              mdi-check-circle
            </v-icon>
            <div class="text-h6 mb-4">Conversion Complete!</div>
            <v-btn
              color="success"
              :href="textUrl"
              target="_blank"
              size="large"
            >
              <v-icon left class="mr-2">mdi-download</v-icon>
              Download Text File
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'

// Configure axios with base URL
const API_BASE_URL = 'http://35.187.13.156'
axios.defaults.baseURL = API_BASE_URL

export default {
  name: 'Home',
  
  data() {
    return {
      file: null,
      uploading: false,
      error: null,
      success: null,
      conversionId: null,
      status: null,
      textUrl: null,
      statusCheckInterval: null
    }
  },

  methods: {
    onFileChange(file) {
      this.error = null
      this.success = null
      this.conversionId = null
      this.status = null
      this.textUrl = null
    },

    async uploadFile() {
      if (!this.file) return

      this.uploading = true
      this.error = null
      this.success = null

      try {
        const formData = new FormData()
        formData.append('file', this.file)

        const response = await axios.post('/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        this.success = response.data.message
        this.conversionId = response.data.file_id
        this.startStatusCheck()

      } catch (error) {
        this.error = error.response?.data?.detail || 'Error uploading file'
      } finally {
        this.uploading = false
      }
    },

    async checkStatus() {
      if (!this.conversionId) return

      try {
        const response = await axios.get(`/status/${this.conversionId}`)
        this.status = response.data.status
        
        if (response.data.status === 'completed') {
          this.textUrl = API_BASE_URL + response.data.text_url
          this.stopStatusCheck()
        }
      } catch (error) {
        console.error('Error checking status:', error)
      }
    },

    startStatusCheck() {
      this.status = 'processing'
      this.statusCheckInterval = setInterval(this.checkStatus, 2000)
    },

    stopStatusCheck() {
      if (this.statusCheckInterval) {
        clearInterval(this.statusCheckInterval)
        this.statusCheckInterval = null
      }
    }
  },

  beforeUnmount() {
    this.stopStatusCheck()
  }
}
</script>

<style scoped>
.v-card-title {
  word-break: normal;
}
</style> 
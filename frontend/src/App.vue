<template>
  <v-app>
    <v-app-bar app color="primary" dark elevation="4">
      <v-app-bar-title class="text-h5 font-weight-bold">
        <v-icon icon="mdi-file-document-convert" class="mr-2"></v-icon>
        PagePulse
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon href="https://github.com/yourusername/pagepulse" target="_blank">
        <v-icon>mdi-github</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <v-container class="py-8">
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app color="primary" dark class="py-3">
      <v-container>
        <div class="d-flex align-center justify-space-between">
          <span>&copy; {{ new Date().getFullYear() }} PagePulse</span>
          <div>
            <span class="text-caption">Made with</span>
            <v-icon icon="mdi-heart" color="red" class="mx-1"></v-icon>
            <span class="text-caption">using Vue & GCP</span>
          </div>
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
:root {
  --v-theme-overlay-multiplier: 1;
}

.v-application {
  font-family: 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 
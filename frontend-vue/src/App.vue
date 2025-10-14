<template>
  <header class="border-b bg-white">
    <div class="mx-auto max-w-6xl px-4 py-3 flex flex-wrap gap-3 items-center justify-between">
      <h1 class="text-lg font-semibold">Rail QMS PoC</h1>

      <nav class="flex flex-wrap gap-2 items-center">
        <!-- Core -->
        <RouterLink
          to="/"
          class="px-3 py-1.5 rounded-md hover:bg-slate-100"
          active-class="bg-maroon text-white hover:bg-maroon"
        >
          Dashboard
        </RouterLink>

        <RouterLink
          to="/pads"
          class="px-3 py-1.5 rounded-md hover:bg-slate-100"
          active-class="bg-maroon text-white hover:bg-maroon"
        >
          Pads
        </RouterLink>

        <span class="mx-2 h-5 w-px bg-slate-300"></span>

        <!-- Navigation links for AI features -->
        <div class="ai-nav flex flex-wrap gap-2">
          <RouterLink to="/ai/predict" class="ai-feature-link">Predict</RouterLink>
          <RouterLink to="/ai/xai" class="ai-feature-link">XAI</RouterLink>
          <RouterLink to="/ai/reviews" class="ai-feature-link">Reviews</RouterLink>
          <RouterLink to="/ai/models" class="ai-feature-link">Models</RouterLink>
          <RouterLink to="/ai/vision" class="ai-feature-link">Vision</RouterLink>
        </div>
      </nav>
    </div>
  </header>

  <main class="mx-auto max-w-6xl px-4 py-6">
    <RouterView />
  </main>
</template>

<style scoped>
/* AI chip styling */
.ai-feature-link {
  @apply px-3 py-1.5 rounded-full border border-indigo-300 text-indigo-700 hover:bg-indigo-50;
}
/* Active state for AI feature links (RouterLink auto-adds this class) */
.ai-feature-link.router-link-active {
  @apply bg-indigo-600 text-white border-indigo-600;
}
</style>
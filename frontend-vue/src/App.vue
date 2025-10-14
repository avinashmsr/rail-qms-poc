<template>
  <div class="min-h-screen bg-slate-50 text-slate-800">
    <!-- Top bar -->
    <header class="sticky top-0 z-20 border-b bg-white/90 backdrop-blur">
      <div class="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-semibold tracking-tight">
          🚄 Rail QMS <span class="text-slate-500 text-sm font-normal">PoC</span>
        </h1>
        <nav class="flex gap-4">
          <RouterLink to="/" class="px-3 py-1.5 rounded-md hover:bg-slate-100"
            active-class="bg-slate-900 text-white hover:bg-slate-900">Dashboard</RouterLink>
          <RouterLink to="/pads" class="px-3 py-1.5 rounded-md hover:bg-slate-100"
            active-class="bg-slate-900 text-white hover:bg-slate-900">Pads</RouterLink>
          <RouterLink to="/ai/predict" class="underline">Predict</RouterLink>
          <RouterLink to="/ai/xai" class="underline">XAI</RouterLink>
          <RouterLink to="/ai/reviews" class="underline">Reviews</RouterLink>
          <RouterLink to="/ai/models" class="underline">Models</RouterLink>
          <RouterLink to="/ai/vision" class="underline">Vision</RouterLink>
        </nav>
      </div>
    </header>

    <!-- Page -->
    <main class="mx-auto max-w-6xl px-4 py-6">
      <RouterView />
    </main>

    <footer class="mx-auto max-w-6xl px-4 py-8 text-sm text-slate-500">
      Built with FastAPI + Vue + Tailwind · Demo data only
    </footer>
  </div>
</template>
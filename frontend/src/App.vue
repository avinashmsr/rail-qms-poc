<template>
  <nav style="display:flex; gap:12px; padding:12px; border-bottom:1px solid #eee">
    <router-link to="/">Dashboard</router-link>
    <router-link to="/pads">Pads</router-link>
  </nav>
  <router-view />
</template>
<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import BottomNav from '$lib/components/common/BottomNav.svelte';

  const publicRoutes = ['/', '/login', '/register'];
  let ready = false;

  onMount(async () => {
    if (import.meta.env.DEV && 'serviceWorker' in navigator) {
      void navigator.serviceWorker.getRegistrations().then((registrations) =>
        Promise.all(registrations.map((registration) => registration.unregister()))
      );
      if ('caches' in window) {
        void caches.keys().then((keys) => Promise.all(keys.map((key) => caches.delete(key))));
      }
    }

    const isPublic = publicRoutes.includes(page.url.pathname);
    const hasToken = Boolean(localStorage.getItem('token'));

    if (hasToken && isPublic) {
      await goto('/dashboard', { replaceState: true });
    } else if (!hasToken && !isPublic) {
      await goto('/', { replaceState: true });
    }

    ready = true;
  });
</script>

{#if ready}
  <slot />
  {#if !publicRoutes.includes(page.url.pathname)}
    <BottomNav />
  {/if}
{/if}

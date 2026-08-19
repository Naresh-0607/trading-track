<script lang="ts">
  import { goto } from '$app/navigation';
  import { LogOut } from 'lucide-svelte';
  export let title: string;
  export let subtitle = '';
  function logout() {
    localStorage.removeItem('token');
    void goto('/');
  }
</script>

<header>
  <div class="identity">
    <img src="/app-icon-192.png" alt="" />
    <div>
      <div class="eyebrow">Trade Track</div>
      <h1 class="page-title">{title}</h1>
      {#if subtitle}<p class="muted">{subtitle}</p>{/if}
    </div>
  </div>
  <button class="icon" onclick={logout} aria-label="Log out"><LogOut size={20} /></button>
</header>

<style>
  header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:22px}.identity{display:flex;align-items:flex-start;gap:12px}.identity img{width:42px;height:42px;border-radius:12px}.icon{border:1px solid #26364e;background:#0d192b;color:#93a2b7;padding:10px;border-radius:12px;cursor:pointer}p{font-size:.88rem;margin-bottom:0}
</style>

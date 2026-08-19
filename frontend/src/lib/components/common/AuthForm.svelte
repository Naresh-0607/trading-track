<script lang="ts">
  import { goto } from '$app/navigation';
  import { authApi } from '$lib/api';
  export let mode: 'login' | 'register';
  let name = '';
  let email = '';
  let password = '';
  let loading = false;
  let error = '';

  async function submit() {
    loading = true;
    error = '';
    try {
      const result = mode === 'login'
        ? await authApi.login({ email, password })
        : await authApi.register({ name, email, password });
      localStorage.setItem('token', result.access_token);
      void goto('/dashboard');
    } catch (reason) {
      error = reason instanceof Error ? reason.message : 'Unable to continue';
    } finally {
      loading = false;
    }
  }
</script>

<main>
  <section class="card auth">
    <img class="mark" src="/app-icon-192.png" alt="Trade Track" />
    <div class="eyebrow">Trade Track</div>
    <h1>{mode === 'login' ? 'Welcome back' : 'Create your journal'}</h1>
    <p class="muted">{mode === 'login' ? 'Sign in to review your trading edge.' : 'Start recording decisions, not just results.'}</p>
    <form onsubmit={(event) => { event.preventDefault(); submit(); }}>
      {#if mode === 'register'}<label class="field"><span>Name</span><input bind:value={name} required autocomplete="name" /></label>{/if}
      <label class="field"><span>Email</span><input type="email" bind:value={email} required autocomplete="email" /></label>
      <label class="field"><span>Password</span><input type="password" bind:value={password} minlength="8" required autocomplete={mode === 'login' ? 'current-password' : 'new-password'} /></label>
      {#if error}<p class="error">{error}</p>{/if}
      <button class="btn" disabled={loading}>{loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
    </form>
    <p class="switch">{mode === 'login' ? 'New here?' : 'Already registered?'} <a href={mode === 'login' ? '/register' : '/'}>{mode === 'login' ? 'Create account' : 'Sign in'}</a></p>
  </section>
</main>

<style>
  main{min-height:100vh;display:grid;place-items:center;padding:20px}.auth{width:min(420px,100%);box-sizing:border-box}.mark{width:56px;height:56px;border-radius:16px;display:block;margin-bottom:20px}h1{margin:.35rem 0}.muted{margin-bottom:25px}form{display:grid;gap:15px}.btn{width:100%;margin-top:4px}.switch{text-align:center;margin:22px 0 0;color:#8290a7;font-size:.88rem}.switch a{color:#5c96ff}
</style>

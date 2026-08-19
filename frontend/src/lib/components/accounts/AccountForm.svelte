<script lang="ts">
 import type { Account } from '$lib/types';
 import { accountsApi } from '$lib/api';
 export let account: Account | null = null;
 export let close: () => void;
 export let saved: () => void;
 let form = { name: account?.name || '', broker: account?.broker || '', account_type: account?.account_type || 'OTHER', initial_balance: account?.initial_balance || '0', currency: account?.currency || 'USD', is_active: account?.is_active ?? true };
 let error = ''; let loading = false;
 async function submit() {
  loading = true; error = '';
  try { account ? await accountsApi.update(account.id, form) : await accountsApi.create(form); saved(); close(); }
  catch (e) { error = e instanceof Error ? e.message : 'Could not save account'; }
  finally { loading = false; }
 }
</script>
<div class="modal" role="dialog" aria-modal="true" aria-label={account ? 'Edit account' : 'Add account'} tabindex="-1" onclick={(e) => e.target === e.currentTarget && close()} onkeydown={(e) => e.key === 'Escape' && close()}>
 <section class="sheet">
  <header><div><div class="eyebrow">Portfolio</div><h2>{account ? 'Edit account' : 'Add account'}</h2></div><button class="btn secondary" onclick={close}>Close</button></header>
  <form class="grid" onsubmit={(e) => { e.preventDefault(); submit(); }}>
   <label class="field"><span>Account name *</span><input bind:value={form.name} required /></label>
   <label class="field"><span>Broker</span><input bind:value={form.broker} /></label>
   <label class="field"><span>Account type</span><select bind:value={form.account_type}>{#each ['LIVE','DEMO','PROP','OTHER'] as x}<option>{x}</option>{/each}</select></label>
   <label class="field"><span>Initial balance</span><input type="number" step=".01" bind:value={form.initial_balance} /></label>
   <label class="field"><span>Currency</span><input minlength="3" maxlength="3" bind:value={form.currency} /></label>
   <label><input type="checkbox" bind:checked={form.is_active} /> Active account</label>
   {#if error}<p class="error">{error}</p>{/if}<button class="btn" disabled={loading}>{loading ? 'Saving…' : 'Save account'}</button>
  </form>
 </section>
</div>
<style>header{display:flex;justify-content:space-between;margin-bottom:20px}h2{margin:.25rem 0}form{max-width:480px}</style>

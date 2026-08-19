<script lang="ts">
  import { onMount } from 'svelte';
  import AppHeader from '$lib/components/common/AppHeader.svelte';
  import TradeCard from '$lib/components/dashboard/TradeCard.svelte';
  import TradeForm from '$lib/components/dashboard/TradeForm.svelte';
  import { accountsApi, tradesApi } from '$lib/api';
  import type { Account, Trade } from '$lib/types';

  let accounts: Account[] = [];
  let trades: Trade[] = [];
  let accountId = '';
  let side = '';
  let search = '';
  let loading = true;
  let error = '';
  let showForm = false;
  let editing: Trade | null = null;
  let searchTimer: ReturnType<typeof setTimeout>;

  $: closed = trades.filter((trade) => trade.pnl !== null);
  $: net = closed.reduce((total, trade) => total + Number(trade.pnl), 0);
  $: wins = closed.filter((trade) => Number(trade.pnl) > 0).length;

  function tradeQuery() {
    const query = new URLSearchParams({ page_size: '100' });
    if (accountId) query.set('account_id', accountId);
    if (side) query.set('side', side);
    if (search) query.set('search', search);
    return `?${query}`;
  }

  async function loadDashboard() {
    loading = true;
    error = '';
    try {
      const [accountItems, tradePage] = await Promise.all([
        accountsApi.list(),
        tradesApi.list(tradeQuery())
      ]);
      accounts = accountItems;
      trades = tradePage.items;
    } catch (reason) {
      error = reason instanceof Error ? reason.message : 'Could not load dashboard';
    } finally {
      loading = false;
    }
  }

  async function loadTrades() {
    loading = true;
    error = '';
    try {
      trades = (await tradesApi.list(tradeQuery())).items;
    } catch (reason) {
      error = reason instanceof Error ? reason.message : 'Could not load trades';
    } finally {
      loading = false;
    }
  }

  function searchLater() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadTrades, 300);
  }

  onMount(loadDashboard);
</script>

<svelte:head><title>Dashboard · Trade Track</title></svelte:head>

<main class="shell">
  <AppHeader title="Dashboard" subtitle="Your performance at a glance" />

  <div class="controls">
    <select class="search" bind:value={accountId} onchange={loadTrades}>
      <option value="">All accounts</option>
      {#each accounts as account}<option value={account.id}>{account.name}</option>{/each}
    </select>
    <input class="search" bind:value={search} oninput={searchLater} placeholder="Search symbol or notes…" />
  </div>

  <section class="grid summary">
    <div class="card wide"><div class="muted">Net P&amp;L</div><h2 class:profit={net >= 0} class:loss={net < 0}>{net >= 0 ? '+' : ''}${net.toFixed(2)}</h2></div>
    <div class="card"><div class="muted">Win rate</div><h2>{closed.length ? (wins / closed.length * 100).toFixed(1) : '0'}%</h2></div>
    <div class="card"><div class="muted">Trades</div><h2>{closed.length}</h2></div>
  </section>

  <div class="tabs">
    {#each [['', 'All'], ['BUY', 'Buy'], ['SELL', 'Sell']] as item}
      <button class:active={side === item[0]} onclick={() => { side = item[0]; loadTrades(); }}>{item[1]}</button>
    {/each}
  </div>

  {#if error}
    <p class="error">{error}</p>
  {:else if loading}
    <div class="empty">Loading trades…</div>
  {:else if !trades.length}
    <div class="card empty">
      <h2>{accounts.length ? 'No trades yet' : 'No accounts yet'}</h2>
      <p>{accounts.length ? 'Add your first trade using the + button.' : 'Create an account from the Accounts tab first.'}</p>
    </div>
  {:else}
    <section class="grid trades">
      {#each trades as trade}
        <TradeCard {trade} account={accounts.find((account) => account.id === trade.account_id)} edit={() => { editing = trade; showForm = true; }} removed={loadDashboard} />
      {/each}
    </section>
  {/if}

  {#if accounts.length}<button class="btn fab" aria-label="Add trade" onclick={() => { editing = null; showForm = true; }}>+</button>{/if}
  {#if showForm}<TradeForm {accounts} trade={editing} close={() => showForm = false} saved={loadDashboard} />{/if}
</main>

<style>
  .controls{display:grid;grid-template-columns:1fr 1.4fr;gap:10px;margin-bottom:14px}.summary{margin-bottom:18px}.summary h2{margin:9px 0 0;font-size:1.45rem}.summary .muted{font-size:.75rem}.tabs{display:flex;gap:5px;background:#0d192b;padding:5px;border-radius:13px;margin:0 0 14px;width:max-content}.tabs button{border:0;background:transparent;color:#8290a7;padding:8px 19px;border-radius:9px;cursor:pointer}.tabs .active{background:#2474ff;color:white}.trades{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}@media(max-width:550px){.controls{grid-template-columns:1fr}}
</style>

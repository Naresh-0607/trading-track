<script lang="ts">
  import type { Account, Trade } from '$lib/types';
  import { tradesApi } from '$lib/api';

  export let accounts: Account[];
  export let trade: Trade | null = null;
  export let close: () => void;
  export let saved: () => void;

  let form = {
    account_id: trade?.account_id || accounts[0]?.id || '',
    trade_date: trade?.trade_date.slice(0, 16) || new Date().toISOString().slice(0, 16),
    symbol: trade?.symbol || '', asset_type: trade?.asset_type || 'FOREX', side: trade?.side || 'BUY',
    volume: trade?.volume || '', open_price: trade?.open_price || '', close_price: trade?.close_price || '',
    stop_loss: trade?.stop_loss || '', take_profit: trade?.take_profit || '', comments: trade?.comments || ''
  };
  let error = '';
  let loading = false;

  $: calculatedPnl = calculatePnl();

  function calculatePnl() {
    const volume = Number(form.volume), openPrice = Number(form.open_price), closePrice = Number(form.close_price);
    if (!form.close_price || !Number.isFinite(volume) || !Number.isFinite(openPrice) || !Number.isFinite(closePrice)) return null;
    return (form.side === 'BUY' ? closePrice - openPrice : openPrice - closePrice) * volume;
  }

  async function submit() {
    loading = true; error = '';
    const nullable = ['close_price', 'stop_loss', 'take_profit', 'comments'];
    const body = Object.fromEntries(Object.entries(form).map(([key, value]) => [key, value === '' && nullable.includes(key) ? null : value]));
    try {
      trade ? await tradesApi.update(trade.id, body) : await tradesApi.create(body);
      saved(); close();
    } catch (caught) {
      error = caught instanceof Error ? caught.message : 'Could not save trade';
    } finally { loading = false; }
  }
</script>

<div class="modal" role="presentation" onclick={(event) => event.currentTarget === event.target && close()}>
  <section class="sheet">
    <header><div><div class="eyebrow">{trade ? 'Update entry' : 'New entry'}</div><h2>{trade ? 'Edit trade' : 'Add trade'}</h2></div><button class="btn secondary" onclick={close}>Close</button></header>
    <form class="grid form-grid" onsubmit={(event) => { event.preventDefault(); submit(); }}>
      <label class="field"><span>Account *</span><select bind:value={form.account_id} required>{#each accounts as account}<option value={account.id}>{account.name}</option>{/each}</select></label>
      <label class="field"><span>Date *</span><input type="datetime-local" bind:value={form.trade_date} required /></label>
      <label class="field"><span>Symbol *</span><input bind:value={form.symbol} placeholder="EUR/USD" required /></label>
      <label class="field"><span>Asset type</span><select bind:value={form.asset_type}>{#each ['FOREX', 'STOCK', 'CRYPTO', 'COMMODITY', 'INDEX', 'OTHER'] as type}<option>{type}</option>{/each}</select></label>
      <label class="field"><span>Side *</span><select bind:value={form.side}><option>BUY</option><option>SELL</option></select></label>
      <label class="field"><span>Volume / lots *</span><input type="number" step="any" min="0.000001" bind:value={form.volume} required /></label>
      <label class="field"><span>Open price *</span><input type="number" step="any" min="0" bind:value={form.open_price} required /></label>
      <label class="field"><span>Close price</span><input type="number" step="any" min="0" bind:value={form.close_price} /></label>
      <label class="field"><span>Stop loss</span><input type="number" step="any" min="0" bind:value={form.stop_loss} /></label>
      <label class="field"><span>Take profit</span><input type="number" step="any" min="0" bind:value={form.take_profit} /></label>
      <label class="field"><span>P&amp;L (calculated)</span><input value={calculatedPnl === null ? 'Open trade' : calculatedPnl.toFixed(2)} readonly /></label>
      <label class="field"><span>Comments</span><textarea bind:value={form.comments}></textarea></label>
      {#if error}<p class="error">{error}</p>{/if}<button class="btn" disabled={loading}>{loading ? 'Saving…' : 'Save trade'}</button>
    </form>
  </section>
</div>

<style>header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px}h2{margin:.25rem 0}.form-grid{gap:13px}.form-grid button,.error{grid-column:1/-1}</style>

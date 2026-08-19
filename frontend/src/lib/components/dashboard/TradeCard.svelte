<script lang="ts">
  import type { Account, Trade } from '$lib/types';
  import { tradesApi } from '$lib/api';
  import { Pencil, Trash2 } from 'lucide-svelte';

  export let trade: Trade;
  export let account: Account | undefined;
  export let edit: () => void;
  export let removed: () => void;

  async function remove() {
    if (confirm(`Delete ${trade.symbol} trade?`)) {
      await tradesApi.remove(trade.id);
      removed();
    }
  }
</script>

<article class="card trade-card">
  <header>
    <div class="instrument">
      <strong>{trade.symbol}</strong>
      <span class:buy={trade.side === 'BUY'} class:sell={trade.side === 'SELL'}>{trade.side}</span>
    </div>
    <strong class="result" class:profit={trade.pnl !== null && Number(trade.pnl) >= 0} class:loss={trade.pnl !== null && Number(trade.pnl) < 0}>
      {trade.pnl === null ? 'Open' : `${Number(trade.pnl) >= 0 ? '+' : ''}${account?.currency || '$'} ${Number(trade.pnl).toFixed(2)}`}
    </strong>
  </header>

  <div class="tags">
    <span>{account?.name || 'Account'}</span>
    <span>{trade.asset_type}</span>
    <span>{new Date(trade.trade_date).toLocaleDateString()}</span>
  </div>

  <div class="details">
    <div><small>Volume</small><strong>{Number(trade.volume).toLocaleString(undefined, { maximumFractionDigits: 6 })}</strong></div>
    <div><small>Open</small><strong>{Number(trade.open_price).toLocaleString(undefined, { maximumFractionDigits: 8 })}</strong></div>
    <div><small>Close</small><strong>{trade.close_price === null ? '—' : Number(trade.close_price).toLocaleString(undefined, { maximumFractionDigits: 8 })}</strong></div>
  </div>

  {#if trade.comments}<p>{trade.comments}</p>{/if}

  <footer>
    <button onclick={edit}><Pencil size={16} /> Edit</button>
    <button class="delete" onclick={remove}><Trash2 size={16} /> Delete</button>
  </footer>
</article>

<style>
  .trade-card{display:grid;gap:15px}.trade-card header{display:flex;align-items:center;justify-content:space-between;gap:12px}.instrument{display:flex;align-items:center;gap:9px}.instrument>strong{font-size:1rem}.buy,.sell{border-radius:7px;padding:4px 7px;font-size:.64rem;font-weight:800;letter-spacing:.04em}.buy{background:#123b31;color:#35d07f}.sell{background:#3b1720;color:#ff6577}.result{font-size:.95rem}.tags{display:flex;flex-wrap:wrap;gap:7px}.tags span{border:1px solid #24364e;border-radius:999px;background:#101e31;color:#93a2b7;padding:5px 9px;font-size:.7rem}.details{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.details div{display:grid;min-width:0;gap:4px}.details small{color:#718198;font-size:.67rem}.details strong{overflow:hidden;color:#dce6f5;font-size:.78rem;text-overflow:ellipsis;white-space:nowrap}.trade-card p{margin:0;color:#a8b4c6;font-size:.82rem;line-height:1.5}.trade-card footer{display:flex;justify-content:flex-end;gap:8px;border-top:1px solid #1c2b42;padding-top:11px}.trade-card footer button{display:inline-flex;min-height:36px;align-items:center;gap:6px;border:0;border-radius:9px;background:#152338;color:#9ba8bb;padding:7px 10px;font-size:.74rem;cursor:pointer}.trade-card footer .delete{background:#271720;color:#e58b97}@media(max-width:380px){.details{grid-template-columns:1fr 1fr}.details div:last-child{display:none}}
</style>

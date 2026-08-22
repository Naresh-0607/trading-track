<script lang="ts">
  import { onMount } from 'svelte';
  import { ChevronLeft, ChevronRight, X } from 'lucide-svelte';
  import AppHeader from '$lib/components/common/AppHeader.svelte';
  import TradeCard from '$lib/components/dashboard/TradeCard.svelte';
  import { accountsApi, calendarApi } from '$lib/api';
  import type { Account, CalendarDayDetail, CalendarDaySummary } from '$lib/types';

  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const now = new Date();
  const today = dateKey(now.getFullYear(), now.getMonth() + 1, now.getDate());

  let year = now.getFullYear();
  let month = now.getMonth() + 1;
  let summaries: CalendarDaySummary[] = [];
  let accounts: Account[] = [];
  let loading = true;
  let error = '';
  let selectedDate: string | null = null;
  let detail: CalendarDayDetail | null = null;
  let detailLoading = false;
  let detailError = '';

  $: monthTitle = new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' }).format(new Date(year, month - 1, 1));
  $: cells = calendarCells(year, month);
  $: summariesByDate = new Map(summaries.map((summary) => [summary.date, summary]));

  function dateKey(yearValue: number, monthValue: number, day: number) {
    return `${yearValue}-${String(monthValue).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  }

  function calendarCells(yearValue: number, monthValue: number): (number | null)[] {
    const leading = new Date(yearValue, monthValue - 1, 1).getDay();
    const dayCount = new Date(yearValue, monthValue, 0).getDate();
    const values: (number | null)[] = [
      ...Array.from({ length: leading }, () => null),
      ...Array.from({ length: dayCount }, (_, index) => index + 1)
    ];
    while (values.length % 7) values.push(null);
    return values;
  }

  function money(value: string) {
    const amount = Number(value);
    return `${amount >= 0 ? '+' : '-'}$${Math.abs(amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  function shortMoney(value: string) {
    const amount = Number(value);
    const absolute = Math.abs(amount);
    const compact = absolute >= 1000
      ? absolute.toLocaleString(undefined, { notation: 'compact', maximumFractionDigits: 1 })
      : absolute.toFixed(2);
    return `${amount >= 0 ? '+' : '-'}$${compact}`;
  }

  function readableDate(value: string) {
    return new Intl.DateTimeFormat(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
      .format(new Date(`${value}T00:00:00`));
  }

  async function loadMonth() {
    loading = true;
    error = '';
    try {
      summaries = await calendarApi.month(year, month);
    } catch (reason) {
      error = reason instanceof Error ? reason.message : 'Could not load calendar';
    } finally {
      loading = false;
    }
  }

  async function loadInitial() {
    loading = true;
    error = '';
    try {
      [accounts, summaries] = await Promise.all([
        accountsApi.list(),
        calendarApi.month(year, month)
      ]);
    } catch (reason) {
      error = reason instanceof Error ? reason.message : 'Could not load calendar';
    } finally {
      loading = false;
    }
  }

  async function moveMonth(offset: number) {
    const next = new Date(year, month - 1 + offset, 1);
    year = next.getFullYear();
    month = next.getMonth() + 1;
    summaries = [];
    closeDetail();
    await loadMonth();
  }

  async function selectDay(value: string) {
    selectedDate = value;
    detail = null;
    detailError = '';
    detailLoading = true;
    try {
      const response = await calendarApi.day(value);
      if (selectedDate === value) detail = response;
    } catch (reason) {
      if (selectedDate === value) detailError = reason instanceof Error ? reason.message : 'Could not load this day';
    } finally {
      if (selectedDate === value) detailLoading = false;
    }
  }

  function closeDetail() {
    selectedDate = null;
    detail = null;
    detailError = '';
    detailLoading = false;
  }

  onMount(loadInitial);
</script>

<svelte:head><title>Calendar · Trade Track</title></svelte:head>
<svelte:window onkeydown={(event) => event.key === 'Escape' && selectedDate && closeDetail()} />

<main class="shell">
  <AppHeader title="Calendar" subtitle="See your trading performance day by day" />

  <section class="card calendar-card" aria-busy={loading}>
    <header class="month-header">
      <button class="month-button" aria-label="Previous month" disabled={loading} onclick={() => moveMonth(-1)}>
        <ChevronLeft size={21} />
      </button>
      <h2>{monthTitle}</h2>
      <button class="month-button" aria-label="Next month" disabled={loading} onclick={() => moveMonth(1)}>
        <ChevronRight size={21} />
      </button>
    </header>

    {#if error}<p class="error">{error}</p>{/if}

    <div class="weekdays" aria-hidden="true">
      {#each weekdays as weekday}<span>{weekday}</span>{/each}
    </div>
    <div class="calendar-grid" class:calendar-loading={loading}>
      {#each cells as day}
        {#if day === null}
          <div class="blank" aria-hidden="true"></div>
        {:else}
          {@const key = dateKey(year, month, day)}
          {@const summary = summariesByDate.get(key)}
          <button
            class="day"
            class:today={key === today}
            class:profit-day={summary && Number(summary.pnl) > 0}
            class:loss-day={summary && Number(summary.pnl) < 0}
            aria-label={`${readableDate(key)}${summary ? `, ${money(summary.pnl)}, ${summary.trade_count} trades` : ', no trades'}`}
            onclick={() => selectDay(key)}
          >
            <span class="date-number">{day}</span>
            {#if summary}
              <span class="day-pnl">{shortMoney(summary.pnl)}</span>
              <span class="trade-count">{summary.trade_count} {summary.trade_count === 1 ? 'trade' : 'trades'}</span>
            {/if}
          </button>
        {/if}
      {/each}
    </div>
  </section>

  <div class="legend" aria-label="Calendar legend">
    <span><i class="profit-dot"></i> Profit</span>
    <span><i class="loss-dot"></i> Loss</span>
    <span><i class="neutral-dot"></i> Neutral / no trades</span>
  </div>
</main>

{#if selectedDate}
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="day-title" tabindex="-1" onclick={(event) => event.target === event.currentTarget && closeDetail()} onkeydown={(event) => event.key === 'Escape' && closeDetail()}>
    <section class="sheet day-sheet">
      <header class="detail-header">
        <div>
          <div class="eyebrow">Daily details</div>
          <h2 id="day-title">{readableDate(selectedDate)}</h2>
        </div>
        <button class="close-button" aria-label="Close details" onclick={closeDetail}><X size={20} /></button>
      </header>

      {#if detailLoading}
        <div class="empty">Loading day details…</div>
      {:else if detailError}
        <p class="error">{detailError}</p>
      {:else if detail}
        <section class="detail-summary">
          <div>
            <span>Total P&amp;L</span>
            <strong class:profit={detail.status === 'profit'} class:loss={detail.status === 'loss'}>{money(detail.pnl)}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong class:profit={detail.status === 'profit'} class:loss={detail.status === 'loss'}>{detail.status[0].toUpperCase() + detail.status.slice(1)}</strong>
          </div>
          <div>
            <span>Total trades</span>
            <strong>{detail.trade_count}</strong>
          </div>
        </section>

        {#if detail.trades.length}
          <div class="trade-list">
            {#each detail.trades as trade}
              <TradeCard {trade} account={accounts.find((account) => account.id === trade.account_id)} showActions={false} />
            {/each}
          </div>
        {:else}
          <div class="empty no-trades"><h3>No trades on this date</h3><p>Select another day to review its activity.</p></div>
        {/if}
      {/if}
    </section>
  </div>
{/if}

<style>
  .calendar-card{padding:18px}.month-header{display:grid;grid-template-columns:44px 1fr 44px;align-items:center;gap:12px;margin-bottom:18px}.month-header h2{margin:0;text-align:center;font-size:1.18rem}.month-button,.close-button{display:grid;width:44px;height:44px;place-items:center;border:1px solid #26384f;border-radius:13px;background:#101e31;color:#cdd8e8;cursor:pointer}.month-button:disabled{cursor:wait;opacity:.5}.weekdays,.calendar-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr))}.weekdays{margin-bottom:8px}.weekdays span{text-align:center;color:#718198;font-size:.68rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase}.calendar-grid{gap:8px;transition:opacity .15s ease}.calendar-loading{opacity:.55}.day,.blank{min-height:102px}.day{display:flex;min-width:0;flex-direction:column;align-items:flex-start;gap:7px;box-sizing:border-box;border:1px solid #1e3048;border-radius:15px;background:rgba(8,19,34,.88);color:#dfe8f5;padding:11px;cursor:pointer;text-align:left;transition:border-color .15s ease,background .15s ease,transform .15s ease}.day:hover{border-color:#41658f;background:#10223a;transform:translateY(-1px)}.date-number{display:grid;width:28px;height:28px;place-items:center;border-radius:9px;font-size:.85rem;font-weight:750}.today .date-number{background:#2474ff;color:white}.day-pnl{max-width:100%;overflow:hidden;font-size:.78rem;font-weight:800;text-overflow:ellipsis;white-space:nowrap}.trade-count{color:#8493a8;font-size:.64rem}.profit-day{border-color:rgba(53,208,127,.34);background:linear-gradient(145deg,rgba(24,94,69,.34),rgba(8,25,31,.92))}.profit-day .day-pnl{color:#48dc8e}.loss-day{border-color:rgba(255,101,119,.34);background:linear-gradient(145deg,rgba(104,33,48,.32),rgba(29,16,29,.92))}.loss-day .day-pnl{color:#ff7b8a}.legend{display:flex;flex-wrap:wrap;gap:17px;margin:14px 3px;color:#8391a5;font-size:.73rem}.legend span{display:flex;align-items:center;gap:7px}.legend i{width:8px;height:8px;border-radius:50%}.profit-dot{background:#35d07f}.loss-dot{background:#ff6577}.neutral-dot{background:#52637b}.day-sheet{width:min(760px,100%)}.detail-header{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:18px}.detail-header h2{margin:5px 0 0;font-size:1.2rem}.close-button{flex:0 0 auto}.detail-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}.detail-summary>div{display:grid;gap:7px;border:1px solid #20324a;border-radius:15px;background:#091524;padding:13px}.detail-summary span{color:#8290a7;font-size:.7rem}.detail-summary strong{font-size:1rem}.trade-list{display:grid;gap:12px}.trade-list :global(.trade-card){box-shadow:none}.no-trades{padding-bottom:20px}.no-trades p{margin-bottom:0}
  @media(max-width:650px){.calendar-card{padding:12px}.month-header{margin:2px 2px 15px}.calendar-grid{gap:4px}.day,.blank{min-height:78px}.day{gap:4px;border-radius:11px;padding:7px 5px}.date-number{width:25px;height:25px;font-size:.78rem}.day-pnl{font-size:.63rem}.trade-count{display:none}.weekdays span{font-size:.6rem}.detail-summary{grid-template-columns:1fr 1fr}.detail-summary>div:first-child{grid-column:span 2}}
  @media(max-width:380px){.calendar-card{padding:9px}.calendar-grid{gap:3px}.day,.blank{min-height:70px}.day{padding:5px 4px}.day-pnl{font-size:.58rem}.month-header h2{font-size:1.05rem}}
</style>

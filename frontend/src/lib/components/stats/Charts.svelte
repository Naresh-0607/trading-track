<script lang="ts">
 import { onMount } from 'svelte';
 import Chart from 'chart.js/auto';
 import type { Stats } from '$lib/types';
 export let stats: Stats;
 let line: HTMLCanvasElement; let bars: HTMLCanvasElement; let donut: HTMLCanvasElement;
 let charts: Chart[] = [];
 const common = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#93a2b7' } } }, scales: { x: { ticks: { color: '#718198' }, grid: { color: '#18263a' } }, y: { ticks: { color: '#718198' }, grid: { color: '#18263a' } } } };

 function refresh() {
  if (!charts.length) return;
  charts[0].data.labels = stats.pnl_history.map((x) => x.date);
  charts[0].data.datasets[0].data = stats.pnl_history.map((x) => Number(x.cumulative_pnl));
  charts[1].data.labels = stats.account_performance.map((x) => x.name);
  charts[1].data.datasets[0].data = stats.account_performance.map((x) => Number(x.pnl));
  charts[1].data.datasets[0].backgroundColor = stats.account_performance.map((x) => Number(x.pnl) >= 0 ? '#35d07f' : '#ff6577');
  charts[2].data.datasets[0].data = [stats.buy_count, stats.sell_count];
  charts.forEach((chart) => chart.update());
 }
 $: stats, refresh();

 onMount(() => {
  charts = [
   new Chart(line, { type: 'line', data: { labels: [], datasets: [{ label: 'Cumulative P&L', data: [], borderColor: '#3b82f6', backgroundColor: '#3b82f622', fill: true, tension: .35 }] }, options: common }),
   new Chart(bars, { type: 'bar', data: { labels: [], datasets: [{ label: 'P&L', data: [], backgroundColor: [], borderRadius: 7 }] }, options: common }),
   new Chart(donut, { type: 'doughnut', data: { labels: ['Buy', 'Sell'], datasets: [{ data: [], backgroundColor: ['#3b82f6', '#a855f7'], borderWidth: 0 }] }, options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { color: '#93a2b7' } } } } })
  ];
  refresh();
  return () => charts.forEach((chart) => chart.destroy());
 });
</script>
<section class="charts">
 <div class="card line"><h3>P&amp;L performance</h3><div><canvas bind:this={line}></canvas></div></div>
 <div class="card"><h3>Account performance</h3><div><canvas bind:this={bars}></canvas></div></div>
 <div class="card"><h3>Buy vs sell</h3><div><canvas bind:this={donut}></canvas></div></div>
</section>
<style>.charts{display:grid;grid-template-columns:1fr 1fr;gap:14px}.line{grid-column:1/-1}.card>div{height:250px}h3{font-size:.9rem}@media(max-width:650px){.charts{grid-template-columns:1fr}.line{grid-column:auto}.card>div{height:220px}}</style>

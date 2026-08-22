<script lang="ts">
  import { page } from '$app/state';
  import { LayoutDashboard, WalletCards, CalendarDays, ChartNoAxesCombined } from 'lucide-svelte';

  const links = [
    ['/dashboard', 'Dashboard', LayoutDashboard],
    ['/accounts', 'Accounts', WalletCards],
    ['/calendar', 'Calendar', CalendarDays],
    ['/stats', 'Stats', ChartNoAxesCombined]
  ] as const;
</script>

<nav aria-label="Primary navigation">
  {#each links as [href, label, Icon]}
    <a class:active={page.url.pathname.startsWith(href)} {href} aria-current={page.url.pathname.startsWith(href) ? 'page' : undefined}>
      <Icon size={21} strokeWidth={2.2} />
      <span>{label}</span>
    </a>
  {/each}
</nav>

<style>
  nav {
    position: fixed;
    z-index: 30;
    left: 50%;
    bottom: calc(env(safe-area-inset-bottom, 0px) + 16px);
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    width: min(calc(100% - 40px), 560px);
    height: 68px;
    box-sizing: border-box;
    transform: translateX(-50%);
    overflow: hidden;
    border: 1px solid #263851;
    border-radius: 22px;
    background: rgba(9, 20, 35, .94);
    box-shadow: 0 16px 42px rgba(0, 0, 0, .38);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
  }

  a {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    color: #7f8da4;
    font-size: .72rem;
    font-weight: 600;
    text-decoration: none;
  }

  a::before {
    position: absolute;
    top: 0;
    width: 34px;
    height: 3px;
    border-radius: 0 0 4px 4px;
    background: transparent;
    content: '';
  }

  a.active { background: rgba(36, 116, 255, .08); color: #5d98ff; }
  a.active::before { background: #3f85ff; }

  @media (min-width: 800px) {
    nav { bottom: 18px; }
  }
</style>

import { NavLink, Outlet } from "react-router-dom";
import { logout } from "../api/client";

const links = [
  ["Dashboard", "/app"],
  ["Workspace", "/app/workspace"],
  ["Market analysis", "/app/market"],
  ["Stock screening", "/app/scanner"],
  ["Backtest analytics", "/app/backtest"],
  ["Compare datasets", "/app/compare"],
  ["Data quality", "/app/data-quality"],
  ["Research runs", "/app/runs"],
];

type AppShellProps = { onLogout: () => void };

export default function AppShell({ onLogout }: AppShellProps) {
  async function signOut() {
    await logout();
    onLogout();
  }

  return (
    <>
      <header className="topbar">
        <NavLink to="/" className="brand">
          <strong>AlgoResearch</strong>
          <span>Research workspace</span>
        </NavLink>
        <div className="shell-actions"><div className="sub">Not a broker · Not live trading · Not investment advice</div><button className="btn secondary" onClick={signOut}>Sign out</button></div>
      </header>
      <div className="layout">
        <aside className="sidenav">
          <p>Workflow</p>
          {links.map(([label, href]) => (
            <NavLink key={href} to={href} end={href === "/app"}>
              {label}
            </NavLink>
          ))}
          <p>Context</p>
          <NavLink to="/why">Industry problem</NavLink>
          <NavLink to="/methodology">Methodology</NavLink>
        </aside>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </>
  );
}

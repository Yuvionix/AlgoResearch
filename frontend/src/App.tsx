import { NavLink, Outlet, Route, Routes } from "react-router-dom";
import Landing from "./pages/Landing";
import Why from "./pages/Why";
import Methodology from "./pages/Methodology";
import Disclaimer from "./pages/Disclaimer";
import AppShell from "./pages/AppShell";
import Dashboard from "./pages/Dashboard";
import Market from "./pages/Market";
import Scanner from "./pages/Scanner";
import SymbolDetail from "./pages/SymbolDetail";
import Backtest from "./pages/Backtest";
import Compare from "./pages/Compare";
import Workspace from "./pages/Workspace";
import Runs from "./pages/Runs";
import DataQuality from "./pages/DataQuality";
import Login from "./pages/Login";
import { getAuthState } from "./api/client";
import { useEffect, useState } from "react";

export default function App() {
  const [authState, setAuthState] = useState<boolean | null>(null);
  useEffect(() => { getAuthState().then((data) => setAuthState(data.authenticated)).catch(() => setAuthState(false)); }, []);
  if (authState === null) return <div className="loading-screen">Loading workspace...</div>;
  if (!authState) return <Login onSuccess={() => setAuthState(true)} />;
  return (
    <Routes>
      <Route element={<MarketingFrame />}>
        <Route path="/" element={<Landing />} />
        <Route path="/why" element={<Why />} />
        <Route path="/methodology" element={<Methodology />} />
        <Route path="/disclaimer" element={<Disclaimer />} />
      </Route>
      <Route path="/app" element={<AppShell onLogout={() => setAuthState(false)} />}>
        <Route index element={<Dashboard />} />
        <Route path="market" element={<Market />} />
        <Route path="scanner" element={<Scanner />} />
        <Route path="scanner/:symbol" element={<SymbolDetail />} />
        <Route path="backtest" element={<Backtest />} />
        <Route path="compare" element={<Compare />} />
        <Route path="workspace" element={<Workspace />} />
        <Route path="runs" element={<Runs />} />
        <Route path="data-quality" element={<DataQuality />} />
      </Route>
    </Routes>
  );
}

function MarketingFrame() {
  return (
    <>
      <header className="topbar">
        <NavLink to="/" className="brand">
          <strong>AlgoResearch</strong>
          <span>Research & analytics</span>
        </NavLink>
        <nav className="nav">
          <NavLink to="/why">Why this platform</NavLink>
          <NavLink to="/methodology">Methodology</NavLink>
          <NavLink to="/disclaimer">Disclaimer</NavLink>
          <NavLink to="/app">Open workspace</NavLink>
        </nav>
      </header>
      <Outlet />
    </>
  );
}

import { useState } from "react";
import type { FormEvent } from "react";
import { login } from "../api/client";

type LoginProps = { onSuccess: () => void };

export default function Login({ onSuccess }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      onSuccess();
    } catch (requestError: any) {
      setError(requestError.response?.data?.message || "Unable to sign in.");
    }
  }

  return (
    <main className="login-page">
      <form className="card login-card" onSubmit={submit}>
        <p className="kicker">AlgoResearch</p>
        <h1>Sign in to research workspace</h1>
        <p className="lede">Use the account configured for this deployment.</p>
        <label className="field">
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" required />
        </label>
        <label className="field">
          Password
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn" type="submit">Sign in</button>
      </form>
    </main>
  );
}

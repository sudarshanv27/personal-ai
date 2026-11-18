import { useState } from "react";
import { login, saveTokens } from "./api";

function Login({ onLogin }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();

        setError("");
        setLoading(true);

        try {
            const data = await login(
                email,
                password
            );

            saveTokens(
                data.access_token,
                data.refresh_token
            );

            onLogin(data.user);
        } catch (error) {
            setError(
                error.message || "Login failed"
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="login-page">
            <div className="login-card">

                <div className="login-logo">
                    AI
                </div>

                <h1>Personal AI</h1>

                <p className="login-subtitle">
                    Sign in to your private AI assistant
                </p>

                <form onSubmit={handleSubmit}>

                    <label>
                        Email
                    </label>

                    <input
                        type="email"
                        value={email}
                        onChange={(event) =>
                            setEmail(event.target.value)
                        }
                        placeholder="Enter your email"
                        required
                    />

                    <label>
                        Password
                    </label>

                    <input
                        type="password"
                        value={password}
                        onChange={(event) =>
                            setPassword(event.target.value)
                        }
                        placeholder="Enter your password"
                        required
                    />

                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Signing in..."
                            : "Sign In"}
                    </button>

                </form>

            </div>
        </div>
    );
}

export default Login;
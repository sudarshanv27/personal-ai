// ============================================================
// API CONFIGURATION
// ============================================================

export const API_BASE_URL =
    "http://127.0.0.1:8000/api";


// ============================================================
// TOKEN STORAGE
// ============================================================

export function getAccessToken() {
    return localStorage.getItem(
        "access_token"
    );
}


export function getRefreshToken() {
    return localStorage.getItem(
        "refresh_token"
    );
}


export function saveTokens(
    accessToken,
    refreshToken
) {
    localStorage.setItem(
        "access_token",
        accessToken
    );

    localStorage.setItem(
        "refresh_token",
        refreshToken
    );
}


export function clearTokens() {
    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "refresh_token"
    );
}


// ============================================================
// LOGIN
// ============================================================

export async function login(
    email,
    password
) {
    const response =
        await fetch(
            `${API_BASE_URL}/auth/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    email,
                    password,
                }),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Login failed."
        );
    }

    return data;
}


// ============================================================
// REFRESH ACCESS TOKEN
// ============================================================

export async function refreshAccessToken() {
    const refreshToken =
        getRefreshToken();

    if (!refreshToken) {
        throw new Error(
            "No refresh token available."
        );
    }

    const response =
        await fetch(
            `${API_BASE_URL}/auth/refresh`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    refresh_token:
                        refreshToken,
                }),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {
        clearTokens();

        throw new Error(
            data.detail ||
            "Session expired. Please login again."
        );
    }

    saveTokens(
        data.access_token,
        refreshToken
    );

    return data.access_token;
}


// ============================================================
// AUTHENTICATED FETCH
// ============================================================

export async function authenticatedFetch(
    endpoint,
    options = {},
    retry = true
) {
    let accessToken =
        getAccessToken();

    if (!accessToken) {
        throw new Error(
            "Authentication required."
        );
    }

    const headers = {
        ...(options.headers || {}),

        Authorization:
            `Bearer ${accessToken}`,
    };

    let response =
        await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,
                headers,
            }
        );


    // ==========================================================
    // ACCESS TOKEN EXPIRED
    // ==========================================================

    if (
        response.status === 401 &&
        retry
    ) {
        try {
            accessToken =
                await refreshAccessToken();

            const retryHeaders = {
                ...(options.headers || {}),

                Authorization:
                    `Bearer ${accessToken}`,
            };

            response =
                await fetch(
                    `${API_BASE_URL}${endpoint}`,
                    {
                        ...options,
                        headers:
                            retryHeaders,
                    }
                );

        } catch (refreshError) {
            clearTokens();

            throw refreshError;
        }
    }

    return response;
}


// ============================================================
// GET CONVERSATIONS
// ============================================================

export async function getConversations() {
    const response =
        await authenticatedFetch(
            "/conversations"
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Failed to load conversations."
        );
    }

    return data;
}


// ============================================================
// CREATE CONVERSATION
// ============================================================

export async function createConversation(
    title = "New Conversation",
    systemPrompt =
        "You are my private personal AI assistant."
) {
    const response =
        await authenticatedFetch(
            "/conversations",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    title,
                    system_prompt:
                        systemPrompt,
                }),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Failed to create conversation."
        );
    }

    return data;
}


// ============================================================
// GET SINGLE CONVERSATION
// ============================================================

export async function getConversation(
    conversationId
) {
    const response =
        await authenticatedFetch(
            `/conversations/${conversationId}`
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Failed to load conversation."
        );
    }

    return data;
}


// ============================================================
// UPDATE / RENAME CONVERSATION
// ============================================================

export async function updateConversation(
    conversationId,
    title
) {
    const response =
        await authenticatedFetch(
            `/conversations/${conversationId}`,
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    title,
                }),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Failed to update conversation."
        );
    }

    return data;
}


// ============================================================
// DELETE CONVERSATION
// ============================================================

export async function deleteConversation(
    conversationId
) {
    const response =
        await authenticatedFetch(
            `/conversations/${conversationId}`,
            {
                method: "DELETE",
            }
        );

    if (!response.ok) {
        let data = {};

        try {
            data =
                await response.json();
        } catch {
            // DELETE may return
            // an empty response body.
        }

        throw new Error(
            data.detail ||
            "Failed to delete conversation."
        );
    }

    return true;
}


// ============================================================
// GET CONVERSATION MESSAGES
// ============================================================

export async function getConversationMessages(
    conversationId
) {
    const response =
        await authenticatedFetch(
            `/conversations/${conversationId}/messages`
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Failed to load messages."
        );
    }

    return data;
}


// ============================================================
// CREATE NORMAL MESSAGE
// ============================================================

export async function createMessage(
    conversationId,
    content
) {
    const response =
        await authenticatedFetch(
            `/conversations/${conversationId}/messages`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    content,
                }),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Failed to send message."
        );
    }

    return data;
}


// ============================================================
// DELETE MESSAGE
// ============================================================

export async function deleteMessage(
    conversationId,
    messageId
) {
    const response =
        await authenticatedFetch(
            `/conversations/${conversationId}/messages/${messageId}`,
            {
                method: "DELETE",
            }
        );

    if (!response.ok) {
        let data = {};

        try {
            data =
                await response.json();
        } catch {
            // Empty DELETE response.
        }

        throw new Error(
            data.detail ||
            "Failed to delete message."
        );
    }

    return true;
}


// ============================================================
// PROCESS SSE EVENT
// ============================================================

function processSSEEvent(
    eventBlock,
    onToken,
    onDone,
    onError
) {
    if (!eventBlock.trim()) {
        return;
    }

    const lines =
        eventBlock.split("\n");

    let eventType =
        "message";

    let dataText =
        "";

    for (const line of lines) {

        if (
            line.startsWith(
                "event:"
            )
        ) {
            eventType =
                line
                    .slice(6)
                    .trim();
        }

        if (
            line.startsWith(
                "data:"
            )
        ) {
            dataText +=
                line
                    .slice(5)
                    .trim();
        }
    }

    if (!dataText) {
        return;
    }

    let data;

    try {
        data =
            JSON.parse(dataText);
    } catch {
        console.error(
            "Invalid SSE JSON:",
            dataText
        );

        return;
    }


    // ==========================================================
    // TOKEN
    // ==========================================================

    if (
        eventType ===
        "token"
    ) {
        if (
            typeof onToken ===
            "function"
        ) {
            onToken(
                data.content || ""
            );
        }

        return;
    }


    // ==========================================================
    // DONE
    // ==========================================================

    if (
        eventType ===
        "done"
    ) {
        if (
            typeof onDone ===
            "function"
        ) {
            onDone(data);
        }

        return;
    }


    // ==========================================================
    // ERROR
    // ==========================================================

    if (
        eventType ===
        "error"
    ) {
        if (
            typeof onError ===
            "function"
        ) {
            onError(data);
        }

        return;
    }
}


// ============================================================
// STREAM MESSAGE
// ============================================================

export async function streamMessage(
    conversationId,
    content,
    onToken,
    onDone,
    onError,
    signal,
    retry = true
) {
    let accessToken =
        getAccessToken();

    if (!accessToken) {
        throw new Error(
            "Authentication required."
        );
    }


    async function makeRequest(
        token
    ) {
        return fetch(
            `${API_BASE_URL}/conversations/${conversationId}/messages/stream`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    Accept:
                        "text/event-stream",

                    Authorization:
                        `Bearer ${token}`,
                },

                body: JSON.stringify({
                    content,
                }),

                signal,
            }
        );
    }


    let response =
        await makeRequest(
            accessToken
        );


    // ==========================================================
    // TOKEN EXPIRED
    // ==========================================================

    if (
        response.status === 401 &&
        retry
    ) {
        try {
            accessToken =
                await refreshAccessToken();

            response =
                await makeRequest(
                    accessToken
                );

        } catch (error) {
            clearTokens();

            throw error;
        }
    }


    // ==========================================================
    // HTTP ERROR
    // ==========================================================

    if (!response.ok) {
        let data = {};

        try {
            data =
                await response.json();
        } catch {
            // Response may not contain JSON.
        }

        throw new Error(
            data.detail ||
            "Failed to start AI stream."
        );
    }


    // ==========================================================
    // STREAM BODY
    // ==========================================================

    if (!response.body) {
        throw new Error(
            "Streaming is not supported by this response."
        );
    }


    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    let buffer =
        "";


    try {

        while (true) {

            const {
                value,
                done,
            } =
                await reader.read();

            if (done) {
                break;
            }

            buffer +=
                decoder.decode(
                    value,
                    {
                        stream:
                            true,
                    }
                );


            const events =
                buffer.split(
                    "\n\n"
                );

            buffer =
                events.pop() || "";


            for (
                const eventBlock
                of events
            ) {

                processSSEEvent(
                    eventBlock,
                    onToken,
                    onDone,
                    onError
                );
            }
        }


        // ========================================================
        // PROCESS REMAINING BUFFER
        // ========================================================

        if (
            buffer.trim()
        ) {
            processSSEEvent(
                buffer,
                onToken,
                onDone,
                onError
            );
        }

    } finally {
        reader.releaseLock();
    }
}
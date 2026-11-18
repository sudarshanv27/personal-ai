import {
  useEffect,
  useState,
} from "react";

import "./App.css";

import Login from "./Login";

import {
  getAccessToken,
  clearTokens,
  streamMessage,
  getConversations,
  getConversationMessages,
  createConversation as createConversationAPI,
  updateConversation,
  deleteConversation,
} from "./api";


function App() {
  // ============================================================
  // AUTHENTICATION
  // ============================================================

  const [authenticated, setAuthenticated] =
    useState(Boolean(getAccessToken()));

  const [user, setUser] =
    useState(null);


  // ============================================================
  // CONVERSATIONS
  // ============================================================

  const [conversationId, setConversationId] =
    useState(null);

  const [conversations, setConversations] =
    useState([]);

  const [loadingConversations, setLoadingConversations] =
    useState(false);

  const [loadingMessages, setLoadingMessages] =
    useState(false);


  // ============================================================
  // CONVERSATION MENU
  // ============================================================

  const [openMenuId, setOpenMenuId] =
    useState(null);

  const [editingConversationId, setEditingConversationId] =
    useState(null);

  const [editingTitle, setEditingTitle] =
    useState("");

  const [conversationActionLoading, setConversationActionLoading] =
    useState(false);


  // ============================================================
  // MESSAGES
  // ============================================================

  const [messages, setMessages] =
    useState([]);

  const [message, setMessage] =
    useState("");


  // ============================================================
  // STREAMING
  // ============================================================

  const [isStreaming, setIsStreaming] =
    useState(false);

  const [abortController, setAbortController] =
    useState(null);


  // ============================================================
  // ERRORS
  // ============================================================

  const [error, setError] =
    useState("");


  // ============================================================
  // LOAD CONVERSATIONS AFTER LOGIN
  // ============================================================

  useEffect(() => {
    if (!authenticated) {
      return;
    }

    loadConversations();
  }, [authenticated]);


  // ============================================================
  // CLOSE CONVERSATION MENU WHEN CLICKING OUTSIDE
  // ============================================================

  useEffect(() => {
    function handleDocumentClick() {
      setOpenMenuId(null);
    }

    if (openMenuId !== null) {
      document.addEventListener(
        "click",
        handleDocumentClick
      );
    }

    return () => {
      document.removeEventListener(
        "click",
        handleDocumentClick
      );
    };
  }, [openMenuId]);


  // ============================================================
  // LOAD CONVERSATIONS
  // ============================================================

  async function loadConversations() {
    try {
      setLoadingConversations(true);
      setError("");

      const data =
        await getConversations();

      const conversationList =
        Array.isArray(data)
          ? data
          : data?.conversations || [];

      setConversations(
        conversationList
      );

    } catch (error) {
      console.error(
        "Failed to load conversations:",
        error
      );

      setError(
        error.message ||
        "Failed to load conversations."
      );

    } finally {
      setLoadingConversations(false);
    }
  }


  // ============================================================
  // LOAD MESSAGES FOR A CONVERSATION
  // ============================================================

  async function loadConversationMessages(
    selectedConversationId
  ) {
    try {
      setLoadingMessages(true);
      setError("");

      const data =
        await getConversationMessages(
          selectedConversationId
        );

      const messageList =
        Array.isArray(data)
          ? data
          : data?.messages || [];

      const formattedMessages =
        messageList.map(
          (item) => ({
            id: item.id,
            conversation_id:
              item.conversation_id,
            role: item.role,
            content: item.content,
            model: item.model,
            created_at:
              item.created_at,
          })
        );

      setMessages(
        formattedMessages
      );

    } catch (error) {
      console.error(
        "Failed to load messages:",
        error
      );

      setError(
        error.message ||
        "Failed to load messages."
      );

    } finally {
      setLoadingMessages(false);
    }
  }


  // ============================================================
  // SELECT CONVERSATION
  // ============================================================

  async function handleSelectConversation(
    conversation
  ) {
    if (!conversation) {
      return;
    }

    if (isStreaming) {
      return;
    }

    if (conversationActionLoading) {
      return;
    }

    const selectedId =
      conversation.id;

    setOpenMenuId(null);
    setEditingConversationId(null);

    setConversationId(
      selectedId
    );

    setMessages([]);

    setError("");

    await loadConversationMessages(
      selectedId
    );
  }


  // ============================================================
  // LOGIN
  // ============================================================

  function handleLogin(userData) {
    setUser(userData);

    setAuthenticated(true);
  }


  // ============================================================
  // CREATE CONVERSATION
  // ============================================================

  async function createConversation() {
    const data =
      await createConversationAPI(
        "New Conversation",
        "You are my private personal AI assistant."
      );

    setConversationId(
      data.id
    );

    setMessages([]);

    setConversations(
      (previous) => {
        const alreadyExists =
          previous.some(
            (item) =>
              item.id === data.id
          );

        if (alreadyExists) {
          return previous;
        }

        return [
          data,
          ...previous,
        ];
      }
    );

    return data;
  }


  // ============================================================
  // START RENAME
  // ============================================================

  function startRenameConversation(
    conversation
  ) {
    if (!conversation) {
      return;
    }

    if (isStreaming) {
      return;
    }

    setOpenMenuId(null);

    setEditingConversationId(
      conversation.id
    );

    setEditingTitle(
      conversation.title ||
      "New Conversation"
    );
  }


  // ============================================================
  // CANCEL RENAME
  // ============================================================

  function cancelRenameConversation() {
    setEditingConversationId(
      null
    );

    setEditingTitle("");

    setOpenMenuId(null);
  }


  // ============================================================
  // SAVE RENAMED CONVERSATION
  // ============================================================

  async function saveRenameConversation(
    conversationIdToUpdate
  ) {
    const newTitle =
      editingTitle.trim();

    if (!newTitle) {
      setError(
        "Conversation title cannot be empty."
      );

      return;
    }

    try {
      setConversationActionLoading(
        true
      );

      setError("");

      const updatedConversation =
        await updateConversation(
          conversationIdToUpdate,
          newTitle
        );

      setConversations(
        (previous) =>
          previous.map(
            (conversation) =>
              conversation.id ===
                conversationIdToUpdate
                ? {
                  ...conversation,
                  ...updatedConversation,
                }
                : conversation
          )
      );

      setEditingConversationId(
        null
      );

      setEditingTitle("");

      setOpenMenuId(null);

    } catch (error) {
      console.error(
        "Failed to rename conversation:",
        error
      );

      setError(
        error.message ||
        "Failed to rename conversation."
      );

    } finally {
      setConversationActionLoading(
        false
      );
    }
  }


  // ============================================================
  // DELETE CONVERSATION
  // ============================================================

  async function handleDeleteConversation(
    conversation
  ) {
    if (!conversation) {
      return;
    }

    if (isStreaming) {
      return;
    }

    const confirmed =
      window.confirm(
        `Delete "${conversation.title || "New Conversation"}"?\n\nThis will permanently delete the conversation and its messages.`
      );

    if (!confirmed) {
      setOpenMenuId(null);
      return;
    }

    try {
      setConversationActionLoading(
        true
      );

      setError("");

      setOpenMenuId(null);

      await deleteConversation(
        conversation.id
      );

      setConversations(
        (previous) =>
          previous.filter(
            (item) =>
              item.id !==
              conversation.id
          )
      );

      if (
        conversationId ===
        conversation.id
      ) {
        setConversationId(
          null
        );

        setMessages([]);

        setMessage("");
      }

    } catch (error) {
      console.error(
        "Failed to delete conversation:",
        error
      );

      setError(
        error.message ||
        "Failed to delete conversation."
      );

    } finally {
      setConversationActionLoading(
        false
      );
    }
  }


  // ============================================================
  // SEND MESSAGE
  // ============================================================

  async function handleSend() {
    const content =
      message.trim();

    if (!content) {
      return;
    }

    if (isStreaming) {
      return;
    }

    setError("");

    let activeConversationId =
      conversationId;

    try {

      // ========================================================
      // CREATE CONVERSATION IF NECESSARY
      // ========================================================

      if (!activeConversationId) {
        const conversation =
          await createConversation();

        activeConversationId =
          conversation.id;
      }


      // ========================================================
      // ADD USER MESSAGE TO UI
      // ========================================================

      const userMessageId =
        `user-${Date.now()}`;

      setMessages(
        (previous) => [
          ...previous,
          {
            id:
              userMessageId,

            conversation_id:
              activeConversationId,

            role:
              "user",

            content,
          },
        ]
      );


      // Clear input
      setMessage("");


      // ========================================================
      // CREATE EMPTY ASSISTANT MESSAGE
      // ========================================================

      const assistantId =
        `assistant-${Date.now()}`;

      setMessages(
        (previous) => [
          ...previous,
          {
            id:
              assistantId,

            conversation_id:
              activeConversationId,

            role:
              "assistant",

            content:
              "",
          },
        ]
      );


      // ========================================================
      // CREATE ABORT CONTROLLER
      // ========================================================

      const controller =
        new AbortController();

      setAbortController(
        controller
      );

      setIsStreaming(true);


      // ========================================================
      // START SSE STREAM
      // ========================================================

      await streamMessage(

        activeConversationId,

        content,


        // ======================================================
        // TOKEN EVENT
        // ======================================================

        (token) => {

          setMessages(
            (previous) =>
              previous.map(
                (item) => {

                  if (
                    item.id !==
                    assistantId
                  ) {
                    return item;
                  }

                  return {
                    ...item,

                    content:
                      item.content +
                      token,
                  };
                }
              )
          );
        },


        // ======================================================
        // DONE EVENT
        // ======================================================

        (data) => {

          console.log(
            "AI generation complete:",
            data
          );

          loadConversationMessages(
            activeConversationId
          );

          loadConversations();
        },


        // ======================================================
        // ERROR EVENT
        // ======================================================

        (data) => {

          const errorMessage =
            data?.message ||
            "AI generation failed.";

          setError(
            errorMessage
          );

          setMessages(
            (previous) =>
              previous.filter(
                (item) =>
                  item.id !==
                  assistantId
              )
          );
        },


        // ======================================================
        // ABORT SIGNAL
        // ======================================================

        controller.signal
      );

    } catch (error) {

      if (
        error.name !==
        "AbortError"
      ) {

        console.error(
          "Send message error:",
          error
        );

        setError(
          error.message ||
          "Something went wrong."
        );
      }

    } finally {

      setIsStreaming(false);

      setAbortController(null);
    }
  }


  // ============================================================
  // STOP GENERATION
  // ============================================================

  function stopGeneration() {
    if (!abortController) {
      return;
    }

    abortController.abort();

    setAbortController(null);

    setIsStreaming(false);
  }


  // ============================================================
  // NEW CHAT
  // ============================================================

  function handleNewChat() {

    if (isStreaming) {
      stopGeneration();
    }

    setOpenMenuId(null);

    setEditingConversationId(
      null
    );

    setEditingTitle("");

    setConversationId(null);

    setMessages([]);

    setMessage("");

    setError("");
  }


  // ============================================================
  // LOGOUT
  // ============================================================

  function handleLogout() {

    if (isStreaming) {
      stopGeneration();
    }

    clearTokens();

    setAuthenticated(false);

    setUser(null);

    setConversationId(null);

    setConversations([]);

    setMessages([]);

    setMessage("");

    setError("");

    setOpenMenuId(null);

    setEditingConversationId(
      null
    );

    setEditingTitle("");
  }


  // ============================================================
  // LOGIN SCREEN
  // ============================================================

  if (!authenticated) {

    return (
      <Login
        onLogin={handleLogin}
      />
    );
  }


  // ============================================================
  // CHAT APPLICATION
  // ============================================================

  return (
    <div
      className="app"
      onClick={() => {
        if (openMenuId !== null) {
          setOpenMenuId(null);
        }
      }}
    >


      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="header">

        <div className="brand">

          <div className="logo">
            AI
          </div>

          <div>

            <h1>
              Personal AI
            </h1>

            <span className="status">

              <span className="status-dot"></span>

              Online

            </span>

          </div>

        </div>


        {/* ====================================================
            HEADER ACTIONS
            ==================================================== */}

        <div className="header-actions">

          <span className="user-info">
            {user?.username ||
              "sudarshan"}
          </span>

          <button
            className="logout-button"
            onClick={
              (event) => {
                event.stopPropagation();
                handleLogout();
              }
            }
          >
            Logout
          </button>

        </div>

      </header>


      {/* ======================================================
          MAIN
          ====================================================== */}

      <div className="main">


        {/* ====================================================
            SIDEBAR
            ==================================================== */}

        <aside className="sidebar">


          {/* ==================================================
              NEW CHAT
              ================================================== */}

          <button
            className="new-chat-button"
            onClick={
              (event) => {
                event.stopPropagation();
                handleNewChat();
              }
            }
            disabled={
              isStreaming ||
              conversationActionLoading
            }
          >
            + New Chat
          </button>


          {/* ==================================================
              SIDEBAR TITLE
              ================================================== */}

          <div className="sidebar-title">
            Conversations
          </div>


          {/* ==================================================
              LOADING
              ================================================== */}

          {loadingConversations ? (

            <div className="empty-conversations">
              Loading conversations...
            </div>

          ) : conversations.length === 0 ? (

            <div className="empty-conversations">
              No conversations yet
            </div>

          ) : (

            <div className="conversation-list">

              {conversations.map(
                (conversation) => {

                  const isEditing =
                    editingConversationId ===
                    conversation.id;

                  const isMenuOpen =
                    openMenuId ===
                    conversation.id;

                  return (

                    <div
                      key={
                        conversation.id
                      }

                      className={
                        `conversation-wrapper ${conversation.id ===
                          conversationId
                          ? "active"
                          : ""
                        }`
                      }

                      onClick={
                        (event) =>
                          event.stopPropagation()
                      }
                    >

                      {isEditing ? (

                        // ======================================
                        // RENAME MODE
                        // ======================================

                        <div className="conversation-edit">

                          <input
                            type="text"
                            value={
                              editingTitle
                            }

                            autoFocus

                            maxLength={255}

                            disabled={
                              conversationActionLoading
                            }

                            onChange={
                              (event) =>
                                setEditingTitle(
                                  event.target.value
                                )
                            }

                            onKeyDown={
                              (event) => {

                                if (
                                  event.key ===
                                  "Enter"
                                ) {
                                  event.preventDefault();

                                  saveRenameConversation(
                                    conversation.id
                                  );
                                }

                                if (
                                  event.key ===
                                  "Escape"
                                ) {
                                  event.preventDefault();

                                  cancelRenameConversation();
                                }
                              }
                            }
                          />

                          <button
                            className="rename-save-button"
                            onClick={() =>
                              saveRenameConversation(
                                conversation.id
                              )
                            }

                            disabled={
                              conversationActionLoading ||
                              !editingTitle.trim()
                            }

                            title="Save"
                          >
                            ✓
                          </button>

                          <button
                            className="rename-cancel-button"
                            onClick={
                              cancelRenameConversation
                            }

                            disabled={
                              conversationActionLoading
                            }

                            title="Cancel"
                          >
                            ×
                          </button>

                        </div>

                      ) : (

                        // ======================================
                        // NORMAL CONVERSATION ROW
                        // ======================================

                        <div className="conversation-row">

                          <button
                            className={
                              `conversation-item ${conversation.id ===
                                conversationId
                                ? "active"
                                : ""
                              }`
                            }

                            disabled={
                              isStreaming ||
                              conversationActionLoading
                            }

                            onClick={() =>
                              handleSelectConversation(
                                conversation
                              )
                            }
                          >

                            <span className="conversation-title">
                              {conversation.title ||
                                "New Conversation"}
                            </span>

                          </button>


                          {/* ==================================
                              THREE DOT MENU
                              ================================== */}

                          <button
                            className="conversation-menu-button"

                            disabled={
                              isStreaming ||
                              conversationActionLoading
                            }

                            onClick={
                              (event) => {

                                event.stopPropagation();

                                setOpenMenuId(
                                  (previous) =>
                                    previous ===
                                      conversation.id
                                      ? null
                                      : conversation.id
                                );
                              }
                            }

                            title="Conversation options"
                          >
                            ⋮
                          </button>


                          {/* ==================================
                              MENU
                              ================================== */}

                          {isMenuOpen && (

                            <div
                              className="conversation-menu"
                              onClick={
                                (event) =>
                                  event.stopPropagation()
                              }
                            >

                              <button
                                onClick={() =>
                                  startRenameConversation(
                                    conversation
                                  )
                                }
                              >
                                ✏️ Rename
                              </button>

                              <button
                                className="delete-menu-item"
                                onClick={() =>
                                  handleDeleteConversation(
                                    conversation
                                  )
                                }
                              >
                                🗑 Delete
                              </button>

                            </div>

                          )}

                        </div>

                      )}

                    </div>
                  );
                }
              )}

            </div>

          )}

        </aside>


        {/* ====================================================
            CHAT
            ==================================================== */}

        <section className="chat">


          {/* ==================================================
              CHAT CONTENT
              ================================================== */}

          <div className="chat-content">


            {/* =================================================
                LOADING MESSAGES
                ================================================= */}

            {loadingMessages ? (

              <div className="welcome">

                <div className="welcome-icon">
                  AI
                </div>

                <h2>
                  Loading conversation...
                </h2>

                <p>
                  Retrieving your messages.
                </p>

              </div>

            ) : messages.length === 0 ? (

              <div className="welcome">

                <div className="welcome-icon">
                  AI
                </div>

                <h2>
                  Welcome to Personal AI
                </h2>

                <p>
                  Your private AI assistant.
                  Ask questions, work with
                  your data, and build
                  intelligent workflows.
                </p>

              </div>

            ) : (

              <div className="messages">

                {messages.map(
                  (msg, index) => (

                    <div
                      key={
                        msg.id
                      }

                      className={
                        `message-row ${msg.role}`
                      }
                    >

                      <div className="message-avatar">

                        {msg.role ===
                          "user"
                          ? "You"
                          : "AI"}

                      </div>

                      <div className="message-content">

                        {msg.content}

                        {msg.role ===
                          "assistant" &&

                          isStreaming &&

                          index ===
                          messages.length -
                          1 && (

                            <span className="cursor">
                              ▌
                            </span>

                          )}

                      </div>

                    </div>
                  )
                )}

              </div>

            )}

          </div>


          {/* ==================================================
              ERROR
              ================================================== */}

          {error && (

            <div className="chat-error">

              {error}

            </div>

          )}


          {/* ==================================================
              INPUT AREA
              ================================================== */}

          <div className="input-area">

            <div className="input-container">

              <textarea
                value={
                  message
                }

                disabled={
                  isStreaming
                }

                onChange={
                  (event) =>
                    setMessage(
                      event.target.value
                    )
                }

                onKeyDown={
                  (event) => {

                    if (
                      event.key ===
                      "Enter" &&
                      !event.shiftKey
                    ) {

                      event.preventDefault();

                      handleSend();
                    }

                  }
                }

                placeholder={
                  isStreaming
                    ? "AI is responding..."
                    : "Ask me anything..."
                }

                rows="1"
              />


              {isStreaming ? (

                <button
                  className="stop-button"
                  onClick={
                    stopGeneration
                  }
                  title="Stop generation"
                >
                  ■
                </button>

              ) : (

                <button
                  className="send-button"
                  onClick={
                    handleSend
                  }
                  disabled={
                    !message.trim()
                  }
                  title="Send message"
                >
                  ➤
                </button>

              )}

            </div>


            <div className="input-hint">

              {isStreaming
                ? "AI is generating a response..."
                : "Enter to send · Shift + Enter for new line"}

            </div>

          </div>

        </section>

      </div>

    </div>
  );
}


export default App;
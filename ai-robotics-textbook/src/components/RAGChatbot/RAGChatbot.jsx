import React, { useState, useRef, useEffect } from 'react';
import styles from './RAGChatbot.module.css';

export default function RAGChatbot() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your Textbook Assistant. I can help you with questions about physical systems, robotics, computer vision, motion planning, and more. Ask me anything about the content!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [apiUrl, setApiUrl] = useState('http://localhost:8001');
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Try to detect selected text
    const handleTextSelection = () => {
      const selected = window.getSelection().toString();
      if (selected) {
        setSelectedText(selected);
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('touchend', handleTextSelection);

    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('touchend', handleTextSelection);
    };
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) {
      return;
    }

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const endpoint = selectedText ? '/api/chat/query-with-selection' : '/api/chat/query';
      
      const payload = selectedText
        ? {
            query: input,
            selected_text: selectedText,
          }
        : {
            query: input,
            conversation_history: messages.map(msg => ({
              role: msg.type === 'user' ? 'user' : 'assistant',
              content: msg.content,
            })),
          };

      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        content: data.response,
        sources: data.retrieved_documents,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setSelectedText(''); // Clear selected text after sending
    } catch (error) {
      // Add error message
      const errorMessage = {
        id: messages.length + 2,
        type: 'error',
        content: `Error: ${error.message || 'Failed to get response from chatbot backend. Make sure the FastAPI server is running on ${apiUrl}.'}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: 'Hello! I\'m your Textbook Assistant. I can help you with questions about physical systems, robotics, computer vision, motion planning, and more. Ask me anything about the content!',
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className={styles.chatbotContainer}>
      <div className={styles.chatHeader}>
        <h3 className={styles.title}>🤖 AI Robotics Chatbot</h3>
        <div className={styles.headerButtons}>
          <button
            className={styles.settingsBtn}
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            ⚙️
          </button>
          <button
            className={styles.clearBtn}
            onClick={clearChat}
            title="Clear conversation"
          >
            🗑️
          </button>
        </div>
      </div>

      {showSettings && (
        <div className={styles.settingsPanel}>
          <label>
            API URL:
            <input
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8000"
            />
          </label>
          {selectedText && (
            <div className={styles.selectedTextInfo}>
              📌 Selected text detected:
              <div className={styles.selectedTextPreview}>
                {selectedText.substring(0, 100)}
                {selectedText.length > 100 ? '...' : ''}
              </div>
              <button onClick={() => setSelectedText('')}>Clear selection</button>
            </div>
          )}
        </div>
      )}

      <div className={styles.messagesContainer} ref={chatContainerRef}>
        {messages.map((message) => (
          <div key={message.id} className={`${styles.message} ${styles[message.type]}`}>
            <div className={styles.messageContent}>{message.content}</div>
            {message.sources && message.sources.length > 0 && (
              <div className={styles.sources}>
                <details>
                  <summary>📚 Sources ({message.sources.length})</summary>
                  {message.sources.map((source, idx) => (
                    <div key={idx} className={styles.source}>
                      <strong>{source.source}</strong>
                      <p>{source.text.substring(0, 150)}...</p>
                      <span className={styles.relevance}>Relevance: {(source.score * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </details>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className={styles.message} style={{ justifyContent: 'center' }}>
            <div className={styles.loadingSpinner}></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className={styles.inputForm} onSubmit={sendMessage}>
        {selectedText && (
          <div className={styles.selectedTextBanner}>
            📌 You have selected text. Your question will focus on: "{selectedText.substring(0, 50)}..."
          </div>
        )}
        <div className={styles.inputWrapper}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about the textbook... (or select text and ask about it)"
            disabled={loading}
            className={styles.input}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className={styles.sendBtn}
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  );
}

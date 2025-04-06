// Continued from the customer support React component in use_cases.md

function CustomerSupportChat() {
  // ... previous component code

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Customer Support</h2>
      </div>
      
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
            
            {/* Render KB articles if present */}
            {message.articles && (
              <div className="kb-articles">
                {message.articles.map((article, idx) => (
                  <div key={idx} className="kb-article">
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                    <p>{article.excerpt}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {isTyping && (
          <div className="message assistant typing">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          disabled={isTyping}
        />
        <button onClick={handleSend} disabled={isTyping}>
          Send
        </button>
      </div>
    </div>
  );
}

// Example CSS
const styles = `
.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  font-family: Arial, sans-serif;
}

.chat-header {
  padding: 10px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.message {
  max-width: 80%;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 8px;
  word-break: break-word;
}

.message.user {
  align-self: flex-end;
  background-color: #0084ff;
  color: white;
}

.message.assistant {
  align-self: flex-start;
  background-color: #f1f0f0;
  color: black;
}

.message.system {
  align-self: center;
  background-color: #fef9c3;
  color: #854d0e;
  font-size: 0.9em;
  width: 90%;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 5px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  display: inline-block;
  margin-right: 5px;
  animation: bounce 1.3s linear infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

.kb-articles {
  margin-top: 10px;
  padding: 5px;
  border-top: 1px solid #ddd;
}

.kb-article {
  padding: 8px;
  margin-bottom: 8px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 4px;
}

.kb-article a {
  color: #0066cc;
  text-decoration: none;
  font-weight: bold;
}

.kb-article p {
  margin: 5px 0 0 0;
  font-size: 0.9em;
  color: #555;
}

.chat-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ddd;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}

.chat-input button {
  margin-left: 10px;
  padding: 10px 15px;
  background-color: #0084ff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.chat-input button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
`;

// Usage
function App() {
  return (
    <div className="App">
      <h1>Customer Support Portal</h1>
      <CustomerSupportChat />
      <style>{styles}</style>
    </div>
  );
}

export default App;

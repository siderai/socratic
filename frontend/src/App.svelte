<script>
  import { onMount, onDestroy } from 'svelte';
  
  let username = '';
  let message = '';
  let messages = [];
  let ws;
  let connected = false;
  let usernameSubmitted = false;
  
  function handleUsernameSubmit() {
    if (username.trim()) {
      connectWebSocket();
      usernameSubmitted = true;
    }
  }
  
  function connectWebSocket() {
    ws = new WebSocket(`ws://localhost:8000/ws/${username}`);
    
    ws.onopen = () => {
      connected = true;
      console.log('Connected to WebSocket');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      messages = [...messages, data];
      // Auto-scroll to bottom
      setTimeout(() => {
        const chatContainer = document.querySelector('.chat-messages');
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      }, 50);
    };
    
    ws.onclose = () => {
      connected = false;
      console.log('Disconnected from WebSocket');
    };
  }
  
  function sendMessage() {
    if (message.trim() && connected) {
      ws.send(JSON.stringify({ message }));
      message = '';
    }
  }
  
  onDestroy(() => {
    if (ws) {
      ws.close();
    }
  });
</script>

<main>
  <div class="chat-container">
    <h1>Real-time Chat</h1>
    
    {#if !usernameSubmitted}
      <div class="username-form">
        <h2>Enter your username to join the chat</h2>
        <form on:submit|preventDefault={handleUsernameSubmit}>
          <input 
            type="text" 
            bind:value={username} 
            placeholder="Your username" 
            required
          />
          <button type="submit">Join Chat</button>
        </form>
      </div>
    {:else}
      <div class="chat-box">
        <div class="chat-messages">
          {#each messages as msg}
            <div class="message {msg.type === 'system' ? 'system-message' : (msg.username === username ? 'my-message' : 'other-message')}">
              {#if msg.type === 'system'}
                <span class="system-text">{msg.content}</span>
              {:else}
                <span class="username">{msg.username}:</span>
                <span class="content">{msg.content}</span>
              {/if}
            </div>
          {/each}
        </div>
        
        <form class="message-form" on:submit|preventDefault={sendMessage}>
          <input 
            type="text" 
            bind:value={message} 
            placeholder="Type your message..." 
            disabled={!connected}
          />
          <button type="submit" disabled={!connected}>Send</button>
        </form>
        
        <div class="status">
          {#if connected}
            <span class="connected">Connected as {username}</span>
          {:else}
            <span class="disconnected">Disconnected</span>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</main>

<style>
  main {
    font-family: Arial, sans-serif;
    max-width: 100%;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
  }
  
  .chat-container {
    width: 100%;
    max-width: 800px;
    margin: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  h1 {
    text-align: center;
    padding: 20px;
    background-color: #4CAF50;
    color: white;
    margin: 0;
  }
  
  h2 {
    margin-top: 0;
    color: #333;
  }
  
  .username-form {
    padding: 20px;
    text-align: center;
  }
  
  .username-form input {
    padding: 10px;
    width: 70%;
    margin-right: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
  }
  
  .username-form button {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
  }
  
  .chat-box {
    display: flex;
    flex-direction: column;
    height: 70vh;
  }
  
  .chat-messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
    background-color: #f9f9f9;
  }
  
  .message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 5px;
    max-width: 80%;
    word-wrap: break-word;
  }
  
  .system-message {
    width: 100%;
    max-width: 100%;
    text-align: center;
    padding: 5px;
    margin: 10px 0;
    color: #666;
    font-style: italic;
  }
  
  .my-message {
    background-color: #e3f2fd;
    margin-left: auto;
    border-bottom-right-radius: 0;
  }
  
  .other-message {
    background-color: #f1f1f1;
    margin-right: auto;
    border-bottom-left-radius: 0;
  }
  
  .username {
    font-weight: bold;
    margin-right: 5px;
  }
  
  .system-text {
    font-style: italic;
    color: #666;
  }
  
  .message-form {
    display: flex;
    padding: 10px;
    background-color: white;
    border-top: 1px solid #eee;
  }
  
  .message-form input {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
  }
  
  .message-form button {
    padding: 10px 20px;
    margin-left: 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
  }
  
  .message-form button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .status {
    padding: 10px;
    text-align: center;
    font-size: 14px;
    border-top: 1px solid #eee;
  }
  
  .connected {
    color: #4CAF50;
  }
  
  .disconnected {
    color: #f44336;
  }
</style>
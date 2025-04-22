class DwellaChat {
    constructor({
        connectAnnouncementId,
        masterId,
        clientId,
        token,
        messageContainer,
        messageInput,
        sendButton,
        imageInput
    }) {
        this.connectAnnouncementId = connectAnnouncementId;
        this.masterId = masterId;
        this.clientId = clientId;
        this.token = token;
        this.messageContainer = document.getElementById(messageContainer);
        this.messageInput = document.getElementById(messageInput);
        this.sendButton = document.getElementById(sendButton);
        this.imageInput = document.getElementById(imageInput);
        this.socket = null;
        this.messages = [];
        
        this.init();
    }
    
    init() {
        // Connect to WebSocket
        this.connectWebSocket();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load chat history
        this.loadChatHistory();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.connectAnnouncementId}/${this.masterId}/${this.clientId}/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connection established');
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleIncomingMessage(data);
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            // Try to reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    setupEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Send message on Enter key press
        this.messageInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                this.sendMessage();
            }
        });
        
        // Handle image upload
        if (this.imageInput) {
            this.imageInput.addEventListener('change', (event) => {
                const file = event.target.files[0];
                if (file) {
                    this.handleImageUpload(file);
                }
            });
        }
    }
    
    loadChatHistory() {
        // Make API request to get chat history
        fetch(`/api/chat/get_chat_history/?connect_announcement_id=${this.connectAnnouncementId}&master_id=${this.masterId}&client_id=${this.clientId}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            this.messages = data;
            this.renderMessages();
        })
        .catch(error => {
            console.error('Error loading chat history:', error);
        });
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        const data = {
            message: message
        };
        
        this.socket.send(JSON.stringify(data));
        this.messageInput.value = '';
    }
    
    handleImageUpload(file) {
        const reader = new FileReader();
        
        reader.onload = (event) => {
            const imageData = event.target.result;
            
            const data = {
                message: '',
                image: imageData
            };
            
            this.socket.send(JSON.stringify(data));
            this.imageInput.value = '';
        };
        
        reader.readAsDataURL(file);
    }
    
    handleIncomingMessage(data) {
        this.messages.push(data);
        this.renderMessages();
    }
    
    renderMessages() {
        this.messageContainer.innerHTML = '';
        
        this.messages.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            
            // Determine if this is a sent or received message
            const isCurrentUser = message.sender_id === this.userId;
            messageElement.classList.add(isCurrentUser ? 'sent' : 'received');
            
            // Create message content
            let messageContent = '';
            
            if (message.message) {
                messageContent += `<p>${message.message}</p>`;
            }
            
            if (message.image) {
                messageContent += `<img src="${message.image}" alt="Chat image" class="chat-image">`;
            }
            
            // Add timestamp
            const timestamp = new Date(message.timestamp).toLocaleTimeString();
            messageContent += `<span class="timestamp">${timestamp}</span>`;
            
            messageElement.innerHTML = messageContent;
            this.messageContainer.appendChild(messageElement);
        });
        
        // Scroll to bottom
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }
}

// Usage example:
/*
const chat = new DwellaChat({
    connectAnnouncementId: '123',
    masterId: '456',
    clientId: '789',
    token: 'your-jwt-token',
    messageContainer: 'message-container',
    messageInput: 'message-input',
    sendButton: 'send-button',
    imageInput: 'image-input'
});
*/ 
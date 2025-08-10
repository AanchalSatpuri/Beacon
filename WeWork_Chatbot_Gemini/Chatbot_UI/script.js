// Chat functionality
let chatMessages = [];
let isTyping = false;
let isChatOpen = false;

// Initialize chat
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Add event listeners
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    messageInput.addEventListener('input', function() {
        const hasText = this.value.trim().length > 0;
        sendBtn.style.opacity = hasText ? '1' : '0.6';
    });
    
    // Focus input on load
    messageInput.focus();
});

// Send message function
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (message === '' || isTyping) return;
    
    // Hide welcome section after first user message
    if (chatMessages.length <= 1) {
        hideWelcomeSection();
    }
    
    // Add user message
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Make actual API call and wait for real response
    handleBotResponse(message);
}

// Add message to chat
function addMessage(content, sender = 'bot') {
    const chatContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (sender === 'bot') {
        avatarDiv.innerHTML = '<span class="we-text">we</span>';
    } else {
        avatarDiv.innerHTML = '<span class="we-text">U</span>';
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (sender === 'bot') {
        // For bot messages, convert URLs to clickable links and preserve formatting
        contentDiv.innerHTML = convertUrlsToLinks(content);
    } else {
        // For user messages, keep as plain text
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Store message
    chatMessages.push({ content, sender, timestamp: new Date() });
}

// Show typing indicator
function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const chatContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <span class="we-text">we</span>
        </div>
        <div class="message-content typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isTyping = false;
}

// Handle bot response
async function handleBotResponse(userMessage) {
    try {
        // Try to get response from RAG API first
        const ragResponse = await sendToRAGAPI(userMessage);
        hideTypingIndicator(); // Hide typing indicator when response arrives
        
        if (ragResponse && ragResponse.success) {
            addMessage(ragResponse.response, 'bot');
        } else {
            // Fallback to local responses if RAG API fails
            const fallbackResponse = generateBotResponse(userMessage);
            addMessage(fallbackResponse, 'bot');
        }
    } catch (error) {
        console.error('Error getting RAG response:', error);
        hideTypingIndicator(); // Hide typing indicator on error too
        
        // Fallback to local responses
        const fallbackResponse = generateBotResponse(userMessage);
        addMessage(fallbackResponse, 'bot');
    }
}

// Generate bot response based on user input
function generateBotResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    // Simple keyword-based responses
    if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
        return "Hello! Welcome to WeWork India. How can I assist you today?";
    }
    
    if (message.includes('book') || message.includes('room') || message.includes('meeting')) {
        return "I can help you book a meeting room. Please provide your preferred date, time, and location. You can also use the WeWork app to make bookings directly.";
    }
    
    if (message.includes('wifi') || message.includes('internet') || message.includes('network')) {
        return "I understand you're having Wi-Fi issues. Please try reconnecting to the WeWork network. If the problem persists, I can connect you with our technical support team.";
    }
    
    if (message.includes('print') || message.includes('printer')) {
        return "For printing issues, please ensure you're connected to the WeWork network and have the printer drivers installed. I can help you troubleshoot or contact our IT support.";
    }
    
    if (message.includes('bill') || message.includes('payment') || message.includes('billing')) {
        return "I can help you with billing inquiries. Please provide your membership details, and I'll connect you with our billing support team or help resolve your payment questions.";
    }
    
    if (message.includes('keycard') || message.includes('access') || message.includes('entry')) {
        return "If you're having issues with your keycard or building access, I can help you troubleshoot or arrange for a replacement. Please provide your membership details.";
    }
    
    if (message.includes('clean') || message.includes('housekeeping')) {
        return "I can help you request cleaning services or report cleanliness issues. Please provide the specific location and details of what needs attention.";
    }
    
    if (message.includes('mail') || message.includes('package') || message.includes('post')) {
        return "For mail and package inquiries, I can help you track deliveries or set up mail handling services. Please provide tracking details or specify what assistance you need.";
    }
    
    if (message.includes('temperature') || message.includes('hot') || message.includes('cold') || message.includes('ac')) {
        return "I understand you're having temperature concerns. I can report this to our facilities team to adjust the climate control in your area. Please specify your location.";
    }
    
    if (message.includes('noise') || message.includes('loud') || message.includes('quiet')) {
        return "I can help address noise concerns in the workspace. Please provide details about the location and type of noise issue you're experiencing.";
    }
    
    if (message.includes('help') || message.includes('support')) {
        return "I'm here to help! I can assist with room bookings, technical issues, billing questions, access problems, and general WeWork services. What specifically do you need help with?";
    }
    
    // Default responses
    const defaultResponses = [
        "Thank you for reaching out. I'm here to help with any WeWork-related questions or issues. Could you please provide more details about what you need assistance with?",
        "I understand you need help. As your WeWork India Agent, I can assist with bookings, technical support, billing, and facility issues. How can I help you today?",
        "I'm here to assist you with any WeWork services. Please let me know what specific issue or question you have, and I'll do my best to help.",
        "Thanks for contacting WeWork support. I can help with a wide range of services including room bookings, technical issues, and general inquiries. What would you like assistance with?"
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}

// Toggle chatbot visibility
function toggleChatbot() {
    const chatContainer = document.getElementById('chatbotContainer');
    const chatButton = document.getElementById('chatButton');
    const chatButtonIcon = chatButton.querySelector('.chat-button-icon');
    const chatButtonClose = chatButton.querySelector('.chat-button-close');
    const welcomeSection = document.getElementById('welcomeSection');
    
    if (isChatOpen) {
        // Close chatbot
        chatContainer.style.display = 'none';
        chatButtonIcon.style.display = 'flex';
        chatButtonClose.style.display = 'none';
        isChatOpen = false;
    } else {
        // Open chatbot
        chatContainer.style.display = 'flex';
        chatButtonIcon.style.display = 'none';
        chatButtonClose.style.display = 'flex';
        isChatOpen = true;
        
        // Show welcome section only on first open or if no messages have been sent
        if (chatMessages.length <= 1) {
            welcomeSection.style.display = 'block';
        }
        
        // Focus input
        setTimeout(() => {
            const messageInput = document.getElementById('messageInput');
            messageInput.focus();
        }, 300);
    }
}

// Hide welcome section after first user message
function hideWelcomeSection() {
    const welcomeSection = document.getElementById('welcomeSection');
    welcomeSection.style.display = 'none';
}

// Refresh chat
function refreshChat() {
    const chatContainer = document.getElementById('chatMessages');
    const welcomeSection = document.getElementById('welcomeSection');
    
    chatContainer.innerHTML = `
        <div class="message bot-message">
            <div class="message-avatar">
                <span class="we-text">we</span>
            </div>
            <div class="message-content">
                Hello, how can I help you today?
            </div>
        </div>
    `;
    
    chatMessages = [{
        content: "Hello, how can I help you today?",
        sender: "bot",
        timestamp: new Date()
    }];
    
    // Show welcome section again
    welcomeSection.style.display = 'block';
    
    const messageInput = document.getElementById('messageInput');
    messageInput.value = '';
    messageInput.focus();
}

// RAG API Integration - Switch between Gemini (5000) and GPT-4o (5001)
async function sendToRAGAPI(message) {
    try {
        console.log('🚀 Sending to Gemini API:', message);
        
        // Gemini API on port 5000
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: message, // Changed from 'message' to 'query' to match API
                membership_type: 'All Access',
                context: {
                    source: 'chatbot_ui',
                    timestamp: new Date().toISOString()
                }
            })
        });
        
        console.log('📡 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ API Response:', data);
        return data;
    } catch (error) {
        console.error('❌ RAG API Error:', error);
        throw error;
    }
}

// Legacy API Integration (keeping for reference)
async function sendToAPI(message) {
    // This is the old category suggestion API
    try {
        const response = await fetch('YOUR_API_ENDPOINT', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': 'YOUR_API_KEY'
            },
            body: JSON.stringify({
                type: 'HELP_AND_SUPPORT',
                data: {
                    membership_type: 'All Access',
                    description: message,
                    options: []
                }
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { error: 'Unable to process request at the moment. Please try again.' };
    }
}

// Initialize chat messages
chatMessages = [{
    content: "Hello, how can I help you today?",
    sender: "bot",
    timestamp: new Date()
}];

// Convert URLs to clickable links
function convertUrlsToLinks(text) {
    // Escape HTML to prevent XSS attacks
    const escapeHtml = (unsafe) => {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    };
    
    // Escape the text first
    let escapedText = escapeHtml(text);
    
    // URL regex pattern that matches http/https URLs
    const urlRegex = /(https?:\/\/[^\s\)]+)/g;
    
    // Replace URLs with clickable links
    escapedText = escapedText.replace(urlRegex, (url) => {
        // Remove trailing punctuation if present
        const cleanUrl = url.replace(/[.,;:!?]+$/, '');
        const punctuation = url.substring(cleanUrl.length);
        
        return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" style="color: #3b82f6; text-decoration: underline;">${cleanUrl}</a>${punctuation}`;
    });
    
    // Convert line breaks to <br> tags
    escapedText = escapedText.replace(/\n/g, '<br>');
    
    return escapedText;
}

// Export functions for potential external use
window.chatbot = {
    sendMessage,
    addMessage,
    toggleChatbot,
    refreshChat,
    sendToRAGAPI,
    sendToAPI,
    convertUrlsToLinks
};

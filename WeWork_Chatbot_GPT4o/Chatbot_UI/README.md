# WeWork India Chatbot UI

A modern, responsive chatbot interface designed for WeWork India customer support.

## Features

- **Modern Design**: Clean, professional interface matching WeWork branding
- **Responsive Layout**: Works on desktop and mobile devices
- **Real-time Chat**: Smooth messaging experience with typing indicators
- **Smart Responses**: Context-aware bot responses for common queries
- **Easy Integration**: Ready for API integration with backend services

## Quick Start

### Option 1: Using Python Server (Recommended)
```bash
cd /Users/aanchal.satpuri/Desktop/projects/Beacon/Chatbot_UI
python3 server.py
```

### Option 2: Using Node.js (if you have it installed)
```bash
npx http-server . -p 8080 -o
```

### Option 3: Direct File Opening
Simply open `index.html` in your web browser.

## File Structure

```
Chatbot_UI/
├── index.html          # Main HTML structure
├── styles.css          # All styling and animations
├── script.js           # JavaScript functionality
├── server.py           # Simple Python server
└── README.md           # This file
```

## Supported Query Types

The chatbot currently handles these types of queries:

- **Room Bookings**: Meeting room reservations and availability
- **Technical Issues**: Wi-Fi, printing, and IT support
- **Billing**: Payment and billing inquiries
- **Access**: Keycard and building access issues
- **Facilities**: Cleaning, temperature, and maintenance
- **Mail Services**: Package and mail handling
- **General Support**: Any other WeWork-related questions

## Customization

### Branding
- Update logo and colors in `styles.css`
- Modify the WeWork branding elements as needed

### Responses
- Edit `generateBotResponse()` function in `script.js`
- Add new keyword patterns and responses

### API Integration
- Update the `sendToAPI()` function in `script.js`
- Connect to your backend chatbot service
- Add authentication headers as needed

## API Integration Example

To integrate with your WeWork support API:

```javascript
async function sendToAPI(message) {
    const response = await fetch('https://your-api-endpoint.com/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': 'your-api-key'
        },
        body: JSON.stringify({
            type: 'HELP_AND_SUPPORT',
            data: {
                membership_type: 'All Access',
                description: message,
                options: getRelevantOptions()
            }
        })
    });
    
    return await response.json();
}
```

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development

### Making Changes
1. Edit the HTML, CSS, or JavaScript files
2. Refresh your browser to see changes
3. No build process required!

### Adding New Features
- **New UI Components**: Add to `index.html` and style in `styles.css`
- **New Functionality**: Add JavaScript functions to `script.js`
- **New Responses**: Update the `generateBotResponse()` function

## Production Deployment

For production use:

1. **Optimize Assets**: Minify CSS and JavaScript
2. **Add Analytics**: Integrate with Google Analytics or similar
3. **Error Handling**: Add proper error handling and logging
4. **Security**: Implement proper API security
5. **Performance**: Add caching and optimization

## License

This project is part of the WeWork India support system.

## Support

For technical support or questions about this chatbot UI, please contact the development team.

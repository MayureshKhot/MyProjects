# LinkedIn Content Generator AI

An AI-powered tool that generates LinkedIn-style content and related images using Groq API and Tavily API.

## Features

- Generate LinkedIn-style text content
- Generate related AI images
- Optional web search integration for additional context
- Modern, responsive UI
- Download generated images
- Copy text to clipboard
- Error handling and user feedback

## Prerequisites

- Python 3.8+
- Node.js 14+
- Groq API key (required)
- Tavily API key (optional)

## Local Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key  # Optional
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the frontend directory:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter your prompt in the text field
3. Toggle web search if you want additional context
4. Click "Generate Content"
5. View the generated text and image
6. Use the copy button to copy the text to clipboard
7. Download the image if desired

## Troubleshooting

### Backend Issues

1. **API Key Errors**
   - Ensure your `.env` file is properly configured
   - Check if the API keys are valid and have sufficient credits
   - Verify the environment variables are loaded correctly

2. **Server Not Starting**
   - Check if port 8000 is available
   - Ensure all dependencies are installed correctly
   - Check the virtual environment is activated

3. **API Rate Limits**
   - Monitor your API usage
   - Implement rate limiting if needed

### Frontend Issues

1. **Connection Errors**
   - Verify the backend server is running
   - Check if the `REACT_APP_API_URL` is correct
   - Ensure CORS is properly configured

2. **Build Errors**
   - Clear the `node_modules` folder and reinstall dependencies
   - Check for version conflicts in `package.json`

## Deployment

### Backend Deployment (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY` (optional)

### Frontend Deployment (Vercel)

1. Create a new project on Vercel
2. Connect your GitHub repository
3. Set the environment variable:
   - `REACT_APP_API_URL`: Your backend URL (e.g., `https://your-app.onrender.com`)
4. Deploy

## Development Guidelines

### Code Structure
- Backend: FastAPI with modular services
- Frontend: React with Material-UI components
- Clear separation of concerns between frontend and backend

### Error Handling
- Backend: Proper HTTP status codes and error messages
- Frontend: User-friendly error displays and loading states

### API Integration
- Groq API for text generation
- Placeholder for image generation (to be replaced with actual service)
- Tavily API for web search (optional)

## Future Enhancements

- User authentication
- Subscription model
- Content history
- Custom templates
- Advanced image generation options
- Analytics dashboard
- Rate limiting
- Caching layer
- Content moderation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 
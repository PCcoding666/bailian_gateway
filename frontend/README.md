# Frontend for Alibaba Cloud Bailian Integration Platform

This directory contains the frontend implementation for the Alibaba Cloud Bailian Integration Platform.

## Project Structure

- `src/` - Source code
  - `components/` - Reusable UI components
  - `pages/` - Page components
  - `services/` - API service integrations
  - `utils/` - Utility functions
  - `assets/` - Static assets (images, styles, etc.)
- `public/` - Public assets

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. The application will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Development

This project uses React with Vite for fast development and Hot Module Replacement (HMR).

### Project Setup

- React 18+ with hooks
- React Router for navigation
- CSS modules for styling
- Axios for HTTP requests

### Environment Variables

Create a `.env` file in the root of the frontend directory:

```bash
VITE_API_URL=http://localhost:8000
```

### Routing

The application uses React Router with the following routes:

- `/` - Main chat interface (requires authentication)
- `/login` - Login page
- `/register` - Registration page
- `/conversations/:id` - Conversation detail page
- `/history` - API call history page
- `/settings` - User settings page

## Testing

```bash
npm test
```

## Deployment

For production deployment, build the application and serve the `dist` directory:

```bash
npm run build
# Serve the dist directory with your preferred web server
```
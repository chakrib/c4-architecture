# Quick Start Guide

Get up and running with the C4 Diagram Generator in 5 minutes!

## Step 1: Install Dependencies

```bash
npm install
```

## Step 2: Configure API Key

Choose one of the following options:

### Option A: Using OpenAI

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Open `.env` file
3. Add your key:
   ```
   VITE_OPENAI_API_KEY=sk-proj-your-key-here
   ```

### Option B: Using Anthropic Claude

1. Get an API key from [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Open `.env` file
3. Add your key:
   ```
   VITE_ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

## Step 3: Start the Application

```bash
npm run dev
```

Open your browser to `http://localhost:5173`

## Step 4: Generate Your First Diagram

1. Select your AI provider (OpenAI or Anthropic) from the dropdown
2. Enter a solution context, for example:

   ```
   We're building a ride-sharing app called QuickRide. Riders use mobile apps
   to request rides, drivers accept requests through their driver app. The system
   integrates with Google Maps for navigation, Stripe for payments, and Twilio
   for SMS notifications.
   ```

3. Click "Generate Diagram"
4. View your C4 diagram!

## Tips

- Be descriptive: Include users, external systems, and integrations
- Specify technologies: Mention APIs, services, and platforms
- Use natural language: No need for technical jargon or special formatting

## Need Help?

Check the full [README.md](./README.md) for detailed documentation, troubleshooting, and advanced features.

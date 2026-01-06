# C4 Diagram Generator

A React-based web application that uses AI to generate C4 Level 1 (System Context) diagrams from natural language descriptions. Powered by OpenAI or Anthropic Claude API and rendered using Mermaid.js.

## Features

- **AI-Powered Parsing**: Uses OpenAI GPT or Anthropic Claude to intelligently parse free-form solution context descriptions
- **C4 Standard Diagrams**: Generates C4 Level 1 (System Context) diagrams following industry standards
- **Mermaid.js Rendering**: Beautiful, interactive diagrams rendered directly in the browser
- **Multiple AI Providers**: Support for both OpenAI and Anthropic Claude APIs
- **Export Functionality**: Download generated Mermaid diagram code for use in documentation
- **Modern UI**: Clean, responsive interface built with React

## Architecture

```
┌─────────────────────────────────────────┐
│           React Frontend                │
│  ┌───────────────────────────────────┐  │
│  │   DiagramGenerator Component      │  │
│  │  - Input form for context         │  │
│  │  - AI provider selection          │  │
│  │  - Generate/Clear controls        │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│  ┌──────────────▼────────────────────┐  │
│  │      AIService (Service Layer)    │  │
│  │  - OpenAI API integration         │  │
│  │  - Anthropic API integration      │  │
│  │  - Prompt engineering             │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│                 │ (Mermaid Code)         │
│  ┌──────────────▼────────────────────┐  │
│  │   MermaidDiagram Component        │  │
│  │  - Mermaid.js initialization      │  │
│  │  - Diagram rendering              │  │
│  │  - Error handling                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Prerequisites

- Node.js (v18.17.0 or higher recommended)
- npm or yarn
- An API key from either:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Anthropic](https://console.anthropic.com/settings/keys)

## Installation

1. **Clone or navigate to the repository**:
   ```bash
   cd c4-diagram-generator
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure API Keys**:

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key(s):
   ```env
   # For OpenAI
   VITE_OPENAI_API_KEY=sk-your-openai-api-key-here

   # For Anthropic (Claude)
   VITE_ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
   ```

   **Note**: You only need to configure one API key depending on which provider you want to use.

## Running the Application

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or another port if 5173 is in use).

## Usage

1. **Select AI Provider**: Choose between OpenAI or Anthropic Claude from the dropdown
2. **Enter Solution Context**: Describe your system in natural language. Example:

   ```
   We are building an e-commerce platform called ShopEasy. The system will be
   used by customers to browse and purchase products. It needs to integrate with
   a payment gateway (Stripe) for processing payments, a shipping provider
   (FedEx API) for tracking deliveries, and an email service (SendGrid) for
   sending order confirmations. Internal administrators will manage the product
   catalog and view orders through an admin dashboard.
   ```

3. **Generate Diagram**: Click "Generate Diagram" button
4. **View & Export**: The C4 diagram will be rendered. You can:
   - View the visual diagram
   - Expand "View Mermaid Code" to see the generated code
   - Click "Export Mermaid Code" to download the diagram code

## Example Input & Output

### Input
```
A healthcare appointment system where patients can book appointments with doctors.
The system integrates with an SMS gateway for sending reminders, a payment
processor for handling co-pays, and an electronic health records system for
accessing patient history.
```

### Generated Output
The AI will generate Mermaid C4 diagram code similar to:

```mermaid
C4Context
  title System Context diagram for Healthcare Appointment System

  Person(patient, "Patient", "Books and manages appointments")
  Person(doctor, "Doctor", "Views and manages their schedule")
  System(appointmentSystem, "Healthcare Appointment System", "Manages appointments and patient bookings")

  System_Ext(smsGateway, "SMS Gateway", "Sends appointment reminders")
  System_Ext(paymentProcessor, "Payment Processor", "Handles co-payment processing")
  System_Ext(ehrSystem, "EHR System", "Electronic Health Records")

  Rel(patient, appointmentSystem, "Books appointments", "HTTPS")
  Rel(doctor, appointmentSystem, "Manages schedule", "HTTPS")
  Rel(appointmentSystem, smsGateway, "Sends reminders", "API")
  Rel(appointmentSystem, paymentProcessor, "Processes payments", "API")
  Rel(appointmentSystem, ehrSystem, "Retrieves patient data", "API")
```

## Project Structure

```
c4-diagram-generator/
├── src/
│   ├── components/
│   │   ├── DiagramGenerator.jsx    # Main component with input form
│   │   ├── DiagramGenerator.css    # Styles for generator
│   │   └── MermaidDiagram.jsx      # Mermaid rendering component
│   ├── services/
│   │   └── AIService.js            # AI API integration service
│   ├── App.jsx                     # Root component
│   ├── App.css                     # App-level styles
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── package.json                    # Dependencies and scripts
├── vite.config.js                  # Vite configuration
└── README.md                       # This file
```

## Technologies Used

- **React** - UI framework
- **Vite** - Build tool and dev server
- **Mermaid.js** - Diagram rendering library
- **OpenAI SDK** - OpenAI API integration
- **Anthropic SDK** - Claude API integration

## C4 Diagram Overview

C4 diagrams are a set of hierarchical abstractions for describing software architecture:

- **Level 1 - System Context**: Shows the system in context with users and external systems (this tool generates these)
- **Level 2 - Container**: Shows high-level technology choices
- **Level 3 - Component**: Shows components within a container
- **Level 4 - Code**: Shows implementation details

This tool focuses on Level 1 (System Context) diagrams, which are ideal for:
- Presenting system overview to stakeholders
- Documentation and architectural decision records
- Understanding system boundaries and integrations

## Security Notes

**Important**: This application uses `dangerouslyAllowBrowser: true` in the API clients for demonstration purposes. In a production environment, you should:

1. **Never expose API keys in the browser**
2. **Create a backend proxy server** to handle AI API calls
3. **Implement proper authentication and rate limiting**

Example production architecture:
```
Browser → Your Backend API → AI Provider API
         (with API key)
```

## Troubleshooting

### API Key Errors
- Ensure your `.env` file is in the root directory
- Verify the API key format is correct
- Check that you have credits/quota available in your AI provider account

### Diagram Not Rendering
- Check the browser console for errors
- Verify the generated Mermaid code syntax in the "View Mermaid Code" section
- Try refreshing the page

### Node Version Issues
If you see EBADENGINE warnings, upgrade to Node.js v20 or later:
```bash
nvm install 20
nvm use 20
```

## Building for Production

To create a production build:

```bash
npm run build
```

The optimized files will be in the `dist/` directory. You can preview the production build with:

```bash
npm run preview
```

## Contributing

Feel free to submit issues or pull requests for improvements!

## License

MIT License - feel free to use this project for your own purposes.

## Acknowledgments

- [C4 Model](https://c4model.com/) by Simon Brown
- [Mermaid.js](https://mermaid.js.org/) for diagram rendering
- [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/) for AI capabilities

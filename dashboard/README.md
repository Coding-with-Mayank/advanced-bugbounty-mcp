# Bug Bounty Dashboard

Web dashboard for the Advanced Bug Bounty MCP Server.

## Features

- Real-time statistics display
- Scan history tracking
- Vulnerability monitoring
- System status overview
- Beautiful, responsive UI

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run in production mode
npm start
```

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `API_URL` - MCP Server API URL
- `PORT` - Dashboard port (default: 3000)

## Accessing the Dashboard

Once the Docker containers are running:

- Dashboard: http://localhost:3000
- API: http://localhost:3000/api
- Health Check: http://localhost:3000/api/health

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Get statistics
- `GET /api/scans` - Get recent scans
- `GET /api/vulnerabilities` - Get vulnerabilities
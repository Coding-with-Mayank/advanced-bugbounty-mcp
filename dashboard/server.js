const express = require('express');
const cors = require('cors');
const path = require('path');
const { MongoClient } = require('mongodb');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://admin:bugbounty_secure_pass@mongodb:27017/bugbounty?authSource=admin';
let db;

MongoClient.connect(MONGODB_URI)
  .then(client => {
    console.log('✓ Connected to MongoDB');
    db = client.db('bugbounty');
  })
  .catch(err => {
    console.error('MongoDB connection error:', err);
  });

// API Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get recent scans
app.get('/api/scans', async (req, res) => {
  try {
    if (!db) {
      return res.status(503).json({ error: 'Database not connected' });
    }
    const scans = await db.collection('scans')
      .find({})
      .sort({ created_at: -1 })
      .limit(50)
      .toArray();
    res.json(scans);
  } catch (error) {
    console.error('Error fetching scans:', error);
    res.status(500).json({ error: 'Failed to fetch scans' });
  }
});

// Get vulnerabilities
app.get('/api/vulnerabilities', async (req, res) => {
  try {
    if (!db) {
      return res.status(503).json({ error: 'Database not connected' });
    }
    const vulnerabilities = await db.collection('vulnerabilities')
      .find({})
      .sort({ severity: -1, created_at: -1 })
      .limit(100)
      .toArray();
    res.json(vulnerabilities);
  } catch (error) {
    console.error('Error fetching vulnerabilities:', error);
    res.status(500).json({ error: 'Failed to fetch vulnerabilities' });
  }
});

// Get statistics
app.get('/api/stats', async (req, res) => {
  try {
    if (!db) {
      return res.status(503).json({ error: 'Database not connected' });
    }
    
    const totalScans = await db.collection('scans').countDocuments();
    const totalVulnerabilities = await db.collection('vulnerabilities').countDocuments();
    const criticalVulns = await db.collection('vulnerabilities').countDocuments({ severity: 'critical' });
    const highVulns = await db.collection('vulnerabilities').countDocuments({ severity: 'high' });
    
    res.json({
      totalScans,
      totalVulnerabilities,
      criticalVulns,
      highVulns,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Failed to fetch statistics' });
  }
});

// Serve index.html for all other routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Bug Bounty Dashboard running on http://0.0.0.0:${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}`);
  console.log(`🔌 API: http://localhost:${PORT}/api`);
});
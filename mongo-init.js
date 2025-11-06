// MongoDB initialization script
// Creates database and collections for bug bounty data

db = db.getSiblingDB('bugbounty');

// Create collections
db.createCollection('scans');
db.createCollection('vulnerabilities');
db.createCollection('assets');
db.createCollection('reports');
db.createCollection('monitoring');

// Create indexes
db.scans.createIndex({ domain: 1, timestamp: -1 });
db.vulnerabilities.createIndex({ target: 1, severity: 1 });
db.assets.createIndex({ domain: 1, type: 1 });
db.reports.createIndex({ created_at: -1 });
db.monitoring.createIndex({ target: 1, last_checked: -1 });

// Create initial admin user (optional)
// db.createUser({
//   user: 'bugbounty_admin',
//   pwd: 'secure_password',
//   roles: [{ role: 'readWrite', db: 'bugbounty' }]
// });

print('Database initialized successfully');
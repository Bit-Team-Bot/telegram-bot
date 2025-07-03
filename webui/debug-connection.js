/**
 * Debug-Skript für Netzwerkverbindungen
 * 
 * Dieses Skript testet die Verbindungen zu Backend und Userbot-Service
 * und hilft bei der Diagnose von Network Error Problemen.
 */

const axios = require('axios');

// Konfiguration
const BACKEND_URL = 'http://localhost:8000';
const USERBOT_URL = 'http://localhost:8001';
const FRONTEND_URL = 'http://localhost:8080';

// Farben für bessere Lesbarkeit
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

const log = (message, color = 'reset') => {
  console.log(`${colors[color]}${message}${colors.reset}`);
};

const logSuccess = (message) => {
  log(`✅ ${message}`, 'green');
};

const logError = (message) => {
  log(`❌ ${message}`, 'red');
};

const logWarning = (message) => {
  log(`⚠️ ${message}`, 'yellow');
};

const logInfo = (message) => {
  log(`ℹ️ ${message}`, 'blue');
};

const logStep = (step, message) => {
  log(`\n${step}. ${message}`, 'cyan');
};

/**
 * Test 1: Backend-Verbindung
 */
async function testBackendConnection() {
  logStep('1', 'Teste Backend-Verbindung...');
  
  try {
    // Test 1.1: Root-Endpoint
    logInfo('Teste Root-Endpoint...');
    const rootResponse = await axios.get(`${BACKEND_URL}/`, { timeout: 5000 });
    logSuccess(`Backend Root: ${rootResponse.status} - ${JSON.stringify(rootResponse.data)}`);
    
    // Test 1.2: Health-Check
    logInfo('Teste Health-Check...');
    const healthResponse = await axios.get(`${BACKEND_URL}/health`, { timeout: 5000 });
    logSuccess(`Backend Health: ${healthResponse.status} - ${JSON.stringify(healthResponse.data)}`);
    
    // Test 1.3: Status
    logInfo('Teste Status...');
    const statusResponse = await axios.get(`${BACKEND_URL}/status`, { timeout: 5000 });
    logSuccess(`Backend Status: ${statusResponse.status} - ${JSON.stringify(statusResponse.data)}`);
    
    return true;
  } catch (error) {
    logError(`Backend-Verbindung fehlgeschlagen: ${error.message}`);
    if (error.code === 'ECONNREFUSED') {
      logWarning('Backend läuft nicht auf Port 8000. Starte es mit:');
      log('cd backend && source ../venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload', 'yellow');
    }
    return false;
  }
}

/**
 * Test 2: Userbot-Service-Verbindung
 */
async function testUserbotConnection() {
  logStep('2', 'Teste Userbot-Service-Verbindung...');
  
  try {
    // Test 2.1: Root-Endpoint
    logInfo('Teste Userbot Root-Endpoint...');
    const rootResponse = await axios.get(`${USERBOT_URL}/`, { timeout: 5000 });
    logSuccess(`Userbot Root: ${rootResponse.status} - ${JSON.stringify(rootResponse.data)}`);
    
    // Test 2.2: Status
    logInfo('Teste Userbot Status...');
    const statusResponse = await axios.get(`${USERBOT_URL}/status`, { timeout: 5000 });
    logSuccess(`Userbot Status: ${statusResponse.status} - ${JSON.stringify(statusResponse.data)}`);
    
    return true;
  } catch (error) {
    logError(`Userbot-Verbindung fehlgeschlagen: ${error.message}`);
    if (error.code === 'ECONNREFUSED') {
      logWarning('Userbot-Service läuft nicht auf Port 8001. Starte es mit:');
      log('cd userbot_service && source ../venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload', 'yellow');
    }
    return false;
  }
}

/**
 * Test 3: Frontend-Verbindung
 */
async function testFrontendConnection() {
  logStep('3', 'Teste Frontend-Verbindung...');
  
  try {
    const response = await axios.get(`${FRONTEND_URL}/`, { timeout: 5000 });
    logSuccess(`Frontend: ${response.status} - Erreichbar`);
    return true;
  } catch (error) {
    logError(`Frontend-Verbindung fehlgeschlagen: ${error.message}`);
    if (error.code === 'ECONNREFUSED') {
      logWarning('Frontend läuft nicht auf Port 8080. Starte es mit:');
      log('cd webui && npm run dev', 'yellow');
    }
    return false;
  }
}

/**
 * Test 4: CORS-Probleme
 */
async function testCORS() {
  logStep('4', 'Teste CORS-Konfiguration...');
  
  try {
    // Test mit OPTIONS-Request (CORS Preflight)
    const response = await axios.options(`${BACKEND_URL}/auth/request-code`, {
      timeout: 5000,
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
      }
    });
    logSuccess(`CORS Backend: ${response.status} - OK`);
    
    const userbotResponse = await axios.options(`${USERBOT_URL}/start`, {
      timeout: 5000,
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
      }
    });
    logSuccess(`CORS Userbot: ${userbotResponse.status} - OK`);
    
    return true;
  } catch (error) {
    logError(`CORS-Test fehlgeschlagen: ${error.message}`);
    logWarning('Möglicherweise CORS-Probleme. Prüfe die Backend-Konfiguration.');
    return false;
  }
}

/**
 * Test 5: API-Endpunkte
 */
async function testAPIEndpoints() {
  logStep('5', 'Teste API-Endpunkte...');
  
  const endpoints = [
    { name: 'Backend Auth Request Code', url: `${BACKEND_URL}/auth/request-code`, method: 'POST' },
    { name: 'Userbot Start', url: `${USERBOT_URL}/start`, method: 'POST' },
    { name: 'Userbot Status', url: `${USERBOT_URL}/status`, method: 'GET' }
  ];
  
  for (const endpoint of endpoints) {
    try {
      const config = {
        method: endpoint.method,
        url: endpoint.url,
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' }
      };
      
      if (endpoint.method === 'POST') {
        config.data = { phone: '+49123456789' };
      }
      
      const response = await axios(config);
      logSuccess(`${endpoint.name}: ${response.status} - OK`);
    } catch (error) {
      if (error.response) {
        // Endpoint existiert, aber gibt Fehler zurück (normal bei Test-Daten)
        logInfo(`${endpoint.name}: ${error.response.status} - Endpoint erreichbar`);
      } else {
        logError(`${endpoint.name}: ${error.message}`);
      }
    }
  }
}

/**
 * Test 6: Port-Verfügbarkeit
 */
async function testPorts() {
  logStep('6', 'Teste Port-Verfügbarkeit...');
  
  const net = require('net');
  
  const ports = [
    { port: 8000, service: 'Backend' },
    { port: 8001, service: 'Userbot' },
    { port: 8080, service: 'Frontend' }
  ];
  
  for (const { port, service } of ports) {
    const client = new net.Socket();
    
    const isOpen = await new Promise((resolve) => {
      client.setTimeout(3000);
      
      client.on('connect', () => {
        logSuccess(`Port ${port} (${service}): Offen`);
        client.destroy();
        resolve(true);
      });
      
      client.on('timeout', () => {
        logError(`Port ${port} (${service}): Timeout`);
        client.destroy();
        resolve(false);
      });
      
      client.on('error', () => {
        logError(`Port ${port} (${service}): Geschlossen`);
        client.destroy();
        resolve(false);
      });
      
      client.connect(port, 'localhost');
    });
  }
}

/**
 * Hauptfunktion
 */
async function main() {
  log('🔍 Netzwerk-Diagnose für Telegram Bot Management System', 'bright');
  log('=' .repeat(60), 'bright');
  
  const results = {
    backend: false,
    userbot: false,
    frontend: false,
    cors: false
  };
  
  try {
    // Führe alle Tests aus
    results.backend = await testBackendConnection();
    results.userbot = await testUserbotConnection();
    results.frontend = await testFrontendConnection();
    results.cors = await testCORS();
    
    await testAPIEndpoints();
    await testPorts();
    
    // Zusammenfassung
    log('\n📊 Test-Zusammenfassung:', 'magenta');
    log('=' .repeat(30), 'magenta');
    
    log(`Backend (Port 8000): ${results.backend ? '✅ OK' : '❌ Fehler'}`, results.backend ? 'green' : 'red');
    log(`Userbot (Port 8001): ${results.userbot ? '✅ OK' : '❌ Fehler'}`, results.userbot ? 'green' : 'red');
    log(`Frontend (Port 8080): ${results.frontend ? '✅ OK' : '❌ Fehler'}`, results.frontend ? 'green' : 'red');
    log(`CORS: ${results.cors ? '✅ OK' : '❌ Fehler'}`, results.cors ? 'green' : 'red');
    
    // Empfehlungen
    log('\n💡 Empfehlungen:', 'yellow');
    log('=' .repeat(20), 'yellow');
    
    if (!results.backend) {
      log('1. Starte das Backend: cd backend && source ../venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload', 'yellow');
    }
    
    if (!results.userbot) {
      log('2. Userbot ist optional - Login funktioniert auch ohne', 'blue');
    }
    
    if (!results.frontend) {
      log('3. Starte das Frontend: cd webui && npm run dev', 'yellow');
    }
    
    if (!results.cors) {
      log('4. CORS-Probleme - prüfe Backend-Konfiguration', 'yellow');
    }
    
    if (results.backend && results.frontend) {
      logSuccess('🎉 Grundlegende Verbindungen funktionieren!');
      log('Öffne http://localhost:8080/login im Browser', 'green');
    }
    
  } catch (error) {
    logError(`Diagnose fehlgeschlagen: ${error.message}`);
  }
}

// Skript ausführen
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  testBackendConnection,
  testUserbotConnection,
  testFrontendConnection,
  testCORS,
  testAPIEndpoints,
  testPorts
}; 
/**
 * Debug-Skript für öffentliche Produktions-URLs
 * 
 * Dieses Skript testet die Verbindungen zu den öffentlichen APIs
 * und hilft bei der Diagnose von Network Error Problemen im Internet.
 */

const axios = require('axios');

// Öffentliche Produktions-URLs
const BACKEND_URL = 'https://api.bit-team-bot.online';
const USERBOT_URL = 'https://userbot.bit-team-bot.online';
const FRONTEND_URL = 'https://webui.bit-team-bot.online';

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
 * Test 1: Backend-Verbindung (öffentlich)
 */
async function testBackendConnection() {
  logStep('1', 'Teste öffentliche Backend-Verbindung...');
  
  try {
    // Test 1.1: Root-Endpoint
    logInfo('Teste Root-Endpoint...');
    const rootResponse = await axios.get(`${BACKEND_URL}/`, { 
      timeout: 10000,
      headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
    });
    logSuccess(`Backend Root: ${rootResponse.status} - ${JSON.stringify(rootResponse.data)}`);
    
    // Test 1.2: Health-Check
    logInfo('Teste Health-Check...');
    const healthResponse = await axios.get(`${BACKEND_URL}/health`, { 
      timeout: 10000,
      headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
    });
    logSuccess(`Backend Health: ${healthResponse.status} - ${JSON.stringify(healthResponse.data)}`);
    
    // Test 1.3: Status
    logInfo('Teste Status...');
    const statusResponse = await axios.get(`${BACKEND_URL}/status`, { 
      timeout: 10000,
      headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
    });
    logSuccess(`Backend Status: ${statusResponse.status} - ${JSON.stringify(statusResponse.data)}`);
    
    return true;
  } catch (error) {
    logError(`Backend-Verbindung fehlgeschlagen: ${error.message}`);
    if (error.code === 'ENOTFOUND') {
      logWarning('DNS-Auflösung fehlgeschlagen. Prüfe die Domain api.bit-team-bot.online');
    } else if (error.code === 'ECONNREFUSED') {
      logWarning('Verbindung verweigert. Server läuft möglicherweise nicht.');
    } else if (error.response) {
      logWarning(`HTTP ${error.response.status}: ${error.response.statusText}`);
    }
    return false;
  }
}

/**
 * Test 2: Userbot-Service-Verbindung (öffentlich)
 */
async function testUserbotConnection() {
  logStep('2', 'Teste öffentliche Userbot-Service-Verbindung...');
  
  try {
    // Test 2.1: Root-Endpoint
    logInfo('Teste Userbot Root-Endpoint...');
    const rootResponse = await axios.get(`${USERBOT_URL}/`, { 
      timeout: 10000,
      headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
    });
    logSuccess(`Userbot Root: ${rootResponse.status} - ${JSON.stringify(rootResponse.data)}`);
    
    // Test 2.2: Status
    logInfo('Teste Userbot Status...');
    const statusResponse = await axios.get(`${USERBOT_URL}/status`, { 
      timeout: 10000,
      headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
    });
    logSuccess(`Userbot Status: ${statusResponse.status} - ${JSON.stringify(statusResponse.data)}`);
    
    return true;
  } catch (error) {
    logError(`Userbot-Verbindung fehlgeschlagen: ${error.message}`);
    if (error.code === 'ENOTFOUND') {
      logWarning('DNS-Auflösung fehlgeschlagen. Prüfe die Domain userbot.bit-team-bot.online');
    } else if (error.code === 'ECONNREFUSED') {
      logWarning('Verbindung verweigert. Userbot-Service läuft möglicherweise nicht.');
    } else if (error.response) {
      logWarning(`HTTP ${error.response.status}: ${error.response.statusText}`);
    }
    return false;
  }
}

/**
 * Test 3: Frontend-Verbindung (öffentlich)
 */
async function testFrontendConnection() {
  logStep('3', 'Teste öffentliche Frontend-Verbindung...');
  
  try {
    const response = await axios.get(`${FRONTEND_URL}/`, { 
      timeout: 10000,
      headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
    });
    logSuccess(`Frontend: ${response.status} - Erreichbar`);
    return true;
  } catch (error) {
    logError(`Frontend-Verbindung fehlgeschlagen: ${error.message}`);
    if (error.code === 'ENOTFOUND') {
      logWarning('DNS-Auflösung fehlgeschlagen. Prüfe die Domain webui.bit-team-bot.online');
    }
    return false;
  }
}

/**
 * Test 4: CORS-Probleme (öffentlich)
 */
async function testCORS() {
  logStep('4', 'Teste CORS-Konfiguration (öffentlich)...');
  
  try {
    // Test mit OPTIONS-Request (CORS Preflight)
    const response = await axios.options(`${BACKEND_URL}/auth/request-code`, {
      timeout: 10000,
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type',
        'User-Agent': 'TelegramBotDebug/1.0'
      }
    });
    logSuccess(`CORS Backend: ${response.status} - OK`);
    
    const userbotResponse = await axios.options(`${USERBOT_URL}/start`, {
      timeout: 10000,
      headers: {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type',
        'User-Agent': 'TelegramBotDebug/1.0'
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
 * Test 5: API-Endpunkte (öffentlich)
 */
async function testAPIEndpoints() {
  logStep('5', 'Teste API-Endpunkte (öffentlich)...');
  
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
        timeout: 10000,
        headers: { 
          'Content-Type': 'application/json',
          'User-Agent': 'TelegramBotDebug/1.0'
        }
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
 * Test 6: SSL/TLS-Verbindungen
 */
async function testSSL() {
  logStep('6', 'Teste SSL/TLS-Verbindungen...');
  
  const https = require('https');
  const url = require('url');
  
  const urls = [
    { name: 'Backend SSL', url: BACKEND_URL },
    { name: 'Userbot SSL', url: USERBOT_URL },
    { name: 'Frontend SSL', url: FRONTEND_URL }
  ];
  
  for (const { name, url: testUrl } of urls) {
    try {
      const parsedUrl = url.parse(testUrl);
      
      const response = await new Promise((resolve, reject) => {
        const req = https.request({
          hostname: parsedUrl.hostname,
          port: parsedUrl.port || 443,
          path: parsedUrl.path,
          method: 'GET',
          timeout: 10000,
          headers: { 'User-Agent': 'TelegramBotDebug/1.0' }
        }, (res) => {
          resolve(res);
        });
        
        req.on('error', reject);
        req.on('timeout', () => reject(new Error('Timeout')));
        req.end();
      });
      
      logSuccess(`${name}: ${response.statusCode} - SSL OK`);
    } catch (error) {
      logError(`${name}: ${error.message}`);
    }
  }
}

/**
 * Test 7: DNS-Auflösung
 */
async function testDNS() {
  logStep('7', 'Teste DNS-Auflösung...');
  
  const dns = require('dns').promises;
  
  const domains = [
    { name: 'Backend Domain', domain: 'api.bit-team-bot.online' },
    { name: 'Userbot Domain', domain: 'userbot.bit-team-bot.online' },
    { name: 'Frontend Domain', domain: 'webui.bit-team-bot.online' }
  ];
  
  for (const { name, domain } of domains) {
    try {
      const addresses = await dns.resolve4(domain);
      logSuccess(`${name}: ${addresses.join(', ')}`);
    } catch (error) {
      logError(`${name}: ${error.message}`);
    }
  }
}

/**
 * Hauptfunktion
 */
async function main() {
  log('🌐 Öffentliche Netzwerk-Diagnose für Telegram Bot Management System', 'bright');
  log('=' .repeat(70), 'bright');
  
  const results = {
    backend: false,
    userbot: false,
    frontend: false,
    cors: false,
    ssl: false,
    dns: false
  };
  
  try {
    // Führe alle Tests aus
    await testDNS();
    await testSSL();
    results.backend = await testBackendConnection();
    results.userbot = await testUserbotConnection();
    results.frontend = await testFrontendConnection();
    results.cors = await testCORS();
    
    await testAPIEndpoints();
    
    // Zusammenfassung
    log('\n📊 Test-Zusammenfassung (Öffentlich):', 'magenta');
    log('=' .repeat(40), 'magenta');
    
    log(`Backend (${BACKEND_URL}): ${results.backend ? '✅ OK' : '❌ Fehler'}`, results.backend ? 'green' : 'red');
    log(`Userbot (${USERBOT_URL}): ${results.userbot ? '✅ OK' : '❌ Fehler'}`, results.userbot ? 'green' : 'red');
    log(`Frontend (${FRONTEND_URL}): ${results.frontend ? '✅ OK' : '❌ Fehler'}`, results.frontend ? 'green' : 'red');
    log(`CORS: ${results.cors ? '✅ OK' : '❌ Fehler'}`, results.cors ? 'green' : 'red');
    
    // Empfehlungen
    log('\n💡 Empfehlungen für öffentlichen Zugriff:', 'yellow');
    log('=' .repeat(40), 'yellow');
    
    if (!results.backend) {
      log('1. Backend-Server prüfen: Ist der Server auf api.bit-team-bot.online erreichbar?', 'yellow');
    }
    
    if (!results.userbot) {
      log('2. Userbot ist optional - Login funktioniert auch ohne', 'blue');
    }
    
    if (!results.frontend) {
      log('3. Frontend-Server prüfen: Ist der Server auf webui.bit-team-bot.online erreichbar?', 'yellow');
    }
    
    if (!results.cors) {
      log('4. CORS-Probleme - prüfe Backend-Konfiguration für Cross-Origin-Requests', 'yellow');
    }
    
    if (results.backend && results.frontend) {
      logSuccess('🎉 Öffentliche Verbindungen funktionieren!');
      log(`Öffne ${FRONTEND_URL}/login im Browser`, 'green');
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
  testSSL,
  testDNS
}; 
/**
 * Test-Skript für automatisierten Userbot-Flow
 * 
 * Dieses Skript demonstriert, wie der Userbot-Service automatisch
 * über HTTP-API-Calls gesteuert werden kann, ohne Terminal-Interaktion.
 * 
 * Verwendung:
 * 1. Stelle sicher, dass der Userbot-Service läuft (Port 8001)
 * 2. Führe dieses Skript aus: node test-userbot-flow.js
 * 3. Folge den Anweisungen im Terminal
 */

const axios = require('axios');

// Konfiguration
const USERBOT_API_URL = 'http://localhost:8001';
const TEST_PHONE = '+49123456789'; // Ersetze durch deine Test-Nummer

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

const logStep = (step, message) => {
  log(`\n${step}. ${message}`, 'cyan');
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

/**
 * Test 1: Userbot-Status abrufen
 */
async function testUserbotStatus() {
  logStep('1', 'Prüfe Userbot-Status...');
  
  try {
    const response = await axios.get(`${USERBOT_API_URL}/status`);
    logSuccess('Userbot-Status erfolgreich abgerufen');
    logInfo(`Status: ${JSON.stringify(response.data, null, 2)}`);
    return response.data;
  } catch (error) {
    logError(`Fehler beim Abrufen des Status: ${error.message}`);
    if (error.response) {
      logError(`HTTP Status: ${error.response.status}`);
      logError(`Response: ${JSON.stringify(error.response.data, null, 2)}`);
    }
    throw error;
  }
}

/**
 * Test 2: Verifizierungscode anfordern
 */
async function testRequestCode(phone) {
  logStep('2', `Fordere Verifizierungscode für ${phone} an...`);
  
  try {
    const response = await axios.post(`${USERBOT_API_URL}/start`, { phone }, {
      timeout: 15000,
      headers: { 'Content-Type': 'application/json' }
    });
    
    logSuccess('Code-Anfrage erfolgreich');
    logInfo(`Response: ${JSON.stringify(response.data, null, 2)}`);
    return response.data;
  } catch (error) {
    logError(`Fehler bei Code-Anfrage: ${error.message}`);
    if (error.response) {
      logError(`HTTP Status: ${error.response.status}`);
      logError(`Response: ${JSON.stringify(error.response.data, null, 2)}`);
    }
    throw error;
  }
}

/**
 * Test 3: Code verifizieren
 */
async function testVerifyCode(phone, code) {
  logStep('3', `Verifiziere Code ${code} für ${phone}...`);
  
  try {
    const response = await axios.post(`${USERBOT_API_URL}/verify`, { phone, code }, {
      timeout: 15000,
      headers: { 'Content-Type': 'application/json' }
    });
    
    logSuccess('Code-Verifizierung erfolgreich');
    logInfo(`Response: ${JSON.stringify(response.data, null, 2)}`);
    return response.data;
  } catch (error) {
    logError(`Fehler bei Code-Verifizierung: ${error.message}`);
    if (error.response) {
      logError(`HTTP Status: ${error.response.status}`);
      logError(`Response: ${JSON.stringify(error.response.data, null, 2)}`);
    }
    throw error;
  }
}

/**
 * Test 4: Vollständiger Flow (Code anfordern + verifizieren)
 */
async function testCompleteFlow(phone) {
  log('\n🚀 Starte vollständigen Userbot-Flow Test', 'magenta');
  log('=' .repeat(50), 'magenta');
  
  try {
    // Schritt 1: Status prüfen
    await testUserbotStatus();
    
    // Schritt 2: Code anfordern
    const codeRequest = await testRequestCode(phone);
    
    if (codeRequest.status !== 'code_sent') {
      throw new Error(`Unerwarteter Status: ${codeRequest.status}`);
    }
    
    // Schritt 3: Code vom User eingeben lassen
    logStep('3', 'Warte auf Code-Eingabe...');
    logWarning('Bitte gib den Code ein, der an deine Telegram-Nummer gesendet wurde:');
    
    // In einer echten Anwendung würde hier der Code aus dem Frontend kommen
    // Hier simulieren wir die Eingabe
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const code = await new Promise((resolve) => {
      rl.question('Code eingeben: ', (input) => {
        rl.close();
        resolve(input.trim());
      });
    });
    
    if (!code) {
      throw new Error('Kein Code eingegeben');
    }
    
    // Schritt 4: Code verifizieren
    const verification = await testVerifyCode(phone, code);
    
    if (verification.status === 'success') {
      logSuccess('🎉 Vollständiger Flow erfolgreich abgeschlossen!');
      logInfo('Die Userbot-Session ist jetzt aktiv und kann verwendet werden.');
    } else {
      throw new Error(`Verifizierung fehlgeschlagen: ${verification.message}`);
    }
    
  } catch (error) {
    logError(`Flow-Test fehlgeschlagen: ${error.message}`);
    throw error;
  }
}

/**
 * Test 5: Frontend-Integration simulieren
 */
async function testFrontendIntegration() {
  log('\n🌐 Frontend-Integration Test', 'magenta');
  log('=' .repeat(50), 'magenta');
  
  // Simuliere die API-Calls, die das Frontend machen würde
  const frontendCalls = [
    {
      name: 'Userbot Create Session (Frontend)',
      method: 'POST',
      url: `${USERBOT_API_URL}/userbot/create-session`,
      data: { phone_number: TEST_PHONE }
    },
    {
      name: 'Userbot Verify Code (Frontend)',
      method: 'POST',
      url: `${USERBOT_API_URL}/userbot/verify-code`,
      data: { phone_number: TEST_PHONE, code: '123456' }
    },
    {
      name: 'Userbot Session Status (Frontend)',
      method: 'GET',
      url: `${USERBOT_API_URL}/userbot/session-status/${TEST_PHONE}`
    },
    {
      name: 'Userbot Chats (Frontend)',
      method: 'GET',
      url: `${USERBOT_API_URL}/userbot/chats/${TEST_PHONE}`
    }
  ];
  
  for (const call of frontendCalls) {
    logStep('Frontend', `${call.name}...`);
    
    try {
      const config = {
        method: call.method,
        url: call.url,
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      };
      
      if (call.data) {
        config.data = call.data;
      }
      
      const response = await axios(config);
      logSuccess(`${call.name} erfolgreich`);
      logInfo(`Response: ${JSON.stringify(response.data, null, 2)}`);
      
    } catch (error) {
      logError(`${call.name} fehlgeschlagen: ${error.message}`);
    }
  }
}

/**
 * Hauptfunktion
 */
async function main() {
  log('🤖 Userbot-Flow Test Suite', 'bright');
  log('Dieses Skript testet die automatisierten Userbot-API-Calls', 'reset');
  log('Stelle sicher, dass der Userbot-Service auf Port 8001 läuft!', 'yellow');
  
  try {
    // Prüfe ob Userbot-Service erreichbar ist
    logStep('0', 'Prüfe Userbot-Service-Verfügbarkeit...');
    await axios.get(`${USERBOT_API_URL}/`, { timeout: 5000 });
    logSuccess('Userbot-Service ist erreichbar');
    
    // Führe Tests aus
    await testUserbotStatus();
    await testFrontendIntegration();
    
    // Vollständiger Flow (nur wenn gewünscht)
    log('\nMöchtest du den vollständigen Flow mit Code-Eingabe testen? (j/n)', 'yellow');
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const answer = await new Promise((resolve) => {
      rl.question('Antwort: ', (input) => {
        rl.close();
        resolve(input.trim().toLowerCase());
      });
    });
    
    if (answer === 'j' || answer === 'ja' || answer === 'y' || answer === 'yes') {
      await testCompleteFlow(TEST_PHONE);
    } else {
      logInfo('Vollständiger Flow übersprungen');
    }
    
    logSuccess('\n🎉 Alle Tests abgeschlossen!');
    
  } catch (error) {
    logError(`\n❌ Test-Suite fehlgeschlagen: ${error.message}`);
    process.exit(1);
  }
}

// Skript ausführen
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  testUserbotStatus,
  testRequestCode,
  testVerifyCode,
  testCompleteFlow,
  testFrontendIntegration
}; 
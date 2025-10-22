// --------------------------
// 2025-ready Instagram DM Bot
// --------------------------

const { IgApiClient } = require('instagram-private-api');
const { RealtimeClient } = require('instagram_mqtt');
const fs = require('fs');
const path = require('path');

const USERNAME = 'spyther6';
const PASSWORD = 'Spyther@7860'; // optional if you have browser cookies
const SESSION_FILE = path.join(__dirname, 'ig-session.json');
const DEBUG = true; // true = full debug logs

// Static replies
const staticReplies = {
  hi: '👋 Hello! Bot is online.',
  hello: '👋 Hello! Bot is online.',
  price: '💰 Current price: $100',
  time: () => `⏰ Current time: ${new Date().toLocaleTimeString()}`,
};

// --------------------------
// Initialize Instagram API
// --------------------------
const ig = new IgApiClient();
ig.state.generateDevice(USERNAME);

// --------------------------
// Login & Session Handling
// --------------------------
async function login() {
  try {
    if (fs.existsSync(SESSION_FILE)) {
      const savedSession = require(SESSION_FILE);
      await ig.state.deserializeCookieJar(savedSession);
      console.log('✅ Loaded saved session');
    } else {
      console.log('⚠️ No saved session, logging in with credentials...');
      await ig.simulate.preLoginFlow();
      await ig.account.login(USERNAME, PASSWORD);
      await ig.simulate.postLoginFlow();

      const serialized = await ig.state.serializeCookieJar();
      fs.writeFileSync(SESSION_FILE, JSON.stringify(serialized, null, 2));
      console.log('✅ Session saved');
    }

    const me = await ig.account.currentUser();
    console.log(`✅ Logged in as: @${me.username}`);
    return me;
  } catch (err) {
    console.error('❌ Login/session failed:', err);
    process.exit(1);
  }
}

// --------------------------
// Initialize Realtime DM client
// --------------------------
async function startBot() {
  const me = await login();

  const client = new RealtimeClient(ig, { debug: DEBUG });

  try {
    await client.connect();
    console.log('✅ Realtime DM bot connected');
  } catch (err) {
    console.error('❌ Realtime connection failed:', err);
    process.exit(1);
  }

  client.on('message', async (message) => {
    try {
      if (!message.content) return;
      if (message.author.id === ig.state.cookieUserId) return;

      const msg = message.content.toLowerCase().trim();
      let reply = staticReplies[msg] || '🤖 I saw your message but I don’t have a reply for this.';

      if (typeof reply === 'function') reply = reply();

      await message.reply(reply);
      if (DEBUG) console.log(`📩 Replied to ${message.author.username}: ${reply}`);
    } catch (err) {
      console.error('❌ Failed to send reply:', err);
    }
  });

  client.on('connected', () => {
    console.log('🟢 Bot is ready and listening to DMs...');
  });

  client.on('error', (err) => {
    console.error('⚠️ Realtime client error:', err);
  });
}

// --------------------------
// Run the bot
// --------------------------
startBot();
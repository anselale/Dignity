# 🤖 Setting Up Your Discord Bot (Developer Portal Guide)

Before Dignity can join your server and begin processing history, you need to create an official "Application" in the Discord Developer Portal. This gives you the `DISCORD_TOKEN` required to connect the AgentForge architecture to Discord's servers.

Here is the step-by-step guide to setting up your bot, enabling the correct intents, and granting the exact permissions the architecture requires.

### Step 1: Create the Application
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and log in with your Discord account.
2. Click the **New Application** button in the top right corner.
3. Give your application a name (e.g., "Dignity") and agree to the Terms of Service. Click **Create**.
4. *(Optional)* On the **General Information** page, you can upload an App Icon. This will be Dignity's profile picture.

### Step 2: Configure the Bot Profile & Intents
1. On the left-hand menu, click on the **Bot** tab.
2. Edit the **Username** if needed (this is the name that will appear in your server).
3. **CRITICAL:** Scroll down to the **Privileged Gateway Intents** section. Dignity's cognitive architecture *requires* the ability to read what people are saying to build her memory.
   * Turn **ON** the `Message Content Intent` (Allows her to read the actual text of messages).
   * Turn **ON** the `Server Members Intent` (Highly recommended to ensure she can accurately resolve user mentions).
4. Click **Save Changes** at the bottom of the screen.

### Step 3: Get Your Bot Token
1. Scroll back up to the top of the **Bot** page.
2. Under the username, click the **Reset Token** button. (You may be prompted to enter an authenticator code).
3. A long string of characters will appear. **Click Copy.**
   * ⚠️ **WARNING:** Treat this token like a bank password. Do not share it, and absolutely do *not* commit it to GitHub.
4. Paste this token into your computer's Environment Variables (or your `.env` file) as:
   ```text
   DISCORD_TOKEN=your_copied_token_here
   ```

### Step 4: Generate the Correct Invite Link
Now that the bot exists, you need to invite it to your server with the exact permissions AgentForge requires to operate.

1. On the left-hand menu, click on **OAuth2**, then select **OAuth2 URL Generator**.
2. Under the **Scopes** checklist, you MUST check two boxes:
   * `bot`
   * `applications.commands` *(Required for Dignity's slash commands to sync with your server)*
3. A new **Bot Permissions** checklist will appear at the bottom. To ensure Dignity's cognitive pipeline and UI features don't throw `403 Forbidden` errors, select the following exact permissions:

   * **Text Permissions:**
     * `Read Messages/View Channels`
     * `Send Messages`
     * `Use Application Commands` *(Required for users to trigger her slash commands)*
     * `Embed Links` *(Required for formatting output)*
     * `Attach Files` *(Required if the bot outputs memory files)*
     * `Read Message History`
     * `Add Reactions` *(Required if the bot reacts to indicate it is "thinking")*
   * **Thread Permissions (CRITICAL for Internal Cognition):**
     * `Create Public Threads`
     * `Create Private Threads`
     * `Send Messages in Threads`
     * `Manage Threads` *(Strictly required to remove users from her internal thought threads)*
   * *(Alternatively: Select `Administrator` if you are running this on a private testing server and want to bypass setting individual channel permissions).*

4. Scroll to the very bottom of the page and click **Copy** on the Generated URL.

### Step 5: Invite Dignity to Your Server
1. Paste the copied URL into your web browser.
2. Select the server you want to invite Dignity to from the dropdown menu.
3. Click **Continue**, then **Authorize**.

Once she is in the server, ensure your Python environment is running `main.py`. If her token and permissions are set correctly, Dignity will come online, sync her slash commands, and her cognitive stack will begin listening!
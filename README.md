# 👑 ZEBLASKI OFFICIAL BOT

A Discord bot engineered specifically for **ZEBLASKI GANG**, featuring two dedicated systems:
1. **In-Game Name (IGN) Registration System**
2. **Gang Recruitment Application System**

---

## ⚡ How to Run 24/7 (Without Manually Starting)

You have two simple ways to keep the bot running 24/7:

### Option 1: Run 24/7 in Background on this PC (Instant & Free)

Double-click **`install_autostart_24_7.bat`** once. That's it!

- ✅ **Completely Silent**: Runs invisibly in the background (no open black cmd windows).
- ✅ **Auto-Starts on Boot**: Starts automatically whenever your PC turns on or reboots.
- ✅ **Auto-Restart on Crash**: If Discord has a connection drop or the bot stops, it restarts automatically within 5 seconds.
- 🔍 **Check Status**: Double-click **`check_bot_status.bat`** anytime to see if the bot is online, its process ID, and recent logs.
- 🛑 **Stop Bot**: Double-click **`stop_bot.bat`** to stop the background bot process.
- ❌ **Uninstall Auto-Start**: Double-click **`uninstall_autostart.bat`** if you ever want to remove it from Windows startup.

---

### Option 2: 24/7 Cloud Hosting (Online Even When PC is Shut Down)

If you turn off your PC at night and want the bot online 24/7 in the cloud:

#### A. Free Discord Bot Hosting via Discloud:
1. Join the [Discloud Discord Server](https://discloud.com/) or visit their website.
2. Select your bot folder (it already contains `discloud.config`).
3. Upload via the `.upload` command in Discloud or through their web dashboard.
4. Your bot runs 24/7 on cloud servers with auto-restart!

#### B. Free Cloud Hosting via Railway / Render:
1. Push your folder to a private GitHub repository.
2. Link the repository to [Railway.app](https://railway.app/) or [Render.com](https://render.com/).
3. Add your `DISCORD_TOKEN` in the Environment Variables tab.
4. The included `Dockerfile` and `Procfile` will deploy it automatically!

---

## 🎮 System 1: In-Game Name (IGN) Register

### 1. Registration Panel (Photo 1 Match)
- Embed with signature blue border (`#0055ff`).
- Title: **`IN-GAME-NAME REGISTER`**
- Red button: **`IG-NAME REGISTER`**.

### 2. Submission Modal (Photo 2 Match)
Pops up with all 4 fields:
- `OOC Name *` (e.g. `Gulam_Scofield`)
- `IG Name *` (e.g. `Manu_N12`)
- `Server Name *` (e.g. `XLANTIS CITY`)
- `Your Current Level / Rank *` (e.g. `42`)

### 3. DC Moderator Review System
- Dispatched to the review channel with **Accept** (Green) and **Reject** (Red) buttons.
- Only users with the **DC Moderator** role can approve or reject.

### 4. Dynamic Approved Card (Photo 3 Match)
- **Profile Place**: Applicant's circular Discord avatar in glowing neon green frame.
- **`CURRENT NAME` Tab**: Applicant's Discord username.
- **`Registered Name` Tab**: The newly registered In-Game Name.
- **`LEVEL` Tab**: Registered level.
- **`REVIEWED BY` Tab**: The DC Moderator who reviewed and approved.

### 5. Dynamic Declined Card (Photo 4 Match)
- **Profile Place**: Applicant's circular Discord avatar in red glowing frame.
- **`CURRENT NAME` Tab**: Applicant's Discord username.
- **`Registered Name` Tab**: Automatically displays **`NONE`**.
- **`LEVEL` Tab**: Applicant's level.
- **`REVIEWED BY` Tab**: The DC Moderator who declined the submission.

---

## 👑 System 2: Gang Recruitment Application

- **Panel Command**: `/setup_panel` or `!setuppanel`
- **Application Modal**: All 8 fields (Gang Name, Rank, Reason, OOC Name, OOC Age, IG Name, Experience, Phone).
- **Review**: Moderator Accept/Reject buttons.
- **Results Cards**: Generates recruitment acceptance (Photo 3) or rejection (Photo 4) with avatar & username badge.

---

## 🛠️ Complete Bot Commands

### 🎮 In-Game Name (IGN) Register Commands
| Slash Command | Prefix Command | Permissions | Description |
|---|---|---|---|
| `/setup_ign_panel` | `!setupign` | Administrator | Posts the IGN Registration panel (Photo 1) with the red button. |
| `/set_ign_review_channel <#channel>` | `!setignreviewchannel <#channel>` | Administrator | Sets channel for IGN moderator reviews. |
| `/set_ign_results_channel <#channel>` | `!setignresultschannel <#channel>` | Administrator | Sets channel where approved/declined cards are posted. |
| `/test_ign_card <user> <ign> <lvl> <approved>` | — | Administrator | Previews the Photo 3 (Approved) or Photo 4 (Declined) IGN card. |

### 👑 Gang Recruitment Commands
| Slash Command | Prefix Command | Permissions | Description |
|---|---|---|---|
| `/setup_panel` | `!setuppanel` | Administrator | Posts the recruitment panel with banner and Apply button. |
| `/set_member_role <@role>` | `!setmemberrole <@role>` | Administrator | Role automatically assigned to accepted members. |
| `/test_card <user> <approved>` | — | Administrator | Previews recruitment approved/declined cards. |

### ⚙️ General & Role Settings
| Slash Command | Prefix Command | Permissions | Description |
|---|---|---|---|
| `/set_moderator_role <@role>` | `!setmodrole <@role>` | Administrator | Sets the DC Moderator role allowed to review all submissions. |
| `/set_review_channel <#channel>` | `!setreviewchannel <#channel>` | Administrator | Default review channel. |
| `/set_results_channel <#channel>` | `!setresultschannel <#channel>` | Administrator | Default results channel. |
| `/help_zeblaski` | `!help` | Everyone | Displays help menu with all commands. |

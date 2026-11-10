import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Default role name for reviewers if not configured per guild
DEFAULT_MOD_ROLE_NAME = os.getenv("DEFAULT_MOD_ROLE_NAME", "DC Moderator")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Gang Application assets (Photos 1, 3, 4 from recruitment)
BANNER_PATH = os.path.join(ASSETS_DIR, "gang_banner.png")
APPROVED_TEMPLATE_PATH = os.path.join(ASSETS_DIR, "photo3_approved_template.jpg")
DECLINED_TEMPLATE_PATH = os.path.join(ASSETS_DIR, "photo4_declined_template.jpg")

# In-Game Name (IGN) Register assets (Photos 3 & 4 from IGN system)
IGN_APPROVED_TEMPLATE_PATH = os.path.join(ASSETS_DIR, "ign_photo3_approved.jpg")
IGN_DECLINED_TEMPLATE_PATH = os.path.join(ASSETS_DIR, "ign_photo4_declined.jpg")

# Whether the REVIEWED BY tab displays the moderator name (default) or applicant name
IGN_REVIEW_TAB_TEXT = os.getenv("IGN_REVIEW_TAB_TEXT", "moderator")

# Embed colors
EMBED_COLOR_BLUE = 0x0055ff
EMBED_COLOR_GOLD = 0xf1c40f
EMBED_COLOR_GREEN = 0x2ecc71
EMBED_COLOR_RED = 0xe74c3c

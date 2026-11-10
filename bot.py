import os
import sys
import io
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Dict, Any

import config
import database
import image_generator
import ign_image_generator

# Initialize SQLite database
database.init_db()

# Temporary cache for two-step application submissions: user_id -> dict
temp_applications: Dict[int, Dict[str, Any]] = {}

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# -------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------

def is_moderator(member: discord.Member, guild_id: int) -> bool:
    """Check if member has the DC Moderator role or administrator rights."""
    if member.guild_permissions.administrator:
        return True
    
    settings = database.get_guild_settings(guild_id)
    mod_role_id = settings.get("mod_role_id")
    
    for role in member.roles:
        if mod_role_id and role.id == mod_role_id:
            return True
        if role.name.lower() in ["dc moderator", "moderator", "mod", "admin", "administrator"]:
            return True
    return False

def get_target_channels(guild: discord.Guild, for_ign: bool = False):
    """Retrieve review and results channels according to guild settings."""
    settings = database.get_guild_settings(guild.id)
    review_channel = None
    results_channel = None
    
    if for_ign:
        # Check if dedicated IGN channels are configured, else fallback to standard
        ign_rev_id = settings.get("ign_review_channel_id") or settings.get("review_channel_id")
        ign_res_id = settings.get("ign_results_channel_id") or settings.get("results_channel_id")
        if ign_rev_id:
            review_channel = guild.get_channel(ign_rev_id)
        if ign_res_id:
            results_channel = guild.get_channel(ign_res_id)
    else:
        if settings.get("review_channel_id"):
            review_channel = guild.get_channel(settings["review_channel_id"])
        if settings.get("results_channel_id"):
            results_channel = guild.get_channel(settings["results_channel_id"])
        
    return review_channel, results_channel

def build_recruitment_embed() -> discord.Embed:
    """Build the exact recruitment embed matching Photo 1."""
    embed = discord.Embed(
        title="GANG APPLICATION",
        color=config.EMBED_COLOR_BLUE,
        description=(
            "Submit a request using the button below.\n"
            "An admin will review it as soon as possible.\n\n"
            "**REQUIREMENTS**\n"
            "•Active and loyal members\n"
            "•Good teamwork\n"
            "•Respect towards gang members\n"
            "•Active participation\n"
            "•Must follow gang rules\n\n"
            "**WHAT WE OFFER**\n"
            "•Active & organized gang\n"
            "•Strong brotherhood & teamwork\n"
            "•Gang activities & opportunities\n"
            "•Wars, missions & street domination\n"
            "•Respect for loyal members\n"
            "•Chill vibes + serious gameplay"
        )
    )
    embed.set_image(url="attachment://banner.png")
    return embed

def build_ign_embed() -> discord.Embed:
    """Build the exact IN-GAME-NAME REGISTER embed matching Photo 1."""
    embed = discord.Embed(
        title="IN-GAME-NAME REGISTER",
        color=config.EMBED_COLOR_BLUE,
        description=(
            "WELCOME TO IN-GAME NAME SUBMISSION!\n\n"
            "ALL ZEBLASKI GANG MEMBERS MUST SUBMIT THEIR CURRENT SA-MP IN-GAME NAME HERE.\n\n"
            "⚠️ NOTE\n\n"
            "• SUBMIT YOUR CORRECT IN-GAME NAME.\n"
            "• UPDATE YOUR IGN IF IT CHANGES.\n"
            "• DO NOT SPAM THIS CHANNEL."
        )
    )
    return embed


# =============================================================
# SYSTEM 1: GANG RECRUITMENT APPLICATION (MODALS & VIEWS)
# =============================================================

class GangApplicationStep2Modal(discord.ui.Modal, title="Gang Application (Part 2/2)"):
    ooc_name = discord.ui.TextInput(
        label="OOC Name *",
        placeholder="Enter your OOC Name...",
        min_length=1,
        max_length=100,
        required=True
    )
    ooc_age = discord.ui.TextInput(
        label="OOC Age *",
        placeholder="Enter your OOC Age...",
        min_length=1,
        max_length=20,
        required=True
    )
    experience = discord.ui.TextInput(
        label="Experience *",
        placeholder="Tell us about your experience...",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=1000,
        required=True
    )
    reason_for_change = discord.ui.TextInput(
        label="Reason for Gang Change *",
        placeholder="Explain why you want to change your gang...",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=1000,
        required=True
    )

    def __init__(self, step1_data: Dict[str, Any]):
        super().__init__()
        self.step1_data = step1_data

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        full_data = {
            "user_id": user.id,
            "username": user.name,
            "display_name": user.display_name,
            "avatar_url": user.display_avatar.url,
            "new_gang_name": self.step1_data["new_gang_name"],
            "current_level": self.step1_data["current_level"],
            "ig_name": self.step1_data["ig_name"],
            "ph_number": self.step1_data["ph_number"],
            "ooc_name": self.ooc_name.value.strip(),
            "ooc_age": self.ooc_age.value.strip(),
            "experience": self.experience.value.strip(),
            "reason_for_change": self.reason_for_change.value.strip()
        }
        
        app_id = database.create_application(full_data)
        temp_applications.pop(user.id, None)
        
        await interaction.followup.send(
            "✅ **Your gang application has been submitted successfully!**\n"
            "An administrator or DC Moderator will review your submission soon.",
            ephemeral=True
        )
        
        guild = interaction.guild
        if not guild:
            return
            
        review_channel, _ = get_target_channels(guild, for_ign=False)
        if not review_channel:
            review_channel = interaction.channel
            
        review_embed = discord.Embed(
            title="📥 NEW GANG RECRUITMENT SUBMISSION",
            color=config.EMBED_COLOR_GOLD,
            description=f"**Application ID:** `#{app_id}`\n**Applicant:** {user.mention} (`{user.name}` | ID: `{user.id}`)"
        )
        review_embed.set_thumbnail(url=user.display_avatar.url)
        review_embed.add_field(name="🏷️ New Gang Name", value=full_data["new_gang_name"], inline=True)
        review_embed.add_field(name="🎖️ Current Level / Rank", value=full_data["current_level"], inline=True)
        review_embed.add_field(name="🎮 In-Game (IG) Name", value=full_data["ig_name"], inline=True)
        review_embed.add_field(name="📞 Phone Number", value=full_data["ph_number"], inline=True)
        review_embed.add_field(name="🧑 OOC Name", value=full_data["ooc_name"], inline=True)
        review_embed.add_field(name="🎂 OOC Age", value=full_data["ooc_age"], inline=True)
        review_embed.add_field(name="📜 Experience", value=full_data["experience"], inline=False)
        review_embed.add_field(name="🔄 Reason for Gang Change", value=full_data["reason_for_change"], inline=False)
        review_embed.set_footer(text=f"ZEBLASKI OFFICIAL BOT • Submission #{app_id}")
        review_embed.timestamp = discord.utils.utcnow()
        
        review_view = ModeratorReviewView(app_id=app_id)
        msg = await review_channel.send(
            content=f"🔔 **Attention DC Moderators:** New recruitment application from {user.mention}!",
            embed=review_embed,
            view=review_view
        )
        database.update_application_message(app_id, msg.id, review_channel.id)


class Step2PromptView(discord.ui.View):
    def __init__(self, step1_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.step1_data = step1_data

    @discord.ui.button(label="Continue to Part 2 (Final Step)", style=discord.ButtonStyle.success, emoji="➡️")
    async def continue_step2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GangApplicationStep2Modal(self.step1_data))


class GangApplicationStep1Modal(discord.ui.Modal, title="Gang Application (Part 1/2)"):
    new_gang_name = discord.ui.TextInput(
        label="New Gang Name (Format: Firstname_Lastname) *",
        placeholder="e.g. Gulan_Scofield / Manu_N12 / Bs12_Fans",
        min_length=1,
        max_length=100,
        required=True
    )
    current_level = discord.ui.TextInput(
        label="Your Current Level / Rank *",
        placeholder="42 / Enter Exact Level In In-Game",
        min_length=1,
        max_length=50,
        required=True
    )
    ig_name = discord.ui.TextInput(
        label="IG Name *",
        placeholder="Enter your IG Name...",
        min_length=1,
        max_length=100,
        required=True
    )
    ph_number = discord.ui.TextInput(
        label="PH Number *",
        placeholder="Enter your Phone Number...",
        min_length=1,
        max_length=50,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        step1_data = {
            "new_gang_name": self.new_gang_name.value.strip(),
            "current_level": self.current_level.value.strip(),
            "ig_name": self.ig_name.value.strip(),
            "ph_number": self.ph_number.value.strip()
        }
        temp_applications[interaction.user.id] = step1_data
        
        prompt_view = Step2PromptView(step1_data)
        await interaction.response.send_message(
            "📋 **Part 1 Saved!** Click the button below to complete **Part 2** (OOC & Experience):",
            view=prompt_view,
            ephemeral=True
        )


class ApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Apply for gang application",
        style=discord.ButtonStyle.success,
        custom_id="zeblaski_apply_button"
    )
    async def apply_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GangApplicationStep1Modal())


class ModeratorReviewView(discord.ui.View):
    def __init__(self, app_id: int):
        super().__init__(timeout=None)
        self.app_id = app_id
        
        accept_btn = discord.ui.Button(
            label="Accept",
            style=discord.ButtonStyle.success,
            emoji="✅",
            custom_id=f"zeblaski:accept:{app_id}"
        )
        accept_btn.callback = self.accept_callback
        self.add_item(accept_btn)
        
        reject_btn = discord.ui.Button(
            label="Reject",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            custom_id=f"zeblaski:reject:{app_id}"
        )
        reject_btn.callback = self.reject_callback
        self.add_item(reject_btn)

    async def check_permission(self, interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        member = interaction.guild.get_member(interaction.user.id)
        if not member or not is_moderator(member, interaction.guild.id):
            await interaction.response.send_message(
                "⛔ **Access Denied:** Only members with the **DC Moderator** role can accept or reject applications.",
                ephemeral=True
            )
            return False
        return True

    async def accept_callback(self, interaction: discord.Interaction):
        if not await self.check_permission(interaction):
            return
            
        await interaction.response.defer()
        app_id = self.app_id
        app_data = database.get_application(app_id)
        if not app_data:
            await interaction.followup.send("⚠️ Application not found.", ephemeral=True)
            return
            
        if app_data["status"] != "PENDING":
            await interaction.followup.send(f"⚠️ This application has already been **{app_data['status']}**.", ephemeral=True)
            return
            
        database.update_application_status(app_id, "APPROVED", interaction.user.id, interaction.user.name)
        
        guild = interaction.guild
        applicant_id = app_data["user_id"]
        applicant = guild.get_member(applicant_id) if guild else None
        if not applicant:
            try:
                applicant = await bot.fetch_user(applicant_id)
            except Exception:
                applicant = None

        if applicant:
            avatar_img = await image_generator.fetch_user_avatar(applicant)
            username_display = applicant.name
        else:
            avatar_img = await image_generator.fetch_user_avatar(interaction.user)
            username_display = app_data["username"]

        card_bytes = image_generator.generate_result_card(
            template_path=config.APPROVED_TEMPLATE_PATH,
            avatar_img=avatar_img,
            username=username_display,
            is_approved=True
        )
        discord_file = discord.File(card_bytes, filename=f"approved_{username_display}.png")

        for item in self.children:
            item.disabled = True
            
        orig_embed = interaction.message.embeds[0] if interaction.message.embeds else discord.Embed()
        orig_embed.color = config.EMBED_COLOR_GREEN
        orig_embed.add_field(
            name="📌 Status",
            value=f"✅ **ACCEPTED** by {interaction.user.mention} (`{interaction.user.name}`)",
            inline=False
        )
        await interaction.message.edit(embed=orig_embed, view=self)

        _, results_ch = get_target_channels(guild, for_ign=False)
        post_channel = results_ch or interaction.channel
        
        await post_channel.send(
            content=(
                f"🎉 **CONGRATULATIONS!** <@{applicant_id}> has been officially **ACCEPTED** "
                f"into **ZEBLASKI GANG** by {interaction.user.mention}!"
            ),
            file=discord_file
        )

        settings = database.get_guild_settings(guild.id)
        if settings.get("member_role_id") and isinstance(applicant, discord.Member):
            role = guild.get_role(settings["member_role_id"])
            if role:
                try:
                    await applicant.add_roles(role, reason="Zeblaski Gang Application Accepted")
                except Exception as e:
                    print(f"Failed to assign role: {e}")

        if applicant:
            try:
                dm_card_bytes = io.BytesIO(card_bytes.getvalue())
                dm_file = discord.File(dm_card_bytes, filename="zeblaski_approved.png")
                await applicant.send(
                    content=(
                        f"👑 **WELCOME TO ZEBLASKI GANG!**\n"
                        f"Your recruitment application has been **ACCEPTED** by {interaction.user.name}!\n"
                        f"Here is your official acceptance card:"
                    ),
                    file=dm_file
                )
            except Exception as e:
                print(f"Could not send DM to applicant: {e}")

        await interaction.followup.send(f"✅ Application `#{app_id}` accepted successfully!", ephemeral=True)

    async def reject_callback(self, interaction: discord.Interaction):
        if not await self.check_permission(interaction):
            return
            
        await interaction.response.defer()
        app_id = self.app_id
        app_data = database.get_application(app_id)
        if not app_data:
            await interaction.followup.send("⚠️ Application not found.", ephemeral=True)
            return
            
        if app_data["status"] != "PENDING":
            await interaction.followup.send(f"⚠️ This application has already been **{app_data['status']}**.", ephemeral=True)
            return
            
        database.update_application_status(app_id, "REJECTED", interaction.user.id, interaction.user.name)
        
        guild = interaction.guild
        applicant_id = app_data["user_id"]
        applicant = guild.get_member(applicant_id) if guild else None
        if not applicant:
            try:
                applicant = await bot.fetch_user(applicant_id)
            except Exception:
                applicant = None

        if applicant:
            avatar_img = await image_generator.fetch_user_avatar(applicant)
            username_display = applicant.name
        else:
            avatar_img = await image_generator.fetch_user_avatar(interaction.user)
            username_display = app_data["username"]

        card_bytes = image_generator.generate_result_card(
            template_path=config.DECLINED_TEMPLATE_PATH,
            avatar_img=avatar_img,
            username=username_display,
            is_approved=False
        )
        discord_file = discord.File(card_bytes, filename=f"declined_{username_display}.png")

        for item in self.children:
            item.disabled = True
            
        orig_embed = interaction.message.embeds[0] if interaction.message.embeds else discord.Embed()
        orig_embed.color = config.EMBED_COLOR_RED
        orig_embed.add_field(
            name="📌 Status",
            value=f"❌ **REJECTED** by {interaction.user.mention} (`{interaction.user.name}`)",
            inline=False
        )
        await interaction.message.edit(embed=orig_embed, view=self)

        _, results_ch = get_target_channels(guild, for_ign=False)
        post_channel = results_ch or interaction.channel
        
        await post_channel.send(
            content=(
                f"⚠️ **APPLICATION DECLINED**: <@{applicant_id}>'s application was **DECLINED** "
                f"by {interaction.user.mention}."
            ),
            file=discord_file
        )

        if applicant:
            try:
                dm_card_bytes = io.BytesIO(card_bytes.getvalue())
                dm_file = discord.File(dm_card_bytes, filename="zeblaski_declined.png")
                await applicant.send(
                    content=(
                        f"❌ Your recruitment application to **ZEBLASKI GANG** was reviewed and **DECLINED**.\n"
                        f"Thank you for your interest."
                    ),
                    file=dm_file
                )
            except Exception as e:
                print(f"Could not send DM to applicant: {e}")

        await interaction.followup.send(f"❌ Application `#{app_id}` rejected.", ephemeral=True)


# =============================================================
# SYSTEM 2: IN-GAME-NAME (IGN) REGISTER (MODALS & VIEWS)
# =============================================================

class IgnRegisterModal(discord.ui.Modal, title="IG-Name Register"):
    """Modal with all 4 fields matching Photo 2 of IGN system."""
    
    ooc_name = discord.ui.TextInput(
        label="OOC Name *",
        placeholder="e.g. Gulam_Scofield",
        min_length=1,
        max_length=100,
        required=True
    )
    ig_name = discord.ui.TextInput(
        label="IG Name *",
        placeholder="e.g. Manu_N12",
        min_length=1,
        max_length=100,
        required=True
    )
    server_name = discord.ui.TextInput(
        label="Server Name *",
        placeholder="XLANTIS CITY",
        min_length=1,
        max_length=100,
        required=True
    )
    current_level = discord.ui.TextInput(
        label="Your Current Level / Rank *",
        placeholder="42 / Enter Exact Level In In-Game",
        min_length=1,
        max_length=50,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        
        reg_data = {
            "user_id": user.id,
            "username": user.name,
            "display_name": user.display_name,
            "avatar_url": user.display_avatar.url,
            "ooc_name": self.ooc_name.value.strip(),
            "ig_name": self.ig_name.value.strip(),
            "server_name": self.server_name.value.strip(),
            "current_level": self.current_level.value.strip()
        }
        
        reg_id = database.create_ign_registration(reg_data)
        
        await interaction.followup.send(
            "✅ **Your IG-Name Registration has been submitted successfully!**\n"
            "An administrator or DC Moderator will review your submission soon.",
            ephemeral=True
        )
        
        guild = interaction.guild
        if not guild:
            return
            
        review_channel, _ = get_target_channels(guild, for_ign=True)
        if not review_channel:
            review_channel = interaction.channel
            
        review_embed = discord.Embed(
            title="📋 NEW IN-GAME NAME REGISTRATION",
            color=config.EMBED_COLOR_GOLD,
            description=f"**Registration ID:** `#{reg_id}`\n**Applicant:** {user.mention} (`{user.name}` | ID: `{user.id}`)"
        )
        review_embed.set_thumbnail(url=user.display_avatar.url)
        review_embed.add_field(name="🧑 OOC Name", value=reg_data["ooc_name"], inline=True)
        review_embed.add_field(name="🎮 In-Game (IG) Name", value=reg_data["ig_name"], inline=True)
        review_embed.add_field(name="🌐 Server Name", value=reg_data["server_name"], inline=True)
        review_embed.add_field(name="🎖️ Current Level / Rank", value=reg_data["current_level"], inline=True)
        review_embed.set_footer(text=f"ZEBLASKI OFFICIAL BOT • IGN Submission #{reg_id}")
        review_embed.timestamp = discord.utils.utcnow()
        
        review_view = IgnModeratorReviewView(reg_id=reg_id)
        msg = await review_channel.send(
            content=f"🔔 **Attention DC Moderators:** New In-Game Name registration from {user.mention}!",
            embed=review_embed,
            view=review_view
        )
        database.update_ign_registration_message(reg_id, msg.id, review_channel.id)


class IgnApplyView(discord.ui.View):
    """Persistent View for the IN-GAME-NAME REGISTER panel (Photo 1)."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="IG-NAME REGISTER",
        style=discord.ButtonStyle.danger,
        custom_id="zeblaski_ign_register_button"
    )
    async def ign_register_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IgnRegisterModal())


class IgnModeratorReviewView(discord.ui.View):
    """Persistent View for Accept / Reject on IGN submission review."""
    def __init__(self, reg_id: int):
        super().__init__(timeout=None)
        self.reg_id = reg_id
        
        accept_btn = discord.ui.Button(
            label="Accept",
            style=discord.ButtonStyle.success,
            emoji="✅",
            custom_id=f"zeblaski:ign_accept:{reg_id}"
        )
        accept_btn.callback = self.accept_callback
        self.add_item(accept_btn)
        
        reject_btn = discord.ui.Button(
            label="Reject",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            custom_id=f"zeblaski:ign_reject:{reg_id}"
        )
        reject_btn.callback = self.reject_callback
        self.add_item(reject_btn)

    async def check_permission(self, interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        member = interaction.guild.get_member(interaction.user.id)
        if not member or not is_moderator(member, interaction.guild.id):
            await interaction.response.send_message(
                "⛔ **Access Denied:** Only members with the **DC Moderator** role can accept or reject applications.",
                ephemeral=True
            )
            return False
        return True

    async def accept_callback(self, interaction: discord.Interaction):
        if not await self.check_permission(interaction):
            return
            
        await interaction.response.defer()
        reg_id = self.reg_id
        reg_data = database.get_ign_registration(reg_id)
        if not reg_data:
            await interaction.followup.send("⚠️ IGN Registration not found.", ephemeral=True)
            return
            
        if reg_data["status"] != "PENDING":
            await interaction.followup.send(f"⚠️ This registration has already been **{reg_data['status']}**.", ephemeral=True)
            return
            
        database.update_ign_registration_status(reg_id, "APPROVED", interaction.user.id, interaction.user.name)
        
        guild = interaction.guild
        applicant_id = reg_data["user_id"]
        applicant = guild.get_member(applicant_id) if guild else None
        if not applicant:
            try:
                applicant = await bot.fetch_user(applicant_id)
            except Exception:
                applicant = None

        if applicant:
            avatar_img = await ign_image_generator.fetch_user_avatar(applicant)
            curr_name = applicant.name
        else:
            avatar_img = await ign_image_generator.fetch_user_avatar(interaction.user)
            curr_name = reg_data["username"]

        # Reviewer name for REVIEWED BY tab
        reviewer_name = interaction.user.display_name if config.IGN_REVIEW_TAB_TEXT == "moderator" else curr_name

        # Generate Photo 3 Approved Card
        card_bytes = ign_image_generator.generate_ign_result_card(
            template_path=config.IGN_APPROVED_TEMPLATE_PATH,
            avatar_img=avatar_img,
            current_name=curr_name,
            registered_name=reg_data["ig_name"],
            level=reg_data["current_level"],
            reviewed_by=reviewer_name,
            is_approved=True
        )
        discord_file = discord.File(card_bytes, filename=f"ign_approved_{reg_data['ig_name']}.png")

        # Disable buttons on review message
        for item in self.children:
            item.disabled = True
            
        orig_embed = interaction.message.embeds[0] if interaction.message.embeds else discord.Embed()
        orig_embed.color = config.EMBED_COLOR_GREEN
        orig_embed.add_field(
            name="📌 Status",
            value=f"✅ **ACCEPTED** by {interaction.user.mention} (`{interaction.user.name}`)",
            inline=False
        )
        await interaction.message.edit(embed=orig_embed, view=self)

        # Post accepted card in results channel
        _, results_ch = get_target_channels(guild, for_ign=True)
        post_channel = results_ch or interaction.channel
        
        await post_channel.send(
            content=(
                f"🎉 **IN-GAME NAME REGISTERED!** <@{applicant_id}>'s IG Name (`{reg_data['ig_name']}`) "
                f"has been officially **APPROVED** by {interaction.user.mention}!"
            ),
            file=discord_file
        )

        # Optional: Attempt to set user server nickname to the registered IG Name
        if applicant and isinstance(applicant, discord.Member):
            try:
                await applicant.edit(nick=reg_data["ig_name"], reason="Zeblaski IGN Registration Approved")
            except Exception:
                pass  # Might not have permission if applicant is server owner or higher role

        # Send DM to applicant with card
        if applicant:
            try:
                dm_card_bytes = io.BytesIO(card_bytes.getvalue())
                dm_file = discord.File(dm_card_bytes, filename="zeblaski_ign_approved.png")
                await applicant.send(
                    content=(
                        f"👑 **IN-GAME NAME REGISTRATION APPROVED!**\n"
                        f"Your SA-MP In-Game Name has been registered as **`{reg_data['ig_name']}`** "
                        f"by {interaction.user.name}!\n"
                        f"Here is your official verification card:"
                    ),
                    file=dm_file
                )
            except Exception as e:
                print(f"Could not send DM to applicant: {e}")

        await interaction.followup.send(f"✅ In-Game Name Registration `#{reg_id}` accepted successfully!", ephemeral=True)

    async def reject_callback(self, interaction: discord.Interaction):
        if not await self.check_permission(interaction):
            return
            
        await interaction.response.defer()
        reg_id = self.reg_id
        reg_data = database.get_ign_registration(reg_id)
        if not reg_data:
            await interaction.followup.send("⚠️ IGN Registration not found.", ephemeral=True)
            return
            
        if reg_data["status"] != "PENDING":
            await interaction.followup.send(f"⚠️ This registration has already been **{reg_data['status']}**.", ephemeral=True)
            return
            
        database.update_ign_registration_status(reg_id, "REJECTED", interaction.user.id, interaction.user.name)
        
        guild = interaction.guild
        applicant_id = reg_data["user_id"]
        applicant = guild.get_member(applicant_id) if guild else None
        if not applicant:
            try:
                applicant = await bot.fetch_user(applicant_id)
            except Exception:
                applicant = None

        if applicant:
            avatar_img = await ign_image_generator.fetch_user_avatar(applicant)
            curr_name = applicant.name
        else:
            avatar_img = await ign_image_generator.fetch_user_avatar(interaction.user)
            curr_name = reg_data["username"]

        reviewer_name = interaction.user.display_name if config.IGN_REVIEW_TAB_TEXT == "moderator" else curr_name

        # Generate Photo 4 Declined Card (Registered Name set to NONE when declined)
        card_bytes = ign_image_generator.generate_ign_result_card(
            template_path=config.IGN_DECLINED_TEMPLATE_PATH,
            avatar_img=avatar_img,
            current_name=curr_name,
            registered_name="NONE",
            level=reg_data["current_level"],
            reviewed_by=reviewer_name,
            is_approved=False
        )
        discord_file = discord.File(card_bytes, filename=f"ign_declined_{reg_data['ig_name']}.png")

        for item in self.children:
            item.disabled = True
            
        orig_embed = interaction.message.embeds[0] if interaction.message.embeds else discord.Embed()
        orig_embed.color = config.EMBED_COLOR_RED
        orig_embed.add_field(
            name="📌 Status",
            value=f"❌ **REJECTED** by {interaction.user.mention} (`{interaction.user.name}`)",
            inline=False
        )
        await interaction.message.edit(embed=orig_embed, view=self)

        _, results_ch = get_target_channels(guild, for_ign=True)
        post_channel = results_ch or interaction.channel
        
        await post_channel.send(
            content=(
                f"⚠️ **IN-GAME NAME REGISTRATION DECLINED**: <@{applicant_id}>'s submission for "
                f"`{reg_data['ig_name']}` was **DECLINED** by {interaction.user.mention}."
            ),
            file=discord_file
        )

        if applicant:
            try:
                dm_card_bytes = io.BytesIO(card_bytes.getvalue())
                dm_file = discord.File(dm_card_bytes, filename="zeblaski_ign_declined.png")
                await applicant.send(
                    content=(
                        f"❌ Your In-Game Name registration (`{reg_data['ig_name']}`) was **DECLINED**.\n"
                        f"Please verify your details and resubmit if necessary."
                    ),
                    file=dm_file
                )
            except Exception as e:
                print(f"Could not send DM to applicant: {e}")

        await interaction.followup.send(f"❌ In-Game Name Registration `#{reg_id}` rejected.", ephemeral=True)


# -------------------------------------------------------------
# BOT EVENTS & SETUP
# -------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"  ZEBLASKI OFFICIAL BOT is Online and Ready!")
    print(f"  Logged in as: {bot.user} (ID: {bot.user.id})")
    print(f"  Connected to {len(bot.guilds)} guilds")
    print(f"==================================================")
    
    # 1. Register persistent view for Gang Recruitment
    bot.add_view(ApplyView())
    pending_apps = database.get_pending_applications()
    for app in pending_apps:
        bot.add_view(ModeratorReviewView(app["id"]))
    print(f"  Restored {len(pending_apps)} pending recruitment reviews.")
    
    # 2. Register persistent view for IGN Register
    bot.add_view(IgnApplyView())
    pending_igns = database.get_pending_ign_registrations()
    for ign in pending_igns:
        bot.add_view(IgnModeratorReviewView(ign["id"]))
    print(f"  Restored {len(pending_igns)} pending IGN reviews.")
    
    # 3. Sync Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"  Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"  Error syncing slash commands: {e}")


# =============================================================
# SLASH & PREFIX COMMANDS: GANG RECRUITMENT
# =============================================================

@bot.tree.command(name="setup_panel", description="Post the official Zeblaski Gang recruitment panel (Photo 1 format).")
@app_commands.checks.has_permissions(administrator=True)
async def setup_panel_slash(interaction: discord.Interaction):
    if not os.path.exists(config.BANNER_PATH):
        await interaction.response.send_message("❌ Error: `gang_banner.png` missing in assets.", ephemeral=True)
        return
        
    embed = build_recruitment_embed()
    banner_file = discord.File(config.BANNER_PATH, filename="banner.png")
    view = ApplyView()
    
    await interaction.channel.send(file=banner_file, embed=embed, view=view)
    await interaction.response.send_message("✅ Zeblaski Gang Recruitment panel has been posted successfully!", ephemeral=True)


@bot.command(name="setuppanel")
@commands.has_permissions(administrator=True)
async def setup_panel_prefix(ctx: commands.Context):
    if not os.path.exists(config.BANNER_PATH):
        await ctx.send("❌ Error: `gang_banner.png` missing in assets.")
        return
        
    embed = build_recruitment_embed()
    banner_file = discord.File(config.BANNER_PATH, filename="banner.png")
    view = ApplyView()
    
    await ctx.send(file=banner_file, embed=embed, view=view)
    await ctx.message.delete()


# =============================================================
# NEW COMMANDS: IN-GAME-NAME (IGN) REGISTER
# =============================================================

@bot.tree.command(name="setup_ign_panel", description="Post the official IN-GAME-NAME REGISTER panel (Photo 1 format).")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ign_panel_slash(interaction: discord.Interaction):
    """Post the exact Photo 1 format panel for In-Game Name Register."""
    embed = build_ign_embed()
    view = IgnApplyView()
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ In-Game Name Register panel has been posted successfully!", ephemeral=True)


@bot.command(name="setupign")
@commands.has_permissions(administrator=True)
async def setup_ign_panel_prefix(ctx: commands.Context):
    """Prefix version: !setupign"""
    embed = build_ign_embed()
    view = IgnApplyView()
    
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()


@bot.tree.command(name="set_ign_review_channel", description="Set the channel where IGN registrations are sent for review.")
@app_commands.checks.has_permissions(administrator=True)
async def set_ign_review_channel_slash(interaction: discord.Interaction, channel: discord.TextChannel):
    database.update_guild_setting(interaction.guild.id, "ign_review_channel_id", channel.id)
    await interaction.response.send_message(f"✅ IGN Review channel set to: {channel.mention}", ephemeral=True)


@bot.command(name="setignreviewchannel")
@commands.has_permissions(administrator=True)
async def set_ign_review_channel_prefix(ctx: commands.Context, channel: discord.TextChannel):
    database.update_guild_setting(ctx.guild.id, "ign_review_channel_id", channel.id)
    await ctx.send(f"✅ IGN Review channel set to: {channel.mention}")


@bot.tree.command(name="set_ign_results_channel", description="Set the channel where approved/declined IGN cards are posted.")
@app_commands.checks.has_permissions(administrator=True)
async def set_ign_results_channel_slash(interaction: discord.Interaction, channel: discord.TextChannel):
    database.update_guild_setting(interaction.guild.id, "ign_results_channel_id", channel.id)
    await interaction.response.send_message(f"✅ IGN Results channel set to: {channel.mention}", ephemeral=True)


@bot.command(name="setignresultschannel")
@commands.has_permissions(administrator=True)
async def set_ign_results_channel_prefix(ctx: commands.Context, channel: discord.TextChannel):
    database.update_guild_setting(ctx.guild.id, "ign_results_channel_id", channel.id)
    await ctx.send(f"✅ IGN Results channel set to: {channel.mention}")


@bot.tree.command(name="test_ign_card", description="Test generating an Approved (Photo 3) or Declined (Photo 4) IGN card.")
@app_commands.checks.has_permissions(administrator=True)
async def test_ign_card_slash(interaction: discord.Interaction, user: discord.User, ig_name: str, level: str, approved: bool):
    await interaction.response.defer(ephemeral=True)
    template = config.IGN_APPROVED_TEMPLATE_PATH if approved else config.IGN_DECLINED_TEMPLATE_PATH
    avatar_img = await ign_image_generator.fetch_user_avatar(user)
    
    reg_name_display = ig_name if approved else "NONE"
    card_bytes = ign_image_generator.generate_ign_result_card(
        template_path=template,
        avatar_img=avatar_img,
        current_name=user.name,
        registered_name=reg_name_display,
        level=level,
        reviewed_by=interaction.user.display_name,
        is_approved=approved
    )
    status_label = "Approved (Photo 3)" if approved else "Declined (Photo 4)"
    card_file = discord.File(card_bytes, filename="test_ign_card.png")
    await interaction.followup.send(f"🖼️ Generated test IGN {status_label} card for {user.mention}:", file=card_file, ephemeral=True)


# =============================================================
# GENERAL CONFIGURATION & HELP COMMANDS
# =============================================================

@bot.tree.command(name="set_moderator_role", description="Set the DC Moderator role allowed to accept/reject applications.")
@app_commands.checks.has_permissions(administrator=True)
async def set_moderator_role_slash(interaction: discord.Interaction, role: discord.Role):
    database.update_guild_setting(interaction.guild.id, "mod_role_id", role.id)
    await interaction.response.send_message(f"✅ DC Moderator role set to: {role.mention}", ephemeral=True)


@bot.command(name="setmodrole")
@commands.has_permissions(administrator=True)
async def set_moderator_role_prefix(ctx: commands.Context, role: discord.Role):
    database.update_guild_setting(ctx.guild.id, "mod_role_id", role.id)
    await ctx.send(f"✅ DC Moderator role set to: {role.mention}")


@bot.tree.command(name="set_review_channel", description="Set the default channel where moderator receives submissions.")
@app_commands.checks.has_permissions(administrator=True)
async def set_review_channel_slash(interaction: discord.Interaction, channel: discord.TextChannel):
    database.update_guild_setting(interaction.guild.id, "review_channel_id", channel.id)
    await interaction.response.send_message(f"✅ Default applications review channel set to: {channel.mention}", ephemeral=True)


@bot.command(name="setreviewchannel")
@commands.has_permissions(administrator=True)
async def set_review_channel_prefix(ctx: commands.Context, channel: discord.TextChannel):
    database.update_guild_setting(ctx.guild.id, "review_channel_id", channel.id)
    await ctx.send(f"✅ Default applications review channel set to: {channel.mention}")


@bot.tree.command(name="set_results_channel", description="Set the default channel where accepted/declined cards are announced.")
@app_commands.checks.has_permissions(administrator=True)
async def set_results_channel_slash(interaction: discord.Interaction, channel: discord.TextChannel):
    database.update_guild_setting(interaction.guild.id, "results_channel_id", channel.id)
    await interaction.response.send_message(f"✅ Default acceptance/rejection results channel set to: {channel.mention}", ephemeral=True)


@bot.command(name="setresultschannel")
@commands.has_permissions(administrator=True)
async def set_results_channel_prefix(ctx: commands.Context, channel: discord.TextChannel):
    database.update_guild_setting(ctx.guild.id, "results_channel_id", channel.id)
    await ctx.send(f"✅ Default acceptance/rejection results channel set to: {channel.mention}")


@bot.tree.command(name="set_member_role", description="Set the role given to applicants when accepted.")
@app_commands.checks.has_permissions(administrator=True)
async def set_member_role_slash(interaction: discord.Interaction, role: discord.Role):
    database.update_guild_setting(interaction.guild.id, "member_role_id", role.id)
    await interaction.response.send_message(f"✅ Accepted Member role set to: {role.mention}", ephemeral=True)


@bot.command(name="setmemberrole")
@commands.has_permissions(administrator=True)
async def set_member_role_prefix(ctx: commands.Context, role: discord.Role):
    database.update_guild_setting(ctx.guild.id, "member_role_id", role.id)
    await ctx.send(f"✅ Accepted Member role set to: {role.mention}")


@bot.tree.command(name="help_zeblaski", description="Show instructions and setup guide for Zeblaski Official Bot.")
async def help_slash(interaction: discord.Interaction):
    help_embed = discord.Embed(
        title="👑 ZEBLASKI OFFICIAL BOT - COMMANDS & SETUP",
        color=config.EMBED_COLOR_BLUE,
        description="Official bot featuring Gang Recruitment and In-Game Name (IGN) Registration systems."
    )
    help_embed.add_field(
        name="🎮 IN-GAME NAME (IGN) REGISTER SYSTEM",
        value=(
            "• `/setup_ign_panel` or `!setupign`: Post the IGN register panel (Photo 1 format).\n"
            "• `/set_ign_review_channel <#channel>`: Set IGN review channel.\n"
            "• `/set_ign_results_channel <#channel>`: Set IGN announcement results channel.\n"
            "• `/test_ign_card`: Preview Photo 3 (Approved) or Photo 4 (Declined) IGN cards."
        ),
        inline=False
    )
    help_embed.add_field(
        name="👑 GANG RECRUITMENT SYSTEM",
        value=(
            "• `/setup_panel` or `!setuppanel`: Post gang recruitment panel with banner.\n"
            "• `/set_member_role <@role>`: Role granted on recruitment acceptance."
        ),
        inline=False
    )
    help_embed.add_field(
        name="⚙️ GENERAL MODERATION SETTINGS",
        value=(
            "• `/set_moderator_role <@role>`: DC Moderator role allowed to review.\n"
            "• `/set_review_channel <#channel>`: Default review channel.\n"
            "• `/set_results_channel <#channel>`: Default results channel."
        ),
        inline=False
    )
    await interaction.response.send_message(embed=help_embed, ephemeral=True)


# -------------------------------------------------------------
# MAIN ENTRYPOINT
# -------------------------------------------------------------

def main():
    token = config.DISCORD_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "="*70)
        print(" [!] DISCORD BOT TOKEN MISSING!")
        print(" Please add your bot token in the .env file:")
        print(" DISCORD_TOKEN=your_token_here")
        print("="*70 + "\n")
        return
        
    bot.run(token)

if __name__ == "__main__":
    main()

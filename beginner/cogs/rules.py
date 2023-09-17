from beginner.cog import Cog, commands
from beginner.colors import *
from datetime import datetime
from nextcord import Embed
import re
import nextcord.utils
import pytz


class RulesCog(Cog):
    def __init__(self, client: nextcord.Client):
        super().__init__(client)
        self.message_fields = {
            "Direct Messages": {
                "description": (
                    "Please keep discussion on the server. It helps you get responses more quickly from more people & "
                    "with more viewpoints. It also helps protect you from scammers. \n\n*We recommend disabling DM's "
                    "from all public servers.*"
                ),
                "labels": ("dm", "dming", "pm"),
            },
            "Promotion": {
                "description": (
                    "We're not a job board & do not allow the exchange of money. We also ask that you keep self-"
                    "promotion to a minimum.\n\n*If you have something you think we'd like to promote talk to the "
                    "mods.*"
                ),
                "labels": (
                    "solicitation",
                    "soliciting",
                    "advert",
                    "advertising",
                    "ads",
                    "ad",
                    "jobs",
                    "job",
                    "promotion",
                    "promoting",
                    "ads",
                    "self-promotion",
                    "self promotion",
                ),
            },
            "Laws & TOS's": {
                "description": (
                    "Discussion of anything that breaks the law or violates a TOS is not allowed. This includes account"
                    " creation bots, scam bots, purchase automation bots, DDoS, RATs, etc."
                ),
                "labels": ("tos", "hacker", "illegal", "hack", "hacking"),
            },
            "Acceptable Behavior": {
                "description": (
                    "Our members have an incredible diversity of opinions, experiences, & skill levels. Be kind & "
                    "understanding. Your opinions aren’t more important than anyone else’s. Hold your opinions weakly, "
                    "you’ll learn more.\n\nWe do not tolerate *harassment, NSFW content, flaming, trolling, & bigotry*."
                    " This includes derogatory remarks towards or statements objectifying anyone."
                ),
                "labels": (
                    "understanding",
                    "respectful",
                    "helpful",
                    "helping",
                    "learning",
                    "nsfw",
                    "trolling",
                    "harassment",
                    "bigotry",
                    "harassing",
                    "racism",
                    "derogatory",
                    "objectification",
                ),
            },
            "Academic Honesty": {
                "description": (
                    "You may ask for help with homework but asking others to help on tests/quizzes or to do your "
                    "coursework for you is not allowed."
                ),
                "labels": (
                    "academics",
                    "honesty",
                    "homework",
                    "quizzes",
                    "tests",
                    "school",
                    "cheating",
                    "dishonest",
                ),
            },
            "Getting Help": {
                "description": (
                    "To keep the server organized, please keep coding questions out of discussion channels. Do not spam"
                    " multiple channels with your questions, & do not direct people to your help channel."
                ),
                "labels": ("help", "spam", "questions", "confusion"),
            },
            "Display Names & PFPs": {
                "description": (
                    "Your display name should be readable, not promotional, & should not violate the other rules. Your "
                    "PFP should be reasonably appropriate."
                ),
                "labels": ("nickname", "avatar", "name", "pfp", "username"),
            },
            "Use English": {
                "description": (
                    "To ensure everyone can participate & that the server staff can foster an environment amenable "
                    "to growth and learning, please only use __English__. If you cannot reasonably communicate in "
                    "English you may be removed from the server."
                ),
                "labels": ("english",),
            },
        }

    @Cog.command(name="update-rules")
    @commands.has_guild_permissions(manage_channels=True)
    async def update_rules_message(self, ctx, *, reason: str):
        rules: nextcord.TextChannel = nextcord.utils.get(
            self.server.channels, name="👮rules"
        )
        messages = await rules.history(limit=1, oldest_first=True).flatten()
        if messages:
            rules_content = []
            for title, rule_metadata in sorted(self.message_fields.items()):
                rules_content.append(f"## {title}")
                rules_content.append(rule_metadata["description"])

            await messages[0].edit(
                content="\n".join(
                    [
                        "# Rules & Conduct\n",
                        "Welcome!!! Please give these rules & guidelines a quick read.",
                        *rules_content,
                    ]
                ),
                allowed_mentions=nextcord.AllowedMentions(
                    everyone=False, users=False, roles=False
                ),
            )
            await rules.send(
                f"Rules message has been updated: {reason}", delete_after=60
            )

    def build_rule_message_embed(self, title: str, message: str) -> nextcord.Embed:
        admin: nextcord.Member = self.server.get_member(266432511897370625)
        embed = Embed(
            title=title,
            description=message,
            timestamp=datetime.now().astimezone(pytz.timezone("US/Eastern")),
            color=BLUE,
        )
        embed.set_footer(text=admin.name, icon_url=admin.avatar.url)

        for field_title, field_content in self.message_fields.items():
            embed.add_field(
                name=field_title, value=field_content["description"], inline=False
            )

        return embed

    @Cog.command(name="rule")
    async def show_rule(self, ctx, *, label=None):
        rule = self.get_rule(label, fuzzy=True)
        if rule:
            await ctx.send(embed=self.build_rule_embed(rule))
        else:
            rules = self.get_rules(label, force=True)
            rule_primary_labels = [
                "**" + self.message_fields[rule]["labels"][0] + "**" for rule in rules
            ]
            await ctx.send(
                embed=Embed(
                    title=(
                        f"Didn't find a rule for '{label}'"
                        if label
                        else "Beginner.py Rules"
                    ),
                    description=f"Here are some rules you might try:\n{', '.join(rule_primary_labels)}"
                    if label
                    else f"Here are all the rules: \n{', '.join(sorted(rule_primary_labels))}",
                    color=0x306998,
                ).set_thumbnail(url=ctx.guild.icon.url)
            )

    @Cog.command(name="formatting", aliases=("format", "code"))
    async def show_formatting_rule(self, ctx, raw_language: str = "py", *, _=None):
        language = "".join(re.findall(r"[a-z0-9]+", raw_language, re.I))
        await ctx.send(
            embed=(
                Embed(
                    title="Code Formatting",
                    description=(
                        "When sharing code with the community, please use the correct formatting for ease of "
                        "readability."
                    ),
                    color=BLUE,
                )
                .add_field(
                    name="Example",
                    value=(
                        f"\\`\\`\\`{language}\n"
                        f"YOUR CODE HERE\n"
                        f"\\`\\`\\`\n\n"
                        f"*Those are back ticks not single quotes, typically the key above `TAB`*"
                    ),
                    inline=False,
                )
                .set_thumbnail(url=ctx.guild.icon.url)
            )
        )

    def build_rule_embed(self, rule):
        return Embed(
            title=rule,
            description=self.message_fields[rule]["description"],
            color=0x306998,
        ).set_thumbnail(url=self.server.icon.url)

    def get_rule(self, label, fuzzy=False):
        for rule_name, rule_info in self.message_fields.items():
            if label.casefold() in rule_info["labels"]:
                rule = rule_name
                break
        else:
            rule = None
        if not rule and fuzzy:
            rules = self.get_rules(label)
            if len(rules) == 1:
                rule = rules[0]
        return rule

    def get_rules(self, label=None, force=True):
        if label:
            rules = [
                rule_name
                for rule_name in self.message_fields
                if label in "".join(rule_name)
            ]
        else:
            rules = self.message_fields
        return rules if rules or not force else self.get_rules(force=False)


def setup(client):
    client.add_cog(RulesCog(client))

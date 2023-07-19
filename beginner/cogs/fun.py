from beginner.cog import Cog
import aiohttp
import nextcord
import nextcord.ext.commands
import ast
import math
import re
import random
import socket
from datetime import datetime, timedelta
import pendulum


def async_cache(coroutine):
    cache = {}

    async def run(*args):
        if args not in cache:
            cache[args] = await coroutine(*args)

        return cache[args]

    return run


def url_normalization(coroutine):
    async def normalize(obj, url):
        return await coroutine(obj, normalize_url(url))

    return normalize


def normalize_url(url: str) -> str:
    uri_pattern = re.compile(r"(?:https?://)?(?:www\.)?(.+)")
    normalized_url = uri_pattern.search(url).group(1)
    return normalized_url


class Fun(Cog):
    def __init__(self, client):
        super().__init__(client)
        self._rickroll_rate_limits = {}

        # Rickroll links that the bot cannot detect
        rr_blocklist = [
            "https://www.tenor.com/view/spoiler-gif-24641133",
        ]

        self.rickroll_blocklist = {normalize_url(url) for url in rr_blocklist}

    @Cog.command()
    async def stack(self, ctx, v: str = "", *, instructions):
        class InvalidInstruction(Exception):
            ...

        stack = [0]
        operations = instructions.split()
        try:
            output = []
            for operation in operations:
                if operation.isdigit():
                    output.append(f"Push {operation}")
                    stack.append(int(operation))
                elif operation == "+":
                    a, b = stack.pop(), stack.pop()
                    stack.append(a + b)
                    output.append(f"Pop {a}, Pop {b}, Add, Push {stack[-1]}")
                elif operation == "-":
                    a, b = stack.pop(), stack.pop()
                    stack.append(a - b)
                    output.append(f"Pop {a}, Pop {b}, Subtract, Push {stack[-1]}")
                elif operation == "*":
                    a, b = stack.pop(), stack.pop()
                    stack.append(a * b)
                    output.append(f"Pop {a}, Pop {b}, Multiply, Push {stack[-1]}")
                elif operation == "/":
                    a, b = stack.pop(), stack.pop()
                    stack.append(a // b)
                    output.append(f"Pop {a}, Pop {b}, Divide, Push {stack[-1]}")
                elif operation == "DUP":
                    stack.append(stack[-1])
                    output.append(
                        f"Pop {stack[-1]}, Push {stack[-1]}, Push {stack[-1]}"
                    )
                elif operation == "POP":
                    output.append(f"Pop {stack.pop()}")
                else:
                    raise InvalidInstruction(operation)
            message = f"Final value: {stack.pop()}"
            if v == "-v":
                o = "\n".join(output)
                message = f"```\n{o}\n```{message}"
        except InvalidInstruction as e:
            message = f"Invalid Instruction: {e.args[0]}"
        except IndexError:
            message = f"IndexError: current stack = {stack}"
        except ZeroDivisionError:
            message = f"Division by zero: current stack = {stack}"

        await ctx.send(message)

    @Cog.command()
    async def remove_extras(self, ctx, count: int, *, raw_literals):
        try:
            literals = ast.literal_eval(raw_literals)
        except (SyntaxError, ValueError):
            await ctx.send("You must provide a sequence of literals")
            return

        result = [
            item
            for index, item in enumerate(literals)
            if literals[:index].count(item) < count
        ]
        await ctx.send(f"Result: {result}")

    @Cog.command()
    async def directionally_challenged(self, ctx, *, raw_directions: str):
        try:
            directions = ast.literal_eval(raw_directions)
        except (SyntaxError, ValueError):
            await ctx.send("You must provide a sequence of strings")
            return

        walked = len(directions)
        shortest = abs(directions.count("N") - directions.count("S")) + abs(
            directions.count("E") - directions.count("W")
        )
        await ctx.send(
            f"Your path had a length of `{walked}`\n"
            f"The shortest path had a length of `{shortest}`\n"
            f"The answer was that they have a difference of `{walked - shortest}`"
        )

    @Cog.command(
        aliases=[
            "mystery_func",
            "mystery_fun",
            "mysteryfunction",
            "mysteryfunc",
            "mysteryfun",
        ]
    )
    async def mystery_function(self, ctx, *, number: str):
        if not number.isdigit():
            await ctx.send("You must provide a positive integer")
            return

        result = math.prod(map(int, str(number)))
        await ctx.send(f"```py\n>>> mystery_function({number})\n{result}```")

    @Cog.command(aliases=["minipeaks", "peaks"])
    async def mini_peaks(self, ctx, *, raw_numbers: str):
        try:
            numbers = ast.literal_eval(raw_numbers)
        except (SyntaxError, ValueError):
            numbers = None

        if not hasattr(numbers, "__iter__") or any(
            not isinstance(item, (int, float)) for item in numbers
        ):
            await ctx.send("You must provide a sequence of integers")
            return

        result = [
            y
            for x, y, z in zip(numbers[:-2], numbers[1:-1], numbers[2:])
            if y > x and y > z
        ]
        await ctx.send(f"```py\n>>> mini_peaks({raw_numbers})\n{result}```")

    @Cog.command(aliases=["compass", "directions", "compassdirections"])
    async def compass_directions(self, ctx, raw_facing: str, *, raw_directions: str):
        try:
            facing = ast.literal_eval(raw_facing)
            assert isinstance(facing, str)
            directions = ast.literal_eval(raw_directions)
            assert hasattr(directions, "__iter__") and list(
                filter(lambda item: isinstance(item, str), directions)
            )
        except (AssertionError, SyntaxError, ValueError):
            await ctx.send(
                "Facing must be a string, directions must be a sequence of strings"
            )
            return

        cardinals = {"N": 0, "E": 1, "S": 2, "W": 3}
        direction = cardinals[facing]
        direction -= directions.count("L")
        direction += directions.count("R")
        result = {item: key for key, item in cardinals.items()}[direction % 4]
        await ctx.send(
            f"```py\n>>> final_direction({raw_facing}, {raw_directions})\n{result}```"
        )

    @Cog.command(aliases=["intersection", "union", "intersectionunion"])
    async def intersection_union(self, ctx, *, code: str):
        def intersection_union(list_a, list_b):
            intersection = list({item for item in list_a if item in list_b})
            intersection.sort()
            union = list(set(list_a) | set(list_b))
            union.sort()
            return intersection, union

        try:
            lists = re.findall(r"(\[[0-9,\s]+\])", code)
            print(lists)
            list_a = ast.literal_eval(lists[0])
            list_b = ast.literal_eval(lists[1])
        except (SyntaxError, ValueError) as e:
            await ctx.send(f"There was an exception: {e.__name__}")
        else:
            result = intersection_union(list_a, list_b)
            await ctx.send(
                f"```py\n>>> intersection_union({str(list_a)}, {str(list_b)})\n{result}```"
            )

    @Cog.command(aliases=["countoverlapping", "overlapping"])
    async def count_overlapping(self, ctx, *, code: str):
        def count_overlapping(intervals, point):
            return len([a for a, b in intervals if a <= point <= b])

        try:
            data = re.findall(r"(\[[0-9,\s\[\]]+\]|\d+)", code)
            intervals = ast.literal_eval(data[0])
            point = ast.literal_eval(data[1])
        except (SyntaxError, ValueError) as e:
            await ctx.send(f"There was an exception: {e.__name__}")
        else:
            result = count_overlapping(intervals, point)
            await ctx.send(
                f"```py\n>>> count_overlapping({intervals}, {point})\n{result}```"
            )

    @Cog.command(aliases=["rearranged"])
    async def rearranged_difference(self, ctx, number: int):
        result = int("".join(reversed(sorted(str(number))))) - int(
            "".join(sorted(str(number)))
        )
        await ctx.send(f"```py\n>>> rearranged_difference({number})\n{result}```")

    @Cog.command(
        aliases=[
            "left",
            "leftdigit",
            "leftmost",
            "left_most",
            "leftmost_digit",
            "left_most_digit",
            "leftmostdigit",
        ]
    )
    async def left_digit(self, ctx, input_string: str):
        def left_digit(string: str):
            for c in string:
                if c.isdigit():
                    return int(c)
            return None

        result = left_digit(input_string)
        await ctx.send(f'```py\n>>> left_digit("{input_string}")\n{result}```')

    @Cog.command(aliases=["correctinequality", "inequality"])
    async def correct_inequality(self, ctx, *, expression: str):
        def correct_inequality(expression: str):
            tokens = expression.split(" ")
            steps = []

            if len(tokens) < 3 or (len(tokens) - 3) % 2 != 0:
                steps.append("INVALID INPUT")
                return steps

            valid = True
            for index in range(0, len(tokens) - 2, 2):
                a, op, b = tokens[index : index + 3]
                steps.append(f"{a} {op} {b}")
                if op not in {">", "<"} or not a.isdigit() or not b.isdigit():
                    steps[-1] += " - INVALID"
                    valid = False
                    break
                elif op == "<" and int(a) >= int(b):
                    steps[-1] += " - False"
                    valid = False
                    break
                elif op == ">" and int(a) <= int(b):
                    steps[-1] += " - False"
                    valid = False
                    break
                else:
                    steps[-1] += " - True"

            steps.append("VALID EXPRESSION" if valid else "INVALID EXPRESSION")
            return steps

        result = "\n".join(correct_inequality(expression))
        await ctx.send(f"`{expression}`\n```py\n{result}\n```")

    @Cog.command()
    async def dgo(self, ctx):
        await ctx.send(
            embed=nextcord.Embed().set_image(
                url="https://media1.tenor.com/images/f688c77103e32fdd6a9599713b546435/tenor.gif?itemid=7666830"
            )
        )

    @Cog.command()
    async def dns(self, ctx, domain_name: str):
        try:
            ip = socket.gethostbyname(domain_name)
        except socket.gaierror:
            message = f"Could not find the domain {domain_name}"
        else:
            message = f"The IP address for {domain_name} is {ip}"
        await ctx.send(message)

    @Cog.command()
    async def raw(self, ctx: nextcord.ext.commands.Context):
        message: nextcord.Message = ctx.message
        await ctx.send(
            f"```\n{message.content!r}\n```",
            allowed_mentions=nextcord.AllowedMentions(
                everyone=False, users=False, roles=False
            ),
        )

    @Cog.command(aliases=["ducci"])
    async def ducci_sequence(self, ctx, *, content):
        try:
            sequence = ast.literal_eval(content)
        except Exception:
            await ctx.send("There was an error")
            return

        h = [sequence]
        exited = False
        while h.count(h[-1]) == 1 and not all(i == 0 for i in h[-1]):
            h.append(tuple(abs(a - b) for a, b in zip(h[-1], [*h[-1][1:], h[-1][0]])))

            if len(h) == 100:
                exited = True
                break

        sequences = "\n".join(
            f"{str(index) + '.':4} {sequence!r}"
            for index, sequence in enumerate(h, start=1)
        )
        message = f"```py\n{sequences}\n```\n{'Finished in' if not exited else 'Exited after'} {len(h)} steps"
        await ctx.send(message)

    @Cog.command(aliases=["isrickroll", "isrr"])
    async def is_rick_roll(self, ctx, url):
        if (self._is_rickroll_rate_limited(ctx.author.id, 1)) or (
            self._is_rickroll_rate_limited(ctx.message.id, 3)
        ):
            wait_message = await ctx.send(
                "Please wait before calling this command again.", reference=ctx.message
            )
            await wait_message.delete(delay=2)
            return

        response = "Couldn't load url 💥"
        try:
            rr = await self._is_url_rickroll(url)
        except Exception as e:
            self.logger.exception("Failed to check a URL for Rickrolls")
        else:
            response = "It's a Rickroll 👎" if rr else "It's not a Rickroll 👍"
        finally:
            await ctx.send(response, reference=ctx.message)

    @Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.emoji.name != "❓":
            return

        channel: nextcord.TextChannel = self.server.get_channel(reaction.channel_id)
        message: nextcord.Message = await channel.fetch_message(reaction.message_id)

        urls = re.findall(
            r"(?:(?:https?|ftp)://)?[\w/\-?=%.]+\.[\w/\-&?=%.]+", message.content
        )

        if not urls:
            await self._send_temp_error_message(channel, "No URLs found!", message)
            return
        elif len(urls) > 5:
            await self._send_temp_error_message(
                channel, "Exceeded maximum number of URLs!", message
            )
            return

        if (self._is_rickroll_rate_limited(reaction.user_id, 1)) or (
            self._is_rickroll_rate_limited(reaction.message_id, 3)
        ):
            await message.remove_reaction(reaction.emoji, reaction.member)
            return

        failed = 0
        for url in urls:
            try:
                rr = await self._is_url_rickroll(url)
            except Exception as e:
                self.logger.exception("Failed to check a URL for Rickrolls")
                failed += 1
            else:
                if rr:
                    response = f"This is a Rickroll 👎: <{url}>"
                    break
        else:
            response = (
                "No Rickrolls found 👍"
                if failed < len(urls)
                else f"Couldn't load url{'s' if len(urls) > 1 else ''} 💥"
            )

        await channel.send(response, reference=message)

    async def _send_temp_error_message(
        self, channel: nextcord.TextChannel, error_msg: str, ref_msg: nextcord.Message
    ):
        error_message = await channel.send(error_msg, reference=ref_msg)
        await error_message.delete(delay=2)

    def _is_rickroll_rate_limited(self, limiter: str, time: int) -> bool:
        now = datetime.utcnow()
        delta = now - self._rickroll_rate_limits.get(limiter, now)
        if timedelta(seconds=0) < delta < timedelta(minutes=time):
            return True

        self._rickroll_rate_limits[limiter] = now
        return False

    @async_cache
    @url_normalization
    async def _is_url_rickroll(self, url: str) -> bool:
        if url in self.rickroll_blocklist:
            return True

        url = "http://" + url

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                return self._does_content_contain_rickroll(content.decode())

    def _does_content_contain_rickroll(self, content: str) -> bool:
        phrases = [
            "rickroll",
            "rick roll",
            "rick astley",
            "never gonna give you up",
        ]
        return bool(re.findall("|".join(phrases), content.lower(), re.MULTILINE))

    @Cog.command(name="cht.sh")
    async def chtsh(self, ctx, language: str, topic: str | None = None):
        language = language.lstrip("/")
        url = f"https://cht.sh/{language}"
        title = f"Cheat Sheet: {language.title()}"
        if topic:
            url += f"/{topic}"
            title += f" - {topic.title()}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url + "?qT") as response:
                content = (await response.read()).decode()

        await ctx.message.reply(
            embeds=[
                nextcord.Embed(
                    color=0x4477DD,
                    title=title,
                    description="\n".join(
                        (
                            "```",
                            content if len(content) <= 992 else content[:989] + "...",
                            "```",
                        )
                    ),
                    url=url,
                ).set_footer(text=url)
            ]
        )

    @Cog.command()
    async def reveal(self, ctx):
        if not ctx.message.reference:
            await ctx.send("🛑 You must reply to a message.")
            return

        message = ctx.message.reference.resolved
        if not message or not message.content.strip():
            await message.reply.send("*Empty Message*")
            return

        await message.reply(
            "> "
            + (
                "\n> ".join(
                    message.content.replace("\\", "\\\\")
                    .replace("<", r"\<")
                    .replace("> ", r"\> ")
                    .replace("*", r"\*")
                    .replace("_", r"\_")
                    .replace("`", r"\`")
                    .replace("|", r"\|")
                    .split("\n")
                )
            ),
            allowed_mentions=nextcord.AllowedMentions(
                everyone=False, users=False, roles=False, replied_user=True
            ),
        )

    @Cog.command()
    async def bruh(self, ctx, num: int = -1):
        n = min(num, 100) if num > 0 else random.randint(5, 100)
        await ctx.send(f"Br{'u' * n}h")

    @Cog.command(name="gpt-talk")
    async def gpt_talk(self, ctx, *, content):
        embed_to_edit = await ctx.message.reply(
            embed=nextcord.Embed(
                title="Getting response from gpt-j-6b...",
                description="It might take up to one minute if your sentence is short\n[Learn more about gpt-j-6b here](https://gpt3demo.com/apps/gpt-j-6b)",
                colour=0x6C8EB4,
            ),
            mention_author=False,
        )
        temperature = round(random.randint(50000, 100000) / 100000, 3)
        top_p = round(random.randint(50000, 100000) / 100000, 3)
        async with ctx.channel.typing():
            payload = {
                "context": content.casefold(),
                "token_max_length": 512,
                "temperature": temperature,
                "top_p": top_p,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://api.vicgalle.net:5000/generate", params=payload
                ) as response:
                    json_response = await response.json()

        text = json_response.get("text")
        embed = embed_to_edit.embeds[0]

        embed.set_footer(text=f"Settings: temperature={temperature}, top_p={top_p}")
        if text:
            embed.add_field(name="Context Given to GPT-J-6b", value=content)
            embed.add_field(name="GPT-J-6b's Response", value=text[:1000], inline=False)
            if len(text) > 1000:
                embed.add_field(name="[Continued]", value=text[1000:2000], inline=False)

        else:
            embed.add_field(
                name="GPT-J-6b Had an Issue",
                value="Not enough context to auto complete",
            )

        await embed_to_edit.edit(embed=embed)

    @Cog.command(name="make-time-tag")
    async def make_time_tag(self, ctx, time: str):
        time = time.upper()
        if time.index(":") <= 2:
            time = f"0{time}"

        if not time.endswith("M"):
            time += "PM"

        time = datetime.strptime(time, "%I:%M%p")
        dt = datetime.now().replace(
            hour=time.hour,
            minute=time.minute,
            second=0,
            microsecond=0,
            tzinfo=pendulum.timezone("America/New_York"),
        )
        utc = dt.astimezone(pendulum.timezone("UTC"))
        await ctx.message.reply(
            f"<t:{int(utc.timestamp())}:t>\n```\n<t:{int(utc.timestamp())}:t>\n```"
        )

    @Cog.listener("on_message")
    async def delete_see_sharp_jokes(self, message):
        if message.author.bot:
            return

        matches = re.search(
            r"(c+[a@4]+n+'*[t7]+|c+[a@4]+n+[o0]+[t7]+)\s*([s$]+[e3]+\s*[s$]+h+[a@4]+r*p+|c+\s*[s$]+h+[a@4]+r+p+|c+\s*#+)",
            message.content.casefold(),
        )
        if matches:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} please refrain from making C# jokes.",
                delete_after=10,
            )


def setup(client):
    client.add_cog(Fun(client))

import discord
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from discord.ext import commands
from selenium import webdriver

# Selenium setup
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("log-level=3")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

# Bot as discord.Client() class object
tab_bot = discord.Client()
tab_bot = commands.Bot(command_prefix=".")

# Startup
@tab_bot.event
async def on_ready():
    print("Logged as {0.user}".format(tab_bot))


# On command
@tab_bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
# Search for requested tabulature on Songsterr
async def tab(ctx, *, arg):

    search = "songsterr.com " + arg
    driver.get("https://google.com")

    try:
        driver.find_element_by_id("L2AGLb").click()
    except:
        pass

    driver.find_element_by_name("q").send_keys(search)
    driver.find_element_by_name("q").send_keys(Keys.ENTER)
    driver.find_element_by_css_selector("div a h3").click()

    time.sleep(3)
    url = driver.current_url

    if url[:32] == "https://www.songsterr.com/a/wsa/":

        if "-tab-" in url:

            try:
                driver.find_element_by_id("accept").click()
            except:
                pass

            # BPM
            try:
                bpm = driver.find_element_by_class_name("vs1qc").text[1:]
            except:
                bpm = "?"

            # Time signature
            try:
                show_time_signature = True
                time_signature = []
                for name in driver.find_elements_by_class_name("vscf"):
                    time_signature.append(name.text)

                for name in time_signature:
                    if int(name) > 9:
                        time_signature = "?"
                        show_time_signature = False

                if show_time_signature == True:
                    time_signature = str(time_signature)
                    time_signature = (
                        time_signature.replace("[", "")
                        .replace("]", "")
                        .replace("'", "")
                        .replace(",", "")
                    )
                    time_signature = time_signature.replace(" ", "")
                    length = len(time_signature) * 2

                    for i in range(1, len(time_signature) * 2, 3):
                        time_signature = time_signature[:i] + "/" + time_signature[i:]

                    time_signature = time_signature.replace(" ", "")

                    for i in range(3, len(time_signature) * 2, 4):
                        time_signature = time_signature[:i] + " " + time_signature[i:]

                    for i in range(len(time_signature)):
                        if time_signature[len(time_signature) - 1] == "/":
                            time_signature = time_signature[: len(time_signature) - 1]
                            print(time_signature)

                    time_signature = time_signature[:length]
            except:
                time_signature = "?"

            # Number of tracks
            try:
                driver.find_element_by_id("control-mixer").click()
                tracks_number = len(driver.find_elements_by_class_name("Cv3137"))
            except:
                tracks_number = "?"

            # Tuning
            try:
                tuning = []
                for name in driver.find_elements_by_class_name("C8nsu"):
                    tuning.append(name.text)

                tuning = str(tuning)
                tuning = (
                    tuning.replace("[", " ")
                    .replace("]", " ")
                    .replace(",", " ")
                    .replace("'", "")
                )
                tuning = tuning[::-1]
            except:
                tuning = "?"

            # Chords, if avaliable
            try:
                chords_url = driver.find_element_by_class_name("C6c2vy").get_attribute(
                    "href"
                )
            except:
                chords_url = "No chords for this particular song"

            # Artist and song name
            try:
                artist_name = driver.find_element_by_class_name("Bpv319").text
                song_title = driver.find_element_by_css_selector(
                    "span[aria-label='title']"
                ).text
            except:
                artist_name = "?"
                song_title = "?"

            # Difficulty
            try:
                driver.find_element_by_id("menu-search").click()
                time.sleep(1)
                driver.find_element_by_class_name("Cgl126").send_keys(
                    artist_name + " " + song_title
                )
                difficulty = driver.find_element_by_class_name("Cae2ew").get_attribute(
                    "title"
                )
            except:
                difficulty = "?"

            # Tab embed
            embed = discord.Embed(title="Requested tab", color=0x128DF6)
            embed.add_field(name="Artist name", value=artist_name, inline=False)
            embed.add_field(name="Song title", value=song_title, inline=False)
            embed.add_field(name="Url", value=url, inline=False)
            embed.add_field(name="Chords", value=chords_url, inline=False)
            embed.add_field(name="Difficulty", value=difficulty, inline=False)
            embed.add_field(name="BPM", value=bpm, inline=False)
            embed.add_field(name="Tuning", value=tuning, inline=False)
            embed.add_field(name="Time signature", value=time_signature, inline=False)
            embed.add_field(name="Number of tracks", value=tracks_number, inline=False)
            await ctx.send(embed=embed)
            tab.reset_cooldown(ctx)

        elif "-tabs-" in url:

            # Number of tabs for particular artist
            try:
                tabs_number = len(driver.find_elements_by_class_name("Beiqi"))
                artist_name = driver.find_element_by_id("top").text
            except:
                tabs_number = "?"
                artist_name = "?"

            if tabs_number == 50:
                tabs_number = "50+"

            # Tab embed
            embed = discord.Embed(title="Requested artist", color=0x128DF6)
            embed.add_field(name="Artist name", value=artist_name[:-4], inline=False)
            embed.add_field(name="Url", value=url, inline=False)
            embed.add_field(name="Number of tabs", value=tabs_number, inline=False)
            await ctx.send(
                "Unable to find requested tab - redirecting to band page", embed=embed
            )
            tab.reset_cooldown(ctx)

    else:
        await ctx.send("Unable to find requested tab or artist")
        tab.reset_cooldown(ctx)


# On command
@tab_bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
# Informations about bot
async def info(ctx):
    embed = discord.Embed(title="TabBot", color=0x128DF6)
    embed.add_field(
        name="Information",
        value="Use .tab command in format \".tab artist name song name\" to find requested tablature. If the particular tablature couldn't be find or the song name won't be given, only the url to artist page will be sent. The whole tabulature finding process needs a few seconds.",
        inline=False,
    )
    await ctx.send(embed=embed)


# Handling commands errors
@tab.error
async def tab_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Command missing required argument")
        tab.reset_cooldown(ctx)
    if isinstance(error, commands.CommandOnCooldown):
        return
    else:
        raise error


@info.error
async def tab_error(error):
    if isinstance(error, commands.CommandOnCooldown):
        return
    else:
        raise error


# Bot's token
tab_bot.run("token")

# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import heroku3
import asyncio
import requests
import math

from userbot import HEROKU_APP_NAME, HEROKU_API_KEY
from userbot.events import register

Heroku = heroku3.from_key(HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
             'AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/80.0.3987.149 Mobile Safari/537.36'
             )


@register(outgoing=True,
          pattern="^.dyno (on|restart|shutdown|usage|help)(?: |$)")
async def dyno_manage(dyno):
    """ - Restart/Kill dyno - """
    await dyno.edit("`Sending information...`")
    app = Heroku.app(HEROKU_APP_NAME)
    exe = dyno.pattern_match.group(1)
    if exe == "on":
        try:
            Dyno = app.dynos()[0]
        except IndexError:
            app.scale_formation_process("worker", 1)
            text = f"`Starting` ⬢**{HEROKU_APP_NAME}**"
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 30):
                await dyno.edit(text + f"`{dot}`")
                dot += "."
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                sleep += 1
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `is up...`")
        else:
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `already on...`")
    if exe == "restart":
        try:
            """ - Catch error if dyno not on - """
            Dyno = app.dynos()[0]
        except IndexError:
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `is not on...`")
        else:
            text = f"`Restarting` ⬢**{HEROKU_APP_NAME}**"
            Dyno.restart()
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 30):
                await dyno.edit(text + f"`{dot}`")
                dot += "."
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                sleep += 1
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `restarted...`")
    elif exe == "shutdown":
        """ - Complete shutdown - """
        app.scale_formation_process("worker", 0)
        text = f"`Shutdown` ⬢**{HEROKU_APP_NAME}**"
        sleep = 1
        dot = "."
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            dot += "."
            sleep += 1
        await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `turned off...`")
    elif exe == "usage":
        """ - Get your account Dyno Usage - """
        await dyno.edit("`Getting information...`")
        user_id = Heroku.account().id
        headers = {
            'User-Agent': useragent,
            'Authorization': f'Bearer {HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
        }
        path = "/accounts/" + user_id + "/actions/get-quota"
        r = requests.get(heroku_api + path, headers=headers)
        if r.status_code != 200:
            return await dyno.edit("`Error: something bad happened`\n\n"
                                   f">.`{r.reason}`\n")
        result = r.json()
        quota = result['account_quota']
        quota_used = result['quota_used']

        """ - Used - """
        remaining_quota = quota - quota_used
        percentage = math.floor(remaining_quota / quota * 100)
        minutes_remaining = remaining_quota / 60
        hours = math.floor(minutes_remaining / 60)
        minutes = math.floor(minutes_remaining % 60)

        """ - Used per/App Usage - """
        Apps = result['apps']
        msg = "**Dyno Usage Applications**:\n\n"
        for App in Apps:
            try:
                AppQuota = App['quota_used']
                AppQuotaUsed = AppQuota / 60
                AppPercentage = math.floor(AppQuota * 100 / quota)
            except IndexError:
                AppQuotaUsed = 0
                AppPercentage = 0
            finally:
                AppHours = math.floor(AppQuotaUsed / 60)
                AppMinutes = math.floor(AppQuotaUsed % 60)
                msg += (
                    f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                    f"**|**  [`{AppPercentage}`**%**]\n"
                )
        if not msg:
            msg = (" -> `No quota used for any of your Apps`:\n")
            for App in Heroku.apps():
                msg += f"     •  ⬢**{App.name}**.\n"
        return await dyno.edit(
            f"{msg}\n"
            " -> `Dyno hours quota remaining this month`:\n"
            f"     •  `{hours}`**h**  `{minutes}`**m**  "
            f"**|**  [`{percentage}`**%**]"
        )
    elif exe == "help":
        return await dyno.edit(
            ">`.dyno usage`"
            "\nUsage: Check your heroku App usage dyno quota."
            "\nIf one of your app usage is empty, it won't be write in output."
            "\n\n>`.dyno restart`"
            "\nUsage: Restart your dyno application, turn it on if off."
            "\n\n>`.dyno shutdown`"
            "\nUsage: Shutdown dyno completly."
            "\n\n>`.dyno help`"
            "\nUsage: print this help."
        )

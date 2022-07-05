# The MIT License (MIT)
# Copyright (c) 2022 Gamejam.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from discord_webhook import DiscordWebhook, DiscordEmbed


def publish_message_to_discord(webhook_url, content, embed=None, embed_fields=None):
    webhook = DiscordWebhook(url=webhook_url, content=content)

    if embed is not None:
        embed = DiscordEmbed(
            title=embed.get('title'),
            description=embed.get('description'),
            url=embed.get('url'),
            color=embed.get('color'),
        )
        if embed_fields:
            for embed_field in embed_fields:
                embed.add_embed_field(
                    name=embed_field.get('name'),
                    value=embed_field.get('value'),
                )
        webhook.add_embed(embed)

    response = webhook.execute()
    return response

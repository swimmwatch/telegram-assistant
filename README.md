# my-telegram-assistant
:robot: Automation for Telegram messaging.

Read this in other languages:
* [Russian](README.ru.md)
* [English](README.md)

## Features

### Commands
Commands allow handling user requests from conversation (analog [Telegram bot commands](https://core.telegram.org/bots)).
There are several types of commands:
* Explicit - they are explicitly stated in the message.
* Implicit - they are called without stating.

#### Supported commands:

#### Implicit
##### download post/video from social network
Supported social networks:
* [x] YouTube
* [ ] TikTok
* [ ] Instagram
* [ ] Twitter

#### Explicit
##### `\me [type] [scope]` - output contact info about user
##### `\d` - download post by replied message
##### `\audio` - download audio from replied message that contains video
##### `\all` - mention all members in group chat (works only in basic group chat)
##### `\hello` - self-promotion

## Installation and startup
1. Setup necessary environment variables (make `.env` from `.env.example`)
2. docker compose up!

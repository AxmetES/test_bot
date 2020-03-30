## Test bot

Test bot work by [Telegram messenger](https://web.telegram.org/#/login) and [VKontakte](http://vk.com/) social network.

## Getting Started

Fill in the `.env` file:
```python
DB_PASSWORD='Redis database password'
DB_URL='Redis database url'
DB_PORT='Redis database port'

BOT_TOKEN='Bot token from Telegram'

VK_GROUP_KEY='api group key'
```

## Running

Running from command line:
```shell script
python tg_bot.py 
```
to start telegram bot.

![](tg_test_bot.gif)

```shell script
python vk_bot.py 
```

![](vk_test_bot.gif)
to start vkontakte bot.

## License

You may copy, distribute and modify the software.
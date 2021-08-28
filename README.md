# Twitbooks

Attempts to find books mentioned on Twitter

## Requirements

You need these four environment variables set:

`TWITTER_CONSUMER_KEY`
`TWITTER_CONSUMER_SECRET`
`TWITTER_ACCESS_TOKEN_KEY`
`TWITTER_ACCESS_TOKEN_SECRET`

Follow [this](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api) for getting
access to the tokens

## Config

You can configure both the model size and language.
Edit `~/.config/twitbooks/config.json`

```json
{"lang": "en", "size": "sm"}
```

The model sizes can be either: `sm|md|lg`. More information about 
language and models [here](https://spacy.io/usage/models)
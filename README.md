# Pattern-Bot

Monitoring bot that searches for patterns on websites.

## Features

* Search for patterns on websites with regular expressions
* Get notified via a telegram bot if a pattern gets present or absent
* Restrict search space to sub trees via css selectors

## Installation and Configuration

The recommended way to run this bot is via Docker (see `docker-compose.yml`).
The bot has to be configured via a `config.yaml` file that has to be mounted into the container (see `config.example.yaml`).
# learningHouse Service

[![License](https://img.shields.io/github/license/LearningHouseService/learninghouse)](https://github.com/LearningHouseService/learninghouse/blob/main/LICENSE) [![Release](https://img.shields.io/github/v/release/LearningHouseService/learninghouse)](https://github.com/LearningHouseService/learninghouse/releases/latest) [![Build Status](https://img.shields.io/github/actions/workflow/status/LearningHouseService/learninghouse/build_project.yml?branch=main)](https://github.com/LearningHouseService/learninghouse/actions/workflows/build_project.yml) [![PyPI version](https://img.shields.io/pypi/v/learninghouse.svg)](https://pypi.org/project/learninghouse/) [![Discord Chat](https://img.shields.io/discord/997393653758697482)](https://discord.gg/U9axHEYqqB)

![learningHouse Logo](https://raw.githubusercontent.com/LearningHouseService/learninghouse/main/artwork/learninghouse_logo.svg)

The **learningHouse Service** provides machine learning algorithms based on the scikit-learn
Python library as a RESTful API. Its purpose is to offer smart home enthusiasts an easy way to
teach their homes.

You push sensor data into the service, tell it what the right answer was, and it learns the
connection. A *brain* is one such trained model: "is it dark enough to switch the light on?",
"which setpoint should the heating run at?" - whatever your own house does, learned from your own
house's data.

**📖 Full documentation: [learninghouseservice.github.io/learninghouse](https://learninghouseservice.github.io/learninghouse/)**

## 🔧 Features

- 🧠 **Brains**: named models, each one a `classifier` for categorical answers or a `regressor` for
  numerical ones, built on scikit-learn's random forest estimators
- 📡 **Sensors**: your data fields, declared once as `numerical` or `categorical`, preprocessed for
  you
- 🔌 **Training and prediction over REST**, so any home automation system that can send an HTTP
  request can use it
- 🕒 **Automatic time features**: month, day, weekday, hour and minute derived from every training
  row
- 🩹 **Missing sensor values are handled**, not rejected
- 🖥️ **A small web UI** for sensors, brains, API keys and the administration password
- 🔐 **JWT and API key authorization**, with `user` and `trainer` roles
- 🐳 **Docker images** for `linux/amd64` and `linux/arm64`

## 🚀 Quick Start

```bash
pip install -U learninghouse

mkdir -p brains
learninghouse
```

The service listens on <http://localhost:5000/>, the UI is at <http://localhost:5000/ui>. Log in
with the fallback password `learninghouse` and change it - until you do, every other endpoint
stays disabled.

Or with Docker:

```bash
docker run --name learninghouse --rm \
    -v brains:/learninghouse/brains \
    -p 5000:5000 \
    -e "TZ=Europe/Berlin" \
    ghcr.io/learninghouseservice/learninghouse:latest
```

Step by step, with every option explained:
**[Installation guide](https://learninghouseservice.github.io/learninghouse/getting-started/installation/)**

## 📚 Documentation

| Guide | What it covers |
|---|---|
| [Getting Started](https://learninghouseservice.github.io/learninghouse/getting-started/installation/) | Installation, first configuration, running the service |
| [Configuration Reference](https://learninghouseservice.github.io/learninghouse/configuration/) | Every `configuration.yaml` key, sensors, brains, security |
| [Usage](https://learninghouseservice.github.io/learninghouse/usage/training/) | Training, prediction, the UI, where the API documentation lives |
| [Deployment](https://learninghouseservice.github.io/learninghouse/deployment/docker/) | Docker and Docker Compose |
| [Migration](https://learninghouseservice.github.io/learninghouse/migration/environment-variables/) | Upgrading to 2.0.0 from the `LEARNINGHOUSE_*` environment variables |
| [Troubleshooting](https://learninghouseservice.github.io/learninghouse/troubleshooting/) | Known symptoms and what to do about them |
| [Architecture Decisions](https://learninghouseservice.github.io/learninghouse/decisions/) | Why the project is built the way it is |
| [Contributing](AGENTS.md) | Project architecture, conventions and developer commands |

## 💬 Contact and Feedback

If you have any questions, please contact us on Discord.

[![Discord Banner](https://discordapp.com/api/guilds/997393653758697482/widget.png?style=banner2)](https://discord.gg/U9axHEYqqB)

Please share your ideas on what you want to teach your home, suggestions or problems by opening an
[issue](https://github.com/LearningHouseService/learninghouse/issues). We are really looking
forward to your feedback.

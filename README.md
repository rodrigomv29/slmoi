# SLMOI (Small Language Model For Intelligence) Hobby Project
[LLM Wrapper Web app can be found here!](https://llm-wrapper-5a3ac8b7fbbd.herokuapp.com/)
A minimal flask app that integrates openai large language model with several api integrations. 

## Features
- Unlimited LLM Use
- Real time Solutions
- News API Integration
- Weather API Integration

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/rodrigomv29/slmoi.git
   cd slmoi
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your API keys:
   - **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys
   - **NEWS_API**: Get from https://newsapi.org/register
   - **OPENWEATHER_API_KEY**: Get from https://openweathermap.org/api
   - See `.env.example` for all configuration options
## Usage
Run the main application:
```bash
python main.py
```
or 
```bash
export FLASK_APP=main.py
flask run
```

## For Hobbyists: Running Locally

To get started, simply clone the repository, install the dependencies, and follow the usage instructions above. Enjoy experimenting and customizing the project to fit your needs!

## Security

**Important:** Never commit `.env` files or any files containing API keys. See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## Contributing

Pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md) before submitting.

## Donations
LLM Credits, website hosting are funded through my personal budget. If you want to help me please consider donating.

## License
This project is licensed under the GPL License.

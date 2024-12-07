# Gage's Stock Bot

A Discord bot designed to monitor and track stock prices, provide real-time notifications for significant changes, and offer customizable watchlists for users. Built for seamless server integration, powered by the Finnhub API, and ready for deployment.

---

## 🚀 Features
- **📊 Stock Tracking**: Manage server-specific stock watchlists with add and remove commands.
- **💰 Price Fetching**: Retrieve the latest stock prices in real-time.
- **⚠️ Threshold Alerts**: Get notified when stock prices move beyond a specified percentage.
- **🔒 Custom Watchlists**: Each server maintains its unique list of tracked stocks.
- **🌐 Flask Frontend**: Integrated server logs and deployment-ready with Heroku.
- **🎉 Fun Commands**: Includes a command to send random, lighthearted compliments.

---

## 💻 Commands
| Command                 | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `!help`                | Displays a list of available commands with usage details.                  |
| `!addstock SYMBOL`     | Adds a stock to the tracking list for this server.                         |
| `!removestock SYMBOL`  | Removes a stock from the tracking list for this server.                    |
| `!watchlist`           | Displays the server's current stock watchlist.                            |
| `!requests`            | Shows the API request usage for the month.                                |
| `!price SYMBOL`        | Fetches and displays the current price of the specified stock.            |
| `!setthreshold PERCENTAGE` | Sets a percentage threshold for stock price change alerts.                |
| `!forcecheck`          | Manually checks stock prices and sends notifications for significant changes. |
| `!69`                  | Sends a fun, random compliment to the user.                               |

---

## 📋 Requirements
### **Software**
1. Python 3.9+
2. Libraries:
   - `discord.py`
   - `requests`
   - `sqlite3`

### **Environment Variables**
- `TOKEN`: Your Discord bot token.
- `FINNHUB_API_KEY`: Your Finnhub API key.

---

## ⚙️ Installation and Setup

### 1️⃣ Clone the Repository
git clone https://github.com/gagechisholm/Gage-s-Stock-Bot.git
cd Gage-s-Stock-Bot


### 2️⃣ Create a Virtual Environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1


### 3️⃣ Install Dependencies
pip install -r requirements.txt


### 4️⃣ Set Up Environment Variables
#### Create a .env file in the project root and add the following:
TOKEN=your_discord_bot_token
FINNHUB_API_KEY=your_finnhub_api_key


###5️⃣ Run the Bot
python bot.py


## ☁️ Deployment on Heroku

### 1️⃣ Install Heroku CLI
Follow the Heroku CLI installation guide.


### 2️⃣ Log in to Heroku
heroku login


### 3️⃣ Create a Heroku App
heroku create your-app-name


### 4️⃣ Add Buildpacks
heroku buildpacks:add heroku/python


### 5️⃣ Set Environment Variables
heroku config:set TOKEN=your_discord_bot_token
heroku config:set FINNHUB_API_KEY=your_finnhub_api_key


### 6️⃣ Deploy to Heroku
git add .
git commit -m "Initial commit"
git push heroku main


## Security Notes
Ensure sensitive files like .venv, .vscode, and app.log are excluded from your Git repository using .gitignore.
Avoid exposing your API keys and tokens in public repositories.


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

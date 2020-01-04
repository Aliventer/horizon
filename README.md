## Horizon

A multi-purpose discord bot to rule them all. 

## Running

Follow this installation steps to successfully run the bot:

1. **Make sure to get Python 3.5 or higher**

This is required to actually run the bot.

2. **Set up venv**

Just `python3.6 -m venv venv`

3. **Install dependencies**

This is `pip install -U -r requirements.txt`

4. **Create the database in PostgreSQL**

You will need PostgreSQL 9.5 or higher and type the following
in the `psql` tool:

```sql
CREATE ROLE horizon WITH LOGIN PASSWORD 'yourpassword';
CREATE DATABASE horizon OWNER horizon;
```

5. **Setup configuration**

The next step is just to create a `config.py` file in the root directory
 with the following template:

```py
token = "" # your bot's discord token
credentials = { # your postgresql connection info
    "user": "horizon",
    "password": "yourpassword",
    "database": "horizon",
    "host": "host" # just write 127.0.0.1 here if your DB is on the same machine with the bot
}
```

6. **Actually run**

The last step would be to actually run the launch script: `python3.6 launch.py`

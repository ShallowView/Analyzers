from __init__ import *



# Database connection parameters
db_params_SSL = {
    "dbname": "shallowview",
    "user": "Sokhnafaty09", # Replace with your database username
    "password": "", # Replace with your database password
    "host": "s0.net.pimous.dev",
    "port": 31003,
    "sslmode": "require",  # Enforce SSL connection
    "sslcert": "C:/Users/mamef/Downloads/Sokhnafaty09.crt",  # Path to client certificate
    "sslkey": "C:/Users/mamef/Downloads/Sokhnafaty09.key",    # Path to client private key
    "sslrootcert": "C:/Users/mamef/Downloads/pimousdev-db.chain.crt"   # Path to CA certificate
}


""" Connect to database """
engine = get_engine(db_params_SSL)


""" Run All Analyses """
if __name__ == "__main__":


    print("Running win rate by title analysis...")
    title_df = get_win_rate_by_title(engine)
    plot_win_rate_by_title(title_df)


    print("Running win rate by color analysis...")
    color_df = get_win_rate_by_color(engine)
    plot_win_rate_by_color(color_df)


    print("Running average Elo by opening analysis...")
    opening_df = get_avg_elo_by_opening(engine)
    plot_avg_elo_by_opening(opening_df)



import os
import sys

from __init__ import *
from json import load

# Names of the tables in the database
tables = {
	"games": "games",
	"players": "players",
	"openings": "openings"
}

if __name__ == "__main__":
	def main():
		args = sys.argv[1:]
		if not args:
			raise ValueError("Please provide a JSON file path as an argument.")
		with open(args[0], 'r') as file:
			all_params = load(file)

			db_params = {
				"dbname": all_params["dbname"],
				"user": all_params["user"],
				"password": all_params["password"],
				"host": all_params["host"],
				"port": all_params["port"],
			}

			setMaxCores()

			lichessOpeningTSVs = [os.path.join(all_params["openings_dir"], f) for f in
														os.listdir(all_params["openings_dir"]) if
														os.path.isfile(
															os.path.join(all_params["openings_dir"], f))]
			PGNFiles = [os.path.join(all_params["pgn_files_dir"], f) for f in
														os.listdir(all_params["pgn_files_dir"]) if
														os.path.isfile(
															os.path.join(all_params["pgn_files_dir"], f))]

			addOpeningsToDatabase(lichessOpeningTSVs, db_params, tables)

			addNewPGNtoDatabase(PGNFiles, db_params, tables)


	main()

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
		for arg in args:
			if not os.path.isfile(arg):
				raise ValueError(f"File {arg} does not exist.")
			with open(arg, 'r') as file:
				all_params = load(file)

				if all_params.get("pgn_files_dir") is None:
					raise ValueError("Please provide a directory for PGN files.")

				if all_params.get("dbname") is None or all_params.get(
						"user") is None or all_params.get("host") is None or all_params.get(
						"port") is None:
					raise ValueError("One or more necessary database connection "
													 "parameters are absent (dbname, user, host, port)")

				db_params = {
					"dbname": all_params["dbname"],
					"user": all_params["user"],
					"host": all_params["host"],
					"port": all_params["port"],
				}

				if all_params.get("password"):
					db_params["password"] = all_params["password"]

				if all_params.get("sslmode") and all_params.get(
						"sslkey") and all_params.get("sslcert") and all_params.get(
					"sslrootcert"):
					db_params["sslmode"] = all_params["sslmode"]
					db_params["sslkey"] = all_params["sslkey"]
					db_params["sslcert"] = all_params["sslcert"]
					db_params["sslrootcert"] = all_params["sslrootcert"]

				setMaxCores()

				if all_params.get("openings_dir"):

					lichessOpeningTSVs = [os.path.join(all_params["openings_dir"], f) for
																f
																in
																os.listdir(all_params["openings_dir"]) if
																os.path.isfile(
																	os.path.join(all_params["openings_dir"], f))]
					addOpeningsToDatabase(lichessOpeningTSVs, db_params, tables)

				PGNFiles = [os.path.join(all_params["pgn_files_dir"], f) for f in
										os.listdir(all_params["pgn_files_dir"]) if
										os.path.isfile(
											os.path.join(all_params["pgn_files_dir"], f))]

				addNewPGNtoDatabase(PGNFiles, db_params, tables)


	main()

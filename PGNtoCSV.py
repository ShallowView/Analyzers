import pandas as pd

def process_pgn(file : str, output : str) -> None:
    games = []
    dic = {}
    with open(file, "r") as f:
        for line in f.readlines():
            if line.startswith("["):
                string = line[1:-1]
                header = string.split()[0]
                dic[header] = string[len(header):-2].strip().strip('"')
            else:
                if len(dic)!=0:  # Append only non-empty dictionaries
                    games.append(dic)
                dic = {}

    # Create a DataFrame
    df = pd.DataFrame(games)

    # Save to CSV
    df.to_csv(output, index=False)
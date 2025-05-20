import json
import plotly.graph_objects as go
import plotly.io as pio

import json
import plotly.graph_objects as go

with open("analysis_results.json", 'r') as f:
    all_results = json.load(f)

plots_data = all_results.get("plots", {})

for category, plot_list_json in plots_data.items():
    print(f"--- Catégorie : {category.replace('_', ' ').title()} ---")
    for i, plot_json_str in enumerate(plot_list_json):
        fig_dict = json.loads(plot_json_str)
        fig = go.Figure(fig_dict)
        fig.show() # Ou fig.show("notebook") si vous êtes dans un environnement spécifique Jupyter

def view_analysis_plots(json_file_path="analysis_results.json"):
    """
    Lit le fichier JSON des résultats d'analyse et affiche les figures Plotly.
    """
    try:
        with open(json_file_path, 'r') as f:
            all_results = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{json_file_path}' n'a pas été trouvé.")
        print("Assurez-vous que 'main.py' a été exécuté et que le fichier a été créé.")
        return
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de décoder le fichier JSON '{json_file_path}'. Il est peut-être corrompu.")
        return

    plots_data = all_results.get("plots", {})

    if not plots_data:
        print("Aucun graphique trouvé dans le fichier JSON.")
        return

    print(f"Affichage des graphiques depuis '{json_file_path}'...")

    for category, plot_list_json in plots_data.items():
        print(f"\n--- Catégorie : {category.replace('_', ' ').title()} ---")
        if not plot_list_json:
            print(f"Aucun graphique pour cette catégorie.")
            continue

        for i, plot_json_str in enumerate(plot_list_json):
            try:
                # plot_json_str est déjà une chaîne JSON
                fig_dict = json.loads(plot_json_str)
                fig = go.Figure(fig_dict)
                fig.show() # Ceci ouvrira le graphique dans votre navigateur par défaut
                print(f"Affichage du graphique {i+1} pour la catégorie '{category}'.")
            except Exception as e:
                print(f"Erreur lors de l'affichage du graphique {i+1} pour la catégorie '{category}': {e}")
                print(f"JSON du plot problématique: {plot_json_str[:200]}...") # Afficher un extrait

    # Vous pouvez également afficher les rapports textuels si vous le souhaitez
    text_reports = all_results.get("text_reports", {})
    if text_reports:
        print("\n--- Rapports Textuels ---")
        for report_name, report_content in text_reports.items():
            print(f"\n--- {report_name.replace('_', ' ').title()} ---")
            # Pour la classification_report, c'est un dictionnaire, on peut le pretty-printer
            if isinstance(report_content, dict):
                print(json.dumps(report_content, indent=4))
            else:
                print(report_content)


if __name__ == "__main__":
    view_analysis_plots()
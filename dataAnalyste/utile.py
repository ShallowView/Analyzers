import matplotlib.pyplot as plt
import seaborn as sns

def plot_barplot(data, lables_list, values_list, title, xlabel, ylabel, rotation=45, ha='right', figsize=(10, 6)):
    plt.figure(figsize=figsize)
    ax = sns.barplot(x=data[lables_list], y=data[values_list])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha=ha)
    plt.tight_layout()
    return ax


from altair import LayerChart
import pandas as pd
import prince



dataset = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/balloons/adult+stretch.data')
dataset.columns = ['Color', 'Size', 'Action', 'Age', 'Inflated']
dataset.head()

mca : prince.MCA = prince.MCA( # creation of a class
    n_components=3,
    n_iter=3,
    copy=True,
    check_input=True,
    engine='sklearn',
    random_state=42
)
mca = mca.fit(dataset)

one_hot = pd.get_dummies(dataset) ## turns categorical values into usabel ones ( not numeric just useful under hood)
mca_no_one_hot = prince.MCA(one_hot=False)
mca_no_one_hot = mca_no_one_hot.fit(one_hot)

print(mca.eigenvalues_summary)

print(mca.column_coordinates(dataset).head())


plot_object : LayerChart = mca.plot(
    dataset,
    x_component=0,
    y_component=1,
    show_column_markers=True,
    show_row_markers=True,
    show_column_labels=False,
    show_row_labels=False
)

plot_column_labels : LayerChart = mca.plot(
    dataset,
    x_component=0,
    y_component=1,
    show_column_markers=True,
    show_row_markers=False,
    show_column_labels=True, # Set to True to display column labels
    show_row_labels=False
)
plot_column_labels.save("prince_labels.png")

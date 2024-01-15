import pandas as pd
import matplotlib.pyplot as plt
from airland import Airland
import seaborn as sns

# Assuming your data is stored in a CSV file named 'airland_data.csv'
df = pd.read_csv('stats_results.csv')

# Plotting
plt.figure(figsize=(10, 6))

# CP Execution Time
plt.plot(df['N_planes'], df['CP_memory_usage'], marker='o', color='navy', linestyle='-', label='CP')

# MIP Execution Time
plt.plot(df['N_planes'], df['MIP_memory_usage'], marker='o', color='brown', linestyle='-', label='MIP')

plt.xlabel('Number of planes')
plt.ylabel('Memory Usage (bytes)')
plt.title('Comparison between MIP and CP Memory Usage')
plt.legend()
plt.grid(True)
plt.show()




# Calculate the percentage improvement
df['Percentage_Improvement'] = ((df['MIP_memory_usage'] - df['CP_memory_usage']) / df['MIP_memory_usage']) * 100

# Determine bar colors based on improvement direction
df['Bar_Color'] = ['navy' if improvement > 0 else 'maroon' for improvement in df['Percentage_Improvement']]

# Plotting with seaborn
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

# Convert the 'Bar_Color' column to a list
bar_colors = list(df['Bar_Color'])

ax = sns.barplot(x='Airland', y='Percentage_Improvement', data=df, palette=bar_colors)

plt.xlabel('Airland')
plt.ylabel('Percentage Improvement (%)')
plt.title('Memory Usage Percentage Improvement of CP in Relation to MIP')

# Add text annotations above each bar
for p, color in zip(ax.patches, bar_colors):
    height = p.get_height()
    text_color = 'white' if color == 'maroon' else 'black'
    ax.annotate(f'{height:.2f}%', (p.get_x() + p.get_width() / 2., height),
                ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=8, color=text_color)
plt.show()



# Sort the DataFrame by actual landing time
df_sorted = df.sort_values(by='actual_land_time')

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot vertical lines for each plane
for idx, row in df_sorted.iterrows():
    plt.vlines(x=idx, ymin=row['E'], ymax=row['L'], color='gray', linestyle='dashed', linewidth=1, alpha=0.5)
    plt.scatter(idx, row['A'], marker='o', color='blue', label='Earliest Time' if idx == 0 else "")
    plt.scatter(idx, row['T'], marker='o', color='green', label='Target Time' if idx == 0 else "")
    plt.scatter(idx, row['L'], marker='o', color='red', label='Latest Time' if idx == 0 else "")
    plt.scatter(idx, row['actual_land_time'], marker='o', color='black', label='Actual Landing Time' if idx == 0 else "")

# Connect the points with vertical lines
for i in range(1, len(df_sorted)):
    plt.plot([i-1, i], [df_sorted.iloc[i-1]['actual_land_time'], df_sorted.iloc[i]['actual_land_time']], color='black')

# Set x-axis ticks and labels
plt.xticks(range(len(df_sorted)), df_sorted['id'])
plt.xlabel('Plane ID')

# Set y-axis ticks
plt.yticks(range(df_sorted['E'].min(), df_sorted['L'].max() + 1))
plt.ylabel('Discrete Time')

# Set plot title
plt.title('Aircraft Actual Landing Time Order')

# Display the legend
plt.legend()

# Show the plot
plt.show()


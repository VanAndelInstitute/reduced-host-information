import pandas as pd

# Example DataFrame
data = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}
df = pd.DataFrame(data)

# Values to insert in the first column
new_column_values = [10, 20, 30]

# Insert the new column at the beginning (index 0)
df.insert(0, 'new_col', new_column_values)

# Display the updated DataFrame
print(df)
import pandas as pd
# Read JSON string into a Pandas DataFrame
#df_from_string = pd.read_json(yelp_academic_dataset_review.json)
print("DataFrame from JSON string:")
#print(df_from_string)

# Example JSON file path (replace with your actual file path)
#json_file_path = 'path/to/your/json_file.json'

# Read JSON file into a Pandas DataFrame (first 10 lines)
df_from_file = pd.read_json(r'D:/project-1/project/src/datasets/yelp_academic_dataset_review.json', lines=True, nrows=10)
print("\nDataFrame from JSON file (first 10 lines):")
print(df_from_file)
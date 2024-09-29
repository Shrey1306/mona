import pandas as pd
from fuzzywuzzy import process, fuzz
import Levenshtein
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# clean_envi_path = 'clean-environmental-dataset.csv'
# clean_envi_data = pd.read_csv(clean_envi_path)
# cleaneddf = clean_envi_data.drop_duplicates(keep = 'first')
# cleaneddf.to_csv('new_environmental_dataset1.csv')

# Load the nasdaq dataset
# nasdaq_df = pd.read_csv('nasdaq.csv')

# original_data_path = 'cleaned_environmental_dataset_no_duplicates.csv'  # Update this path
# nasdaq_screener_path = 'nasdaq_cleaned.csv'  # Update this path

# original_data = pd.read_csv(original_data_path)
# nasdaq_data = pd.read_csv(nasdaq_screener_path)
# # Preprocess and standardize company names (optional, depends on your data)
# def standardize_name(name):
#     import re
#     suffixes = ['Common Stock', 'Warrant', 'Ordinary Shares', 'Depositary Shares', ' Inc', ' Corp', ' Company', ' Corporation', ' Ltd', ' Limited', ' Co', '\.', ',']
#     pattern = '|'.join(suffixes)
#     name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
#     return name

# original_data['Standardized Company'] = original_data['Company_Name'].apply(standardize_name)
# nasdaq_data['Standardized Name'] = nasdaq_data['Company Name'].apply(standardize_name)

# # Create a mapping of standardized names to NASDAQ symbols
# name_to_symbol = pd.Series(nasdaq_data.Symbol.values, index=nasdaq_data['Standardized Name']).to_dict()

# # Define a function to perform fuzzy matching
# def find_best_match(name, choices, scorer=fuzz.WRatio, threshold=85):
#     best_match = process.extractOne(name, choices, scorer=scorer)
#     if best_match and best_match[1] >= threshold:
#         print(best_match[0])
#         return best_match[0]
#     else:
#         print("None")
#         return None

# # Apply fuzzy matching
# nasdaq_names = nasdaq_data['Standardized Name'].unique()
# original_data['Fuzzy Matched Name'] = original_data['Standardized Company'].apply(lambda x: find_best_match(x, nasdaq_names))
# original_data['Fuzzy Corrected Ticker'] = original_data['Fuzzy Matched Name'].map(name_to_symbol)


# # Save the updated dataset
# original_data.to_csv('save_updated_dataset.csv', index=False)  # Update the save path


# def clean_name(name):
#     suffixes = ['Corporation', 'Ordinary Shares', 'Common Stock', 'Depositary Shares', 'Common Shares']
#     for suffix in suffixes:
#         if name.endswith(suffix):
#             name = name[:name.find(suffix)].strip()
#     return name

# # Apply the cleaning function to the Name column
# nasdaq_df['Updated_Names'] = nasdaq_df['Name'].apply(clean_name)

# # Load the clean environmental dataset
# env_df = pd.read_csv('cleaned_environmental_dataset_no_duplicates.csv')

# # Define a function for fuzzy matching using the correct scorer
# def get_best_match(row, choices, limit=1):
#     best_matches = process.extract(row, choices, scorer=fuzz.WRatio, limit=limit)
#     # Assuming the best match is returned first
#     if best_matches:
#         print(best_matches[0][0])
#     else:
#         print("none")
#     return best_matches[0][0] if best_matches else None

# # Apply fuzzy matching to find the best match in env_df for each entry in nasdaq_df
# nasdaq_df['Best_Match'] = nasdaq_df['Updated_Names'].apply(lambda x: get_best_match(x, env_df['Company_Name'].tolist()))

# # Now merge the datasets based on the best match found
# merged_df = pd.merge(nasdaq_df, env_df, left_on='Best_Match', right_on='Company_Name', how='left')

# merged_df.to_csv('ticker_environmental.csv')

new_envi_path = 'clean_environment_w_ticker.csv'
new_envi_data = pd.read_csv(new_envi_path)
market_path = 'cleaned_market_cap_values.csv'
market_path_data = pd.read_csv(market_path)

new_envi_data['Company_Name'] = new_envi_data['Company_Name'].str.lower()
market_path_data['Company_Name'] = market_path_data['Company_Name'].str.lower()

combined_df = pd.merge(new_envi_data, market_path_data, on='Company_Name', how='outer')
combined_df.to_csv('combined_dataset.csv')

new_path = 'combined_dataset.csv'
new_df = pd.read_csv(new_path)
new_df['ticker'] = new_df['Ticker_x'].combine_first(new_df['Ticker_y'])
new_df.dropna(subset=['ticker'], inplace=True)
final_df = new_df.drop(columns=['Ticker_x', 'Ticker_y'])
final_df.to_csv('final_combined_dataset.csv')
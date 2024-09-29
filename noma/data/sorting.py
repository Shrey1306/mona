import pandas as pd
from fuzzywuzzy import process, fuzz
import Levenshtein
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# # Load your datasets
# original_data_path = 'data/ethical-params.csv'  # Update this path
# nasdaq_screener_path = 'data/nasdaq.csv'  # Update this path

# original_data = pd.read_csv(original_data_path)
# nasdaq_data = pd.read_csv(nasdaq_screener_path)

# # Preprocess and standardize company names (optional, depends on your data)
# def standardize_name(name):
#     import re
#     suffixes = [' Inc', ' Corp', ' Corporation', ' Ltd', ' Limited', ' Co', '\.', ',']
#     pattern = '|'.join(suffixes)
#     name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
#     return name

# original_data['Standardized Company'] = original_data['Company'].apply(standardize_name)
# nasdaq_data['Standardized Name'] = nasdaq_data['Name'].apply(standardize_name)

# # Create a mapping of standardized names to NASDAQ symbols
# name_to_symbol = pd.Series(nasdaq_data.Symbol.values, index=nasdaq_data['Standardized Name']).to_dict()

# # Define a function to perform fuzzy matching
# def find_best_match(name, choices, scorer=fuzz.WRatio, threshold=70):
#     best_match = process.extractOne(name, choices, scorer=scorer)
#     if best_match and best_match[1] >= threshold:
#         return best_match[0]
#     else:
#         return None

# # Apply fuzzy matching
# nasdaq_names = nasdaq_data['Standardized Name'].unique()
# original_data['Fuzzy Matched Name'] = original_data['Standardized Company'].apply(lambda x: find_best_match(x, nasdaq_names))
# original_data['Fuzzy Corrected Ticker'] = original_data['Fuzzy Matched Name'].map(name_to_symbol)

# # Results
# print(original_data[['Company', 'Tickers', 'Fuzzy Corrected Ticker']].head())

# # Save the updated dataset
# original_data.to_csv('path_to_save_updated_dataset.csv', index=False)  # Update the save path

# file_path = 'ethical-params-updated.csv'  # Update this path to your file's location
# data = pd.read_csv(file_path)

# # Remove entries with any empty values
# cleaned_data = data.dropna()

# # Save the cleaned data to a new CSV file
# cleaned_file_path = 'ethical-params-updated-cleaned.csv'  # Specify your desired output file name
# cleaned_data.to_csv(cleaned_file_path, index=False)

# print(f"Cleaned data saved to {cleaned_file_path}.")

# Function to clean company names
# def clean_company_name(name):
#     prefixes_suffixes = [' Inc', ' Corp', ' Corporation', ' LLC', ' Ltd', ' Limited', ' Co', '\.', ',', 'Common Stock']
#     pattern = '|'.join(prefixes_suffixes)
#     cleaned_name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
#     return cleaned_name

# # Load datasets
# nasdaq_path = 'nasdaq.csv'  # Update with the actual path
# clean_environmental_path = 'clean-environmental-dataset.csv'  # Update with the actual path
# nasdaq_data = pd.read_csv(nasdaq_path)
# clean_environmental_data = pd.read_csv(clean_environmental_path)

# # Clean company names
# nasdaq_data['Cleaned_Name'] = nasdaq_data['Name'].apply(clean_company_name)
# clean_environmental_data['Cleaned_Company_Name'] = clean_environmental_data['Company_Name'].apply(clean_company_name)

# # Fuzzy match function adjusted for parallel execution
# def get_ticker_for_company(company_row):
#     cleaned_company_name = company_row['Cleaned_Company_Name']
#     best_match = process.extractOne(cleaned_company_name, nasdaq_data['Cleaned_Name'].tolist(), score_cutoff=80)
#     if best_match:
#         matched_name = best_match[0]
#         ticker = nasdaq_data.loc[nasdaq_data['Cleaned_Name'] == matched_name, 'Symbol'].iloc[0]
#         return (cleaned_company_name, ticker)
#     else:
#         return (cleaned_company_name, None)

# # Parallel fuzzy matching and collecting results
# def parallel_fuzzy_matching():
#     match_results = {}
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         futures = [executor.submit(get_ticker_for_company, row) for index, row in clean_environmental_data.iterrows()]
#         for future in as_completed(futures):
#             company_name, ticker = future.result()
#             match_results[company_name] = ticker
#             print(ticker)
#     return match_results

# # Run the parallel fuzzy matching
# match_results = parallel_fuzzy_matching()

# # Merge the matching results back into the original dataframe
# clean_environmental_data['Ticker'] = clean_environmental_data['Cleaned_Company_Name'].map(match_results)

# # Save the updated dataframe to a new CSV file
# updated_file_path = 'updated_clean_environmental_dataset.csv'  # Specify your desired output file name
# clean_environmental_data.to_csv(updated_file_path, index=False)

# print(f"Updated clean environmental dataset with tickers saved to {updated_file_path}.")

# clean_environment_path = 'updated_clean_environmental_dataset.csv' 
# clean_environment_data = pd.read_csv(clean_environment_path)

# clean_environment_data.drop_duplicates(subset="Company_Name", keep=False, inplace=True) 
# clean_environment_data.to_csv('duplicates_removed_updated_clean_environmental_dataset.csv')

# updated_beta_path = 'updated_beta_cause_data.csv'
# updated_beta_data = pd.read_csv(updated_beta_path)

# merged_data = pd.merge(updated_beta_data , clean_environment_data, on='Ticker', how='inner')

# # Write it to a new CSV file
# merged_data.to_csv('final_combined.csv')

# Load the nasdaq dataset
# nasdaq_df = pd.read_csv('nasdaq.csv')

# Function to remove specified prefixes and suffixes
# def clean_name(name):
#     suffixes = ['Corporation', 'Ordinary Shares', 'Common Stock', 'Depositary Shares', 'Common Shares']
#     for suffix in suffixes:
#         if name.endswith(suffix):
#             name = name[:name.find(suffix)].strip()
#     return name

# # Apply the cleaning function to the Name column
# nasdaq_df['Updated_Names'] = nasdaq_df['Name'].apply(clean_name)

# # Load the clean environmental dataset
# env_df = pd.read_csv('clean-environmental-dataset.csv')

# # Define a function for fuzzy matching
# def get_best_match(row, choices, limit=1):
#     best_matches = process.extract(row, choices, scorer=fuzz.WRatio, limit=limit)
#     # Assuming the best match is returned first
#     if (best_matches[0][0] != None):
#         print(best_matches[0][0])
#     else:
#         print(None)
#     return best_matches[0][0] if best_matches else None

# # Apply fuzzy matching to find the best match in env_df for each entry in nasdaq_df
# nasdaq_df['Best_Match'] = nasdaq_df['Updated_Names'].apply(lambda x: get_best_match(x, env_df['Company_Name'].tolist()))

# # Now merge the datasets based on the best match found
# merged_df = pd.merge(nasdaq_df, env_df, left_on='Best_Match', right_on='Company_Name', how='left')
# merged_df.to_csv('new_environmental_dataset.csv')

df = pd.DataFrame(data)

newdf = df.drop_duplicates()
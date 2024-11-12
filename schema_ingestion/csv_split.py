import pandas as pd

def load_and_split_file(file_path):
    # Load the file with separator ;
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, sep=';')
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)  # Excel files do not require sep parameter
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
    
    # Define the acronyms
    acronyms = ['org', 'syn', 'char', 'sp', 'inst', 'anal', 'pre']
    df_dict = {acronym: [] for acronym in acronyms}
    df_dict[None] = []

    # Separate rows based on the first column acronym
    for index, row in df.iterrows():
        acronym = next((acronym for acronym in acronyms if str(row.iloc[0]).startswith(acronym)), None)
        df_dict[acronym].append(row)

    # Convert lists to DataFrames
    for acronym in df_dict:
        if df_dict[acronym]:
            df_dict[acronym] = pd.DataFrame(df_dict[acronym])
        else:
            df_dict[acronym] = pd.DataFrame()

    # Extract ExperimentID from the org DataFrame
    experiment_id = None
    if not df_dict['org'].empty:
        experiment_id = df_dict['org'].iloc[0, 2]  # Assuming ExperimentID is in the second column

    # Process and save each DataFrame
    for acronym, df_part in df_dict.items():
        if not df_part.empty:
            # Remove the first column
            df_part = df_part.iloc[:, 1:]

            # Remove columns that are entirely NaN (if any)
            df_part = df_part.dropna(axis=1, how='all')

            # Transpose if necessary
            if acronym in ['org', 'char', 'inst']:
                df_part = df_part.transpose()

            # Add ExperimentID column to all except 'org'
            if acronym != 'org' and experiment_id is not None:
                df_part.insert(0, 'ExperimentID', experiment_id)
                df_part.iat[0, 0] = 'ExperimentID'
            print(df_part)
            # Define file name
            part_name = acronym if acronym else 'others'
            output_file = f"schema_ingestion/temp/{part_name}.csv"

            # Save to CSV with separator ; and no header
            df_part.to_csv(output_file, index=False, sep=';', header=False)
            print(f"Saved {output_file}")


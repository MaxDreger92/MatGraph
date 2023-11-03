import re

def load_csv_to_dataframe(file_path):
    """
    Load a CSV file into a pandas DataFrame.

    Parameters:
    - file_path (str): The path to the CSV file to be loaded.

    Returns:
    - DataFrame: If the file is successfully loaded.
    - None: If there's an error in loading the file.
    """

    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def get_unique_csv_headers(csv_path):
    """
    Extract unique column headers from a CSV file, excluding the 0th column.

    Numeric suffixes (like .1, .2, etc.) from headers are removed to obtain the unique headers.

    Parameters:
    - csv_path (str): The path to the CSV file.

    Returns:
    - list: A list of unique column headers.
    """

    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_path)

    # Get unique column headers excluding the 0th column
    unique_csv_headers = df.columns[1:].to_list()

    # Remove numeric suffixes using regular expressions
    unique_csv_headers = [re.sub(r'\.\d+', '', header) for header in unique_csv_headers]

    # Get unique column names after removing numeric suffixes
    unique_csv_headers = list(set(unique_csv_headers))

    return unique_csv_headers

def find_row_by_heading(dataframe, search_value):
    """
    Find the row index of the first occurrence where the 0th column contains the given search value.

    Parameters:
    - dataframe (DataFrame): The DataFrame to search in.
    - search_value (str): The value to search for in the 0th column.

    Returns:
    - int: Index of the row where the search_value was found.
    - None: If search_value was not found or an error occurred.
    """

    try:
        # Use the .str.contains method to check if the target_heading is present in column 0
        # This returns a boolean Series
        matches = dataframe.iloc[:, 0].str.contains(search_value, case=False, na=False)

        # Find the first row index where the condition is True
        row_index = matches.idxmax()

        # If no match was found, idxmax() returns NaN, so handle that case
        if pd.notna(row_index):
            return int(row_index)
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def find_cols_by_heading(file_path, heading):
    """
    Find the column indices in a CSV file where the column header contains the given heading.

    Parameters:
    - file_path (str): The path to the CSV file.
    - heading (str): The string to search for in column headers.

    Returns:
    - list: A list of column indices where the heading was found.
    """

    df = load_csv_to_dataframe(file_path)

    return [idx for idx, col_name in enumerate(df.columns) if heading in col_name]

def get_first_cell_for_heading(file_path, heading):
    """
    Parse a CSV file and return the first cell in the first column for a given heading.

    Parameters:
    - file_path (str): The path to the CSV file.
    - heading (str): The string to search for in column headers.

    Returns:
    - str: The first cell in the first column for the given heading.
    - None: If the heading is not found or an error occurred.
    """

    df = load_csv_to_dataframe(file_path)
    row_index = find_row_by_heading(df, heading)
    column_index = find_cols_by_heading(file_path, heading)

    # If heading was found in the dataframe
    if row_index is not None:
        # Return the value in the first cell of the row
        return df.iloc[row_index, column_index[0]]

    return None

import pandas as pd

def get_true_node_row(csv_path):
    """
    Search for the first row index in a CSV file where any of the options in 'true_node_label_options' is found in the 0th column.

    Parameters:
    - csv_path (str): The path to the CSV file.

    Returns:
    - int: Index of the row where any of the options was found.
    - None: If none of the options were found.
    """
    true_node_label_options = ["node label","node_label"]

    dataframe = load_csv_to_dataframe(csv_path)
    # Iterate over the list of possible label options to find the true node label
    for option in true_node_label_options:
        row = find_row_by_heading(dataframe, option)
        # If the label was found in a row other than the first one (index 0), return its index
        if row != 0 and row is not None:
            return row
    # Return None if none of the label options were found
    return None

def get_true_node_label(csv_path, index_heading, row = 69):
    """
    Find and return the true node label from a CSV file based on a given heading.
    This function looks for the label in columns containing the specified heading.

    Parameters:
    - csv_path (str): The path to the CSV file.
    - heading (str): The heading (or part of it) to identify the columns of interest.

    Returns:
    - str: The true node label found under the given heading.
    - None: If no label was found.
    """

    dataframe = load_csv_to_dataframe(csv_path)
    # Fetch the index of the row containing the true node label
    row = row
    # Fetch the column indices containing the given heading
    col = index_heading


    return dataframe.iloc[row, col]





if __name__ == "__main__":
    # Sample CSV path and heading for demonstration
    sample_csv_path = "../../data/materials.csv"
    sample_heading = "product_id"

    # Find the true node row
    true_node_row_index = get_true_node_row(sample_csv_path)
    print(f"True Node Row Index: {true_node_row_index}")

    # Find the true node label based on a heading
    label = get_true_node_label(sample_csv_path, sample_heading)
    print(f"True Node Label for Heading '{sample_heading}': {label}")

    headings = get_unique_csv_headers(sample_csv_path)
    print(f"Unique headings: {headings}")
from telexpense.sheets.types import Categories


def parse_categories(category_data: list[list]) -> Categories:
    """This function gets categories from sheet as list of lists
    and parses it Categories dictionary.

    Args:
        category_data (list[list]): list of rows containig list of
        values in each row

    Returns:
        Categories: dictionary, containing "income" and "expense"
        keys with parsed categories like::

        categories = {
            "income": {"Salary": []}
            "expense": {"Food": ["Grocaries", "Restaurants"]}
        }
    """
    exp_categories, inc_categories = {}, {}

    # By default, expense categories comes first
    pointer_dict = exp_categories

    # Looping through all sheet rows
    for category_sheet_row in category_data:
        if len(category_sheet_row) == 0:
            # Blank row
            continue
        elif len(category_sheet_row) == 1:
            # This row contains only category, without subcategory
            pointer_dict[category_sheet_row[1]] = []
        else:
            if category_sheet_row[1] == "Income category":
                pointer_dict = inc_categories
                # Skipping this row, it contains only header
                continue

            # This row contains category and subcategories
            pointer_dict[category_sheet_row[1]] = category_sheet_row[2:]

    return Categories(income=inc_categories, expense=exp_categories)


def parse_accounts(account_data: list[list]) -> dict:

    """This function gets list of lists of account names and
    it's aliases and parses it to dictionary.

    Args:
        account_data (list[list]): list of rows containig list of
        account name and it's alias in each row

    Returns:
        dict: dictionary with account names and aliases like::

        accounts = {"Revolut": "rev", "CitiBank": "citi"}
    """
    accounts = {}

    for account_alias_row in account_data:
        row_lenght = len(account_alias_row)

        # If row contains only account name without alias
        if row_lenght == 1:
            accounts[account_alias_row[0]] = None

        # If row contains account name and/or alias
        elif row_lenght == 2:
            # If row contains only alias
            if account_alias_row[0] != "":
                accounts[account_alias_row[0]] = account_alias_row[1]
            # If row contains account name and alias
            else:
                accounts[account_alias_row[1]] = None

    return accounts

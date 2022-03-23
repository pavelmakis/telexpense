import gspread

class Sheet:
    def __init__(self) -> None:
        self.gspread_client = gspread.service_account(filename="token.json")
        self.user_sheet = self.gspread_client.open_by_url('https://docs.google.com/spreadsheets/d/1DfLa0vry-8YJVZgdkPDPcQEI6vYm19n2ddTBPNWo7K8')
    
    def get_savings(self):
        main_sheet = self.user_sheet.worksheet("Main")
        savings_amount = main_sheet.acell('B7').value
        return savings_amount
    
    def get_total(self):
        main_sheet = self.user_sheet.worksheet("Main")
        total_amount = main_sheet.acell('B11').value
        return total_amount

    def get_accounts(self) -> dict:
        # Selectiong sheet 'Preferences'
        pref_sheet = self.user_sheet.worksheet("Preferences")

        # Sending query to get accounts and its amounts
        data = pref_sheet.batch_get(['H4:H23'])

        # Parsing data
        parsed_data, accounts = {}, []
        for i in range(len(data[0])):
            # If user left cell blank
            if data[0][i] == []:
                continue
            # Parse data as account list
            accounts.append(data[0][i][0])
        
        # Adding list of accounts to dictionary
        parsed_data['accounts'] = accounts

        return parsed_data

    def get_account_amounts(self) -> list:
        # Selectiong sheet 'Main'
        main_sheet = self.user_sheet.worksheet("Main")

        # Sending query to get accounts and its amounts
        data = main_sheet.batch_get(['N7:N26', 'O7:O26'])

        # Parsing data
        parsed_data = []
        for i in range(len(data[0])):
            # If user left cell blank
            if data[0][i] == []:
                continue
            # Parse data as list of tuples
            parsed_data.append(tuple((data[0][i][0], data[1][i][0])))
        
        return parsed_data

    def get_day_categories_accounts(self) -> dict:
        """Get today's date, income and outcome categories and accounts as dictionary.
        This function replaced the previous few functions, in which many separate 
        requests were sent, which was inefficient. Now you can get all the data you need 
        in one query.

        Returns:
            dict: all the data needed for parsing expense or income as dictionary of lists
        """
        # Dictionary with data
        # It will contain today date, outcome categories, income categories
        # and account lists
        parsed_data = {}

        # Getting all data from specified ranges as lists
        pref_sheet = self.user_sheet.worksheet("Preferences")
        data = pref_sheet.batch_get(['E25', 'B4:B44', 'C4:C44', 'H4:H23'])

        # Writing date to dictionary
        parsed_data['today'] = data[0][0][0]

        # Parsing outcome categories from list os lists to dictionary
        outcome_categories = []
        for i in range(len(data[1])):
            # If user left blank cell in category column
            if data[1][i] == []:
                continue
            outcome_categories.append(data[1][i][0])
        # Writing outcome categories to dictionary
        parsed_data['outcome categories'] = outcome_categories

        # Parsing income categories from list os lists to dictionary
        income_categories = []
        for i in range(len(data[2])):
            # If user left blank cell in category column
            if data[2][i] == []:
                continue
            income_categories.append(data[2][i][0])
        # Writing income categories to dictionary
        parsed_data['income categories'] = income_categories

        # Parsing accounts from list os lists to dictionary
        accounts = []
        for i in range(len(data[3])):
            if data[3][i] == []:
                continue
            accounts.append(data[3][i][0])
        # Writing accounts to dictionary
        parsed_data['accounts'] = accounts

        return parsed_data

    def add_record(self, data: list):
        """Insert new row with transaction data to transactions list in Google Sheet.

        Args:
            data (list): parsed data for inserting in user's sheet.
        """

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_row(data, index=2, value_input_option='USER_ENTERED')
        return

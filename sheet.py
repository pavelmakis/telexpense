import os
import formulas

import gspread
from gspread import exceptions

class Sheet:
    account = gspread.service_account(
        filename=os.path.join(os.path.dirname(__file__), 'token.json'))

    def __new__(cls, key):
        try:
            cls.account.open_by_key(key)
        except exceptions.GSpreadException:
            return None
        
        # If no errors, call __init__
        return super(Sheet, cls).__new__(cls)

    def __init__(self, key, gspread_client=account) -> None:
        """Opens user sheet"""
        self.user_sheet = gspread_client.open_by_key(key)

    def is_right_sheet(self) -> bool:
        """Сhecks if user has provided the correct sheet"""
        # Check if there are sheets that are in my template
        try:
            main_sheet = self.user_sheet.worksheet("Main")
            pref_sheet = self.user_sheet.worksheet("Preferences")
            tran_sheet = self.user_sheet.worksheet("Transactions")
        except exceptions.WorksheetNotFound:
            return False
        
        # Check if there are specific cells 
        try:
            data = pref_sheet.batch_get(['B2', 'E15', 'H2'])
        except exceptions.APIError:
            return False
        
        # Check cells values
        if data != [[['Categories']], [['Currency']], [['Accounts']]]:
            return False
        
        return True

    def get_day_accounts(self) -> dict:
        """Get today date and account list in one query.
        This data is ised for adding transactions.

        Returns:
            dict: 'today' and 'accounts'
        """
        # Selectiong sheet 'Preferences'
        pref_sheet = self.user_sheet.worksheet("Preferences")

        # Sending query to get accounts and its amounts
        data = pref_sheet.batch_get(['E25', 'H4:H23'])

        # Parsing data
        parsed_data, accounts = {}, []

        # Added today date to dictionary
        parsed_data['today'] = data[0][0][0]

        for i in range(len(data[1])):
            # If user left cell blank
            if data[1][i] == []:
                continue
            # Parse data as account list
            accounts.append(data[1][i][0])
        
        # Adding list of accounts to dictionary
        parsed_data['accounts'] = accounts

        return parsed_data

    def get_account_amounts(self) -> list:
        """Get all accounts and its amounts in one query.
        Data is used to send available amounts to user.

        Returns:
            list: list of tuples (account, amount)
        """
        # Selectiong sheet 'Main'
        main_sheet = self.user_sheet.worksheet("Main")

        # Sending query to get accounts and its amounts and daily available
        data = main_sheet.batch_get(['N7:N26', 'O7:O26', 'N3'])

        # Parsing data
        parsed_data = []
        for i in range(len(data[0])):
            # If user left cell blank
            if data[0][i] == []:
                continue
            # Parse data as list of tuples
            parsed_data.append(tuple((data[0][i][0], data[1][i][0])))

        # Adding "Daily available" as last item to return
        parsed_data.append(data[2][0][0])

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
        data = pref_sheet.batch_get(['E25', 'B4:B43', 'C4:C43', 'H4:H23'])

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
        """Insert new row with expense or income record data to
        transactions list in Google Sheet.

        Args:
            data (list): parsed data for inserting in user's sheet.
        """
        # Appending formula which calculates amounts to main currency
        data.append(formulas.to_main_currency)

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_row(data, index=2, value_input_option='USER_ENTERED')
        return

    def add_transaction(self, data: list):
        """Insert new row with transaction record data to
        transactions list in Google Sheet.

        Args:
            data (list): parsed data for inserting in user's sheet.
        """

        # Preparing transaction data as two records with
        # outcome record and income record
        outcome_tran = [data[0], '', 'Transaction', data[1], data[2]]
        income_tran = [data[0], '', 'Transaction', data[3], data[4]]

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_rows([income_tran, outcome_tran], row=2, value_input_option='USER_ENTERED')
        return

sh = Sheet('1DfLa0vry-8YJVZgdkPDPcQEI6vYm19n2ddTBPNWo7K8')
sh.get_account_amounts()

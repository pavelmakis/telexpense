"""
This module is used for working with user's Google Sheet. 
It contains all functions that writes and reads data in sheet.
"""
import os
from copy import deepcopy

import gspread
from gspread import exceptions


class Sheet:
    account = gspread.service_account(
        filename=os.path.join(os.path.dirname(__file__), "token.json")
    )

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
            data = pref_sheet.batch_get(["B2", "E15", "H2"])
        except exceptions.APIError:
            return False

        # Check cells values
        if data != [[["Categories"]], [["Currency"]], [["Accounts"]]]:
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
        data = pref_sheet.batch_get(["E25", "H4:H23"])

        # Parsing data
        parsed_data, accounts = {}, []

        # Added today date to dictionary
        parsed_data["today"] = data[0][0][0]

        for i in range(len(data[1])):
            # If user left cell blank
            if data[1][i] == []:
                continue
            # Parse data as account list
            accounts.append(data[1][i][0])

        # Adding list of accounts to dictionary
        parsed_data["accounts"] = accounts

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
        data = main_sheet.batch_get(["N7:N26", "O7:O26", "N3"])

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

        Returns:
            dict: all the data needed for parsing expense or income as dictionary of lists
        """
        # Dictionary with data
        # It will contain today date, outcome categories, income categories
        # and account lists
        parsed_data = {}

        # Getting all data from specified ranges as lists
        pref_sheet = self.user_sheet.worksheet("Preferences")
        data = pref_sheet.batch_get(["E25", "B4:B43", "C4:C43", "H4:H23"])

        # Writing date to dictionary
        parsed_data["today"] = data[0][0][0]

        # Parsing outcome categories from list os lists to dictionary
        outcome_categories = []
        for i in range(len(data[1])):
            # If user left blank cell in category column
            if data[1][i] == []:
                continue
            outcome_categories.append(data[1][i][0])
        # Writing outcome categories to dictionary
        parsed_data["outcome categories"] = outcome_categories

        # Parsing income categories from list os lists to dictionary
        income_categories = []
        for i in range(len(data[2])):
            # If user left blank cell in category column
            if data[2][i] == []:
                continue
            income_categories.append(data[2][i][0])
        # Writing income categories to dictionary
        parsed_data["income categories"] = income_categories

        # Parsing accounts from list os lists to dictionary
        accounts = []
        for i in range(len(data[3])):
            if data[3][i] == []:
                continue
            accounts.append(data[3][i][0])
        # Writing accounts to dictionary
        parsed_data["accounts"] = accounts

        return parsed_data

    def get_last_transaction_type(self) -> str | None:
        """Get type of last transaction in Transactions sheet in
        user's Google Sheet. Could be 'transfer', 'category' or None.

        Returns:
            str: 'transfer' or 'category' depending on last record
            in Transactions sheet
            None: if there is no records in Transactions sheet
        """
        trans_list = self.user_sheet.worksheet("Transactions")

        # Excepting APIError because there can be no data
        try:
            data = trans_list.get("C2:C3")
        except exceptions.APIError:
            return None

        # Check last transaction 'category' field
        if len(data) >= 2:
            # TODO: Add check for multilanguage
            if data[0][0] == "Transfer" or "Transaction":
                return "transfer"
            else:
                return "category"
        else:
            return "category"

    def add_record(self, data: list):
        """Insert new row with expense or income record data to
        transactions list in Google Sheet.

        Args:
            data (list): parsed data for inserting in user's sheet.
        """
        # Appending formula which calculates amounts to main currency
        data.append(to_main_currency_f)

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_row(data, index=2, value_input_option="USER_ENTERED")
        return

    def add_transaction(self, data: list):
        """Insert new row with transaction record data to
        transactions list in Google Sheet.

        Args:
            data (list): parsed data for inserting in user's sheet.
        """

        # Preparing transaction data as two records with
        # outcome record and income record
        outcome_tran = [data[0], "", "Transfer", data[1], data[2]]
        income_tran = [data[0], "", "Transfer", data[3], data[4]]

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_rows(
            [income_tran, outcome_tran], row=2, value_input_option="USER_ENTERED"
        )
        return

    def delete_last_transaction(self, transaction_type: str):
        """Delete last transaction record from user's Google Sheet.

        Args:
            transaction_type (str): 'category' to delete 1 row,
            'transfer' to delete 2 rows
        """
        trans_list = self.user_sheet.worksheet("Transactions")
        # If type is 'category' then delete 1 row
        if transaction_type == "category":
            trans_list.delete_row(2)
        # If type is 'transfer' then delete 2 rows
        elif transaction_type == "transfer":
            trans_list.delete_rows(2, 3)

        return

    def set_main_cur(self, currency: str):
        """Update cell with main currency type"""
        pref_sheet = self.user_sheet.worksheet("Preferences")
        pref_sheet.update("F16", currency)

    def set_main_cur_format(self, pattern: str):
        main_sheet_id = self.user_sheet.worksheet("Main").id

        sheet_ranges = [
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 2,
                "endRowIndex": 3,
                "startColumnIndex": 1,
                "endColumnIndex": 3,
            },
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 2,
                "endRowIndex": 3,
                "startColumnIndex": 5,
                "endColumnIndex": 7,
            },
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 2,
                "endRowIndex": 3,
                "startColumnIndex": 9,
                "endColumnIndex": 11,
            },
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 2,
                "endRowIndex": 3,
                "startColumnIndex": 13,
                "endColumnIndex": 15,
            },
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 6,
                "endRowIndex": 7,
                "startColumnIndex": 9,
                "endColumnIndex": 11,
            },
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 10,
                "endRowIndex": 11,
                "startColumnIndex": 9,
                "endColumnIndex": 11,
            },
            {
                "sheetId": main_sheet_id,
                "startRowIndex": 6,
                "endRowIndex": 26,
                "startColumnIndex": 15,
                "endColumnIndex": 16,
            },
        ]

        dry_request = {
            "repeatCell": {
                "range": {},
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "CURRENCY",
                            "pattern": f"{pattern}",
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        }

        requests = []

        for i in range(len(sheet_ranges)):
            # Copying request template
            req_cp = deepcopy(dry_request)

            # Editing range and appending
            req_cp["repeatCell"]["range"] = sheet_ranges[i]
            requests.append(req_cp)

        self.user_sheet.batch_update({"requests": requests})


to_main_currency_f = '=D2*IFNA(GOOGLEFINANCE("CURRENCY:"&IFS(E2 = Preferences!$H$4; \
Preferences!$J$4; E2 = Preferences!$H$5; Preferences!$J$5; E2 = Preferences!$H$6; \
Preferences!$J$6; E2 = Preferences!$H$7; Preferences!$J$7; E2 = Preferences!$H$8; \
Preferences!$J$8; E2 = Preferences!$H$9; Preferences!$J$9; E2 = Preferences!$H$10; \
Preferences!$J$10; E2 = Preferences!$H$11; Preferences!$J$11; E2 = Preferences!$H$12; \
Preferences!$J$12; E2 = Preferences!$H$13; Preferences!$J$13; E2 = Preferences!$H$14; \
Preferences!$J$14; E2 = Preferences!$H$15; Preferences!$J$15; E2 = Preferences!$H$16; \
Preferences!$J$16; E2 = Preferences!$H$17; Preferences!$J$17; E2 = Preferences!$H$18; \
Preferences!$J$18; E2 = Preferences!$H$19; Preferences!$J$19; E2 = Preferences!$H$20; \
Preferences!$J$20; E2 = Preferences!$H$21; Preferences!$J$21; E2 = Preferences!$H$22; \
Preferences!$J$22)&Preferences!$F$16); 1)'

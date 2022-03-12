import gspread

class Sheet:
    def __init__(self) -> None:
        self.gspread_client = gspread.service_account(filename="token.json")
        self.user_sheet = self.gspread_client.open_by_url('https://docs.google.com/spreadsheets/d/1DfLa0vry-8YJVZgdkPDPcQEI6vYm19n2ddTBPNWo7K8')

    def get_available(self):
        main_sheet = self.user_sheet.worksheet("Main")
        available_amount = main_sheet.acell('B3').value
        return available_amount
    
    def get_savings(self):
        main_sheet = self.user_sheet.worksheet("Main")
        savings_amount = main_sheet.acell('B7').value
        return savings_amount
    
    def get_total(self):
        main_sheet = self.user_sheet.worksheet("Main")
        total_amount = main_sheet.acell('B11').value
        return total_amount

    def get_outcome_categories(self) -> list:
        """Get user's outcome categories from preferences list in Google sheet."""
        pref_list = self.user_sheet.worksheet("Preferences")
        category_list = pref_list.col_values(2)
        if category_list == []:
            return category_list
        # Delete column headers
        del category_list[:3]
        for i in range(len(category_list)):
            category_list[i] = category_list[i].lower().strip()
        return category_list
    
    def get_income_categories(self) -> list:
        """Get user's income categories from preferences list in Google sheet"""
        pref_list = self.user_sheet.worksheet("Preferences")
        category_list = pref_list.col_values(3)
        if category_list == []:
            return category_list
        # Delete column headers
        del category_list[:3]
        for i in range(len(category_list)):
            category_list[i] = category_list[i].lower().strip()
        return category_list

    def get_accounts(self) -> list:
        """Get all user accounts from preferences list in Google sheet"""
        pref_list = self.user_sheet.worksheet("Preferences")
        account_list = pref_list.col_values(8)
        if account_list == []:
            return account_list
        # Delete column headers
        del account_list[:3]
        for i in range(len(account_list)):
            account_list[i] = account_list[i].lower().strip()
        return account_list

    def get_today(self) -> str | None:
        """Get today date from cell in users Google sheet.

        Returns:
            str: today date from users sheet.
        """
        pref_list = self.user_sheet.worksheet("Preferences")
        today_date = pref_list.acell('E25').value
        return today_date

    def add_expense(self, data: list):
        # Getting transactions day and appending it 
        today = self.get_today()
        data.insert(0, today)

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_row(data, index=2, value_input_option='USER_ENTERED')
        return


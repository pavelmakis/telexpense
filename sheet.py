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

    def get_categories(self) -> list:
        """Get all user categories from preferences list in Google sheet"""
        pref_list = self.user_sheet.worksheet("Preferences")
        category_list = pref_list.col_values(2)
        if category_list == []:
            return category_list
        category_list.pop(0)
        for i in range(len(category_list)):
            category_list[i] = category_list[i].lower().strip()
        return category_list

    def get_accounts(self) -> list:
        """Get all user accounts from preferences list in Google sheet"""
        pref_list = self.user_sheet.worksheet("Preferences")
        account_list = pref_list.col_values(1)
        if account_list == []:
            return account_list
        account_list.pop(0)
        for i in range(len(account_list)):
            account_list[i] = account_list[i].lower().strip()
        return account_list

    def get_accounts_and_categories(self) -> tuple():
        pref_list = self.user_sheet.worksheet("Preferences")
        account_list = pref_list.col_values(8)
        category_list = pref_list.col_values(2)

        return


    def get_today(self) -> str:
        """Get today date from cell in users Google sheet"""
        pref_list = self.user_sheet.worksheet("Preferences")
        today_date = pref_list.acell('N3').value
        return today_date

    def add_expense(self, data: list):
        # Getting transactions day and appending it 
        today = self.get_today()
        data.insert(0, today)

        # Opening transactions sheet and inserting transaction data
        trans_list = self.user_sheet.worksheet("Transactions")
        trans_list.insert_row(data, index=2, value_input_option='RAW')
        return


user_sheet = Sheet()

print(user_sheet.get_accounts())
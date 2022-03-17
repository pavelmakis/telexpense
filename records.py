import sheet

def _parse_outcome_amount(amount: str) -> float | None:
    if amount[0] == '+' or amount[0] == '-':
        amount = amount[1:]
    amount = '-' + amount
    try: float(amount)
    except ValueError: return None
    return float(amount)

def _parse_income_amount(amount: str) -> float | None:
    if amount[0] == '-':
        amount = amount[1:]
    try: float(amount)
    except ValueError: return None
    return float(amount)

def _parse_account(account: str, user_sheet: sheet.Sheet) -> str | None:
    account_list = user_sheet.get_accounts()
    for i in range(len(account_list)):
        if account.lower() == account_list[i].lower():
            account = account_list[i]
            return account
    return None

def _parse_outcome_category(category: str, user_sheet: sheet.Sheet) -> str | None:
    category_list = user_sheet.get_outcome_categories()
    for i in range(len(category_list)):
        if category.lower() == category_list[i].lower():
            category = category_list[i]
            return category
    return None

def _parse_income_category(category: str, user_sheet: sheet.Sheet) -> str | None:
    category_list = user_sheet.get_income_categories()
    for i in range(len(category_list)):
        if category.lower() == category_list[i].lower():
            category = category_list[i]
            return category
    return None

def parse_record(raw_record: list, type: str) -> list | None:
    for arg in range(len(raw_record)):
        raw_record[arg] = raw_record[arg].strip()

    parsed_data = []
    user_sheet = sheet.Sheet()
    match raw_record:
        case amount, category, account, description:
            if type == 'income':
                amount = _parse_income_amount(amount)
                category = _parse_income_category(category, user_sheet)
            else:
                amount = _parse_outcome_amount(amount)
                category = _parse_outcome_category(category, user_sheet)
            account = _parse_account(account, user_sheet)
            parsed_data = [description, category, amount, account]

        case amount, category, account:
            if type == 'income':
                amount = _parse_income_amount(amount)
                category = _parse_income_category(category, user_sheet)
            elif type == 'outcome':
                amount = _parse_outcome_amount(amount)
                category = _parse_outcome_category(category, user_sheet)
            account = _parse_account(account, user_sheet)
            parsed_data = ['', category, amount, account]
        
        case amount, category:
            if type == 'income':
                amount = _parse_income_amount(amount)
                category = _parse_income_category(category, user_sheet)
            else:
                amount = _parse_outcome_amount(amount)
                category = _parse_outcome_category(category, user_sheet)
            parsed_data = ['', category, amount, '']
    return parsed_data

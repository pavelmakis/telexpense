import sheet

def _parse_amount(amount: str) -> bool:
    try: float(amount)
    except ValueError: return None
    return float(amount)

def _parse_account(account: str, user_sheet: sheet.Sheet) -> str | None:
    account_list = user_sheet.get_accounts()
    for i in range(len(account_list)):
        if account.lower() in account_list[i].lower():
            account = account_list[i]
            return account
    return None

def _parse_category(category: str, user_sheet: sheet.Sheet) -> str | None:
    category_list = user_sheet.get_income_categories()
    category_list.extend(user_sheet.get_outcome_categories())
    for i in range(len(category_list)):
        if category.lower() in category_list[i].lower():
            category = category_list[i]
            return category
    return None

def parse_transaction(raw_transaction: list) -> list | None:
    for arg in range(len(raw_transaction)):
        raw_transaction[arg] = raw_transaction[arg].strip()

    parsed_data = []
    user_sheet = sheet.Sheet()
    match raw_transaction:
        case amount, category, account, description:
            user_sheet = sheet.Sheet()
            amount = _parse_amount(amount=amount)
            category = _parse_category(category=category, user_sheet=user_sheet)
            account = _parse_account(account=account, user_sheet=user_sheet)
            parsed_data = [description, category, amount, account]

        case amount, category, account:
            user_sheet = sheet.Sheet()
            amount = _parse_amount(amount=amount)
            category = _parse_category(category=category, user_sheet=user_sheet)
            account = _parse_account(account=account, user_sheet=user_sheet)
            parsed_data = ['', category, amount, account]
        
        case amount, category:
            user_sheet = sheet.Sheet()
            amount = _parse_amount(amount=amount)
            category = _parse_category(category=category, user_sheet=user_sheet)
            account = _parse_account(account=account, user_sheet=user_sheet)
            parsed_data = ['', category, amount, '']
    return parsed_data

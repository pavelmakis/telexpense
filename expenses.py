import sheet

def _parse_amount(amount: str) -> bool:
    try: float(amount)
    except ValueError: return False
    return True

def parse_expension(raw_expension: list) -> list | None:
    for arg in range(len(raw_expension)):
        raw_expension[arg] = raw_expension[arg].strip()

    parsed_data = []
    match raw_expension:
        case amount, category, account, description:
            if not _parse_amount(amount):
                amount = None
            user_sheet = sheet.Sheet()
            if not category.lower() in user_sheet.get_outcome_categories():
                category = None
            if not account.lower() in user_sheet.get_accounts():
                account = None
            parsed_data = [description, category, amount, account]

        case amount, category, account:
            if not _parse_amount(amount):
                amount = None
            user_sheet = sheet.Sheet()
            if not category.lower() in user_sheet.get_outcome_categories():
                category = None
            if not account.lower() in user_sheet.get_accounts():
                account = None
            parsed_data = ['', category, amount, account]
        
        case amount, category:
            if not _parse_amount(amount):
                amount = None
            user_sheet = sheet.Sheet()
            if not category.lower() in user_sheet.get_outcome_categories():
                category = None
            parsed_data = ['', category, amount, '']
    return parsed_data


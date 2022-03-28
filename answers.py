help = """
I can help you send and receive data from the table. 
If this is your first time here, read this wiki.\n
I can understand theese commands:\n
*Add records*
/expense (➖Expense) - add new expense
/income (➕Income) - add new income
/transaction (💱Transaction) - add new transaction
/addexp - add expense in a single message
/addinc - add income in a single message
/addtran - add transaction in a single message
"""

expense_help = """
Expense can be added by:
    `/addexp amount, category, [account], [description]`
where account and description are optional.

Example:
    `/addexp 3.45, taxi, Revolut, From work`
    `/addexp 9.87, Groceries, N26`
"""

wrong_expense = """
Cannot understand this expense!

Expense can be added by:
    `/addexp amount, category, [account], [description]`
where account and description are optional.

Example:
    `/addexp 3.45, taxi, Revolut, From work`
    `/addexp 9.87, Groceries, N26`
"""

income_help = """
Income can be added by:
    `/addinc amount, category, [account], [description]`
where account and description are optional.

Example:
    `/addinc 1200, Salary, N26, First job`
    `/addinc 20.20, Cashback, Revolut`
"""

wrong_income = """
Cannot understand this income!

Income can be added by:
    `/addinc amount, category, [account], [description]`
where account and description are optional.

Example:
    `/addinc 1200, Salary, N26, First job`
    `/addinc 20.20, Cashback, Revolut`
"""

tran_help = """
Transaction can be added by:
    `/addtran outcome_amount, outcome\\_account, [income\\_amount], income\\_account`
where income amount is optional\\. Add it if your transaction is multicurrency\\.

Example:
    `/addtran 1200, Revolut, N26`
    `/addtran 200, Revolut EUR, 220.3, Revolut USD`
"""

wrong_tran = """
Cannot understand this transaction\\!

Transaction can be added by:
    `/addtran outcome\\_amount, outcome\\_account, [income\\_amount], income\\_account`
where income\\_amount is optional\\. Add it if your transaction is multicurrency\\.

Example:
    `/addtran 1200, Revolut, N26`
    `/addtran 200, Revolut EUR, 220.3, Revolut USD`
"""
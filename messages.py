TEMPLATE_SHEET_LINK = "https://docs.google.com/spreadsheets/\
d/1lO9oTJu3CudibuQCCqk-s1t3DSuRNRoty4SLY5UvG_w"

BOT_SERVICE_EMAIL = "telexpense-bot@telexpense-bot.iam.gserviceaccount.com"

BOT_WIKI = "https://github.com/pavelmakis/telexpense/wiki"

start_message = "Hi! I'm Telexpense bot 📺\n\n\
I can help you manage your finances in Google Sheet.\n\
If you are a new user, read the [wiki]({wiki}) \
or type /register to start using me".format(
    wiki=BOT_WIKI
)

help = "I can help you manage your finances in Google Sheet.\n\n\
If you don't understand something, check out [this wiki]({wiki})\n\n\
I can understand these commands:\n\n\
*Add records*\n\
/expense (➖Expense) - add new expense\n\
/income (➕Income) - add new income\n\
/transfer (💱Transfer) - add new transfer\n\
/cancel - cancel record filling\n\
/addexp - add expense in a single message\n\
/addinc - add income in a single message\n\
/addtran - add transaction in a single message\n\n\
*Show balance*\n\
/available (💲Available) - show your accounts balances\n\n\
*Revert changes*\n\
/undo - delete last transaction from Google Sheet\n\n\
*Settings*\n\
/currency - set main currency and its format\n\
/language - set bot's language\n\
/register - connect me to Google Sheet or change connected sheet\n\n\
*Other*\n\
/donate - sponsor this project".format(
    wiki=BOT_WIKI
)

for_inregistered = "I can only work with registered users!\n\
Read the [wiki]({wiki}) or type /register".format(
    wiki=BOT_WIKI
)

cmd_cancel = "Can cancel only while filling a form.\n\n\
Nothing to cancel now!"

error_message = "😳 Something went wrong...\n\n\
Please try again later.\n\
If it does not work again, check your table or add it again via /register. \
Maybe you have changed the table and I can no longer work with it"

expense_help = "Expense can be added by:\n\
    `/addexp amount, category, [account], [description]`\n\
where account and description are optional.\n\n\
Example:\n\
    `/addexp 3.45, taxi, Revolut, From work`\n\
    `/addexp 9.87, Groceries, N26`"

wrong_expense = "Cannot understand this expense!\n\n\
Expense can be added by:\n\
    `/addexp amount, category, [account], [description]`\n\
where account and description are optional.\n\n\
Example:\n\
    `/addexp 3.45, taxi, Revolut, From work`\n\
    `/addexp 9.87, Groceries, N26`"

income_help = "Income can be added by:\n\
    `/addinc amount, category, [account], [description]`\n\
where account and description are optional.\n\n\
Example:\n\
    `/addinc 1200, Salary, N26, First job`\n\
    `/addinc 20.20, Cashback, Revolut`"

wrong_income = "Cannot understand this income!\n\n\
Income can be added by:\n\
    `/addinc amount, category, [account], [description]`\n\
where account and description are optional.\n\n\
Example:\n\
    `/addinc 1200, Salary, N26, First job`\n\
    `/addinc 20.20, Cashback, Revolut`"

tran_help = "Transfer can be added by:\n\
    `/addtran outcome_amount, outcome\\_account, [income\\_amount], income\\_account`\n\
where income amount is optional\\. Add it if your transaction is multicurrency\\.\n\n\
Example:\n\
    `/addtran 1200, Revolut, N26`\n\
    `/addtran 200, Revolut EUR, 220.3, Revolut USD`"

wrong_tran = "Cannot understand this transaction\\!\n\n\
Transfer can be added by:\n\
    `/addtran outcome\\_amount, outcome\\_account, [income\\_amount], income\\_account`\n\
where income\\_amount is optional\\. Add it if your transaction is multicurrency\\.\n\n\
Example:\n\
    `/addtran 1200, Revolut, N26`\n\
    `/addtran 200, Revolut EUR, 220.3, Revolut USD`\n"

donate_mes = 'The minimum amount is 3€.\n\n\
If you want to donate a different amount, \
tap "Pay" and enter the amount of the tip, \
which will be added to the minimum amount'

donate_description = "This is a voluntary donation to my creator."

russia_donate_message = "To transfer money tap the first button, \
you will be redirected to the payment page"

successfull_payment = "*🙏 Thank you for supporting my creator for \
{total_amount} {currency}!*\n\n🤔 Maybe now he can come \
up with even more functionality for me"


# Registration
reg_start_registered = "You are already registered user!\n\n\
You can either connect me to a new Google Sheet or delete \
a connected sheet from the database"

reg_start_unregistered = "Looks like you are new here...\n\n\
If you want to use me, connect me to new Google Sheet"

reg_step_1 = "*STEP 1*\n\n\
Copy this Google Sheet template to your Google account. \
You do this to ensure that your financial data belongs only to you.\n\n \
👉 [Telexpense Template Sheet]({sheet}) 👈".format(
    sheet=TEMPLATE_SHEET_LINK
)

reg_step_2 = "*STEP 2*\n\n\
Add me to the table as an editor so I can add transactions \
and read the balance. Here is my email:\n\n\
{email}".format(
    email=BOT_SERVICE_EMAIL
)

reg_step_3 = "*STEP 3*\n\n\
Copy the link to the table in your account and send it to this chat. \
It is necessary for me to remember you"

reg_success = "Great, you are in!\n\n\
Don't forget to select the main currency and its format in /currency \
and set bots language in /language"

reg_update_success = "Your sheet successfully changed!\n\n\
Don't forget to select the main currency and its format in /currency \
and set bots language in /language"

reg_forget_warning = "Are you sure? After that you have to /register again to use me"

reg_wrong_link = "Hm. Looks like it's not a link I'm looking for...\n\n\
Read the [wiki]({wiki}) and try to /register one more time!".format(
    wiki=BOT_WIKI
)


# Currency
ask_currency = "What is the main currency of your finances?\n\n\
If your currency is not in the list, unfortunately, you will have \
to adjust the currency and format manually in the table"

wrong_currency = "😥 Sorry, this currency cannot be set up through me yet.\n\n\
You can do this manually on the Preferences page in your sheet."

ask_format = "Please select a currency format that suits you best"

wrong_pattern = "😳 Sorry, I cannot understand this format.\n\n\
Change something and try /currency again later"

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

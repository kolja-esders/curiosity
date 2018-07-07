from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from lake.models import BankTransaction
from lake.lib.log import Log
from hashlib import sha256
from datetime import datetime
import os

class BankClient:
    ME = 'BankClient'
    LOGIN_URL = 'https://banking.fidor.de/login'
    client = None

    def __init__(self):
        self.fidor_password = os.environ['FIDOR_PASSWORD']
        self.fidor_email = os.environ['FIDOR_EMAIL']

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('no-sandbox')

        try:
            self.client = webdriver.Chrome(chrome_options=options)
            Log.debug(self.ME, 'Launched new chromedriver instance.')
        except Exception as e:
            Log.fatal(self.ME, 'Unable to create chrome client: {}'.format(e))

    def login(self):
        self.client.get(self.LOGIN_URL)
        self.handle_credentials()

    def handle_credentials(self):
        USERNAME_ID = 'user_email'
        PASSWORD_ID = 'user_password'
        SUBMIT_BTN_ID = 'login'

        try:
            element = WebDriverWait(self.client, 10).until(
                EC.presence_of_element_located((By.ID, USERNAME_ID)))
        except:
            print('Unable to locate username element.')
            return False

        username = self.client.find_element_by_id(USERNAME_ID)
        password = self.client.find_element_by_id(PASSWORD_ID)
        btn = self.client.find_element_by_id(SUBMIT_BTN_ID)

        username.send_keys(self.fidor_email)
        password.send_keys(self.fidor_password)
        btn.click()

        return True

    def fetch_most_recent_transaction(self):
        """ Import old transactions from the bank account. """
        TRANSACTIONS_URL = 'https://banking.fidor.de/smart-account/transactions'
        self.client.get(TRANSACTIONS_URL)

        transactions = self.client.find_elements_by_css_selector('#booked-transactions tbody tr')
        if transactions:
            t = transactions[0]
            cols = t.find_elements_by_tag_name('td')
            try:
                date = datetime.strptime(cols[0].text, '%d.%m.%Y')
                desc = cols[1].text
                amount = float(cols[2].text.strip("€").replace('.', '').replace(',', '.'))
                balance = float(cols[3].text.strip('€').replace('.', '').replace(',', '.'))
                unique = sha256('{}-{}-{}-{}'.format(date, desc, amount, balance).encode('utf-8')).hexdigest()
                result = BankTransaction.objects.filter(unique=unique)
                if result:
                    return

                # Look for open transactions that can be closed.
                open_transaction = BankTransaction.objects.filter(amount=amount, finished=False).first()
                if open_transaction:
                    open_transaction.arrived_at = date
                    open_transaction.desc = desc
                    open_transaction.unique = unique
                    open_transaction.finished = True
                    open_transaction.new_balance = balance
                    open_transaction.save()
                    Log.info(self.ME, 'A pending SEPA transaction of {} € just arrived. New balance: {} €.'.format(open_transaction.amount, open_transaction.new_balance))
                else:
                    BankTransaction.objects.create(finished=True, arrived_on=date, desc=desc, amount=amount, new_balance=balance, unique=unique)
                    Log.info(self.ME, 'An unexpected SEPA transaction of {} € just arrived. New balance: {} €.'.format(amount, balance))
            except Exception as e:
                Log.warn(self.ME, 'Unable to store new SEPA transaction: {}'.format(e))

    def update_transactions(self):
        """ Keeps turn overs up-to-date """
        TRANSACTIONS_URL = 'https://banking.fidor.de/smart-account/transactions'
        self.client.get(TRANSACTIONS_URL)

        transactions = self.client.find_elements_by_css_selector('#booked-transactions tbody tr')
        new_transactions = []
        for t in transactions:
            cols = t.find_elements_by_tag_name('td')
            try:
                date = datetime.strptime(cols[0].text, '%d.%m.%Y')
                desc = cols[1].text
                amount = float(cols[2].text.strip("€").replace('.', '').replace(',', '.'))
                balance = float(cols[3].text.strip('€').replace('.', '').replace(',', '.'))
                unique = sha256('{}-{}-{}-{}'.format(date, desc, amount, balance).encode('utf-8')).hexdigest()
                result = BankTransaction.objects.filter(unique=unique)
                if result:
                    break

                # Look for open transactions that can be closed
                open_transaction = BankTransaction.objects.filter(amount=amount, finished=False).first()
                if open_transaction:
                    open_transaction.arrived_at = date
                    open_transaction.desc = desc
                    open_transaction.unique = unique
                    open_transaction.finished = True
                    open_transaction.new_balance = balance
                    open_transaction.save()
                    Log.info(self.ME, 'A pending SEPA transaction of {} € just arrived. New balance: {} €.'.format(open_transaction.amount, open_transaction.new_balance))
                else:
                    new_transactions.append(BankTransaction(finished=True, arrived_on=date, desc=desc, amount=amount, new_balance=balance, unique=unique))
            except Exception as e:
                Log.warn(self.ME, 'Unable to store new SEPA transaction: {}'.format(e))

        for t in reversed(new_transactions):
            Log.info(self.ME, 'An unexpected SEPA transaction of {} € just arrived. New balance: {} €.'.format(t.amount, t.new_balance))
            t.save()

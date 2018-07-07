from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from lake.models import Rate, AskPrice, YubiKey
import os

class BitcoinClient:
    LOGIN_URL = 'https://www.bitcoin.de/de/login'
    client = None

    def __init__(self):
        self.email = os.environ['BITCOIN_DE_EMAIL']
        self.password = os.environ['BITCOIN_DE_PASSWORD']

        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        try:
            self.client = webdriver.Chrome()
        except:
            print('Unable to create chrome client.')

    def login(self):
        self.client.get(self.LOGIN_URL)
        self.handle_credentials()
        self.handle_otp()

    def handle_credentials(self):
        USERNAME_ID = 'login_username'
        PASSWORD_ID = 'login_password'
        SUBMIT_BTN_ID = 'signin_button'

        try:
            element = WebDriverWait(self.client, 10).until(
                EC.presence_of_element_located((By.ID, USERNAME_ID)))
        except:
            print('Unable to locate username element.')
            return False

        username = self.client.find_element_by_id(USERNAME_ID)
        password = self.client.find_element_by_id(PASSWORD_ID)
        btn = self.client.find_element_by_id(SUBMIT_BTN_ID)

        username.send_keys(self.email)
        password.send_keys(self.password)
        btn.click()

        return True

    def handle_otp(self):
        # wait until otp input is located
        otp = self.get_otp()
        otp_input = self.client.find_element_by_id('login_otp_otp')
        otp_input.send_keys(otp.value)

        # Send OTP
        btn = self.client.find_element_by_id('signin_button')
        btn.click()

        # Invalidate otp
        self.mark_otp_as_used(otp)

    def mark_otp_as_used(self, otp):
        otp.used = True
        otp.save()

    def get_otp(self):
        val = None
        try:
            val = YubiKey.objects.filter(used=False)[0]
        except IndexError:
            print('No more YubiKeys available.')

        return val

    def open_marketplace(self):
        MARKETPLACE_URL = 'https://www.bitcoin.de/de/btceur/market'
        self.client.get(MARKETPLACE_URL)

    def buy(self, amount):
        ASKS_CONTAINER_ID = 'box_buy_sell_offer'

        self.open_marketplace()
        asks_container = self.client.find_element_by_id(ASKS_CONTAINER_ID)

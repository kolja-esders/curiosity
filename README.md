# Curiosity

## Overview

Arbitrage opportunity tracker between bitcoin.de (buy) and gdax.com (sell).

### Features
- Supports ETH/EUR and BTC/EUR trading pairs
- [Chasqui](https://en.wikipedia.org/wiki/Chasqui): Rate fetching every minute
- [Medici](https://en.wikipedia.org/wiki/House_of_Medici): Track account balance on bitcoin.de
- Email notifications (based on profit threshold)
- Calculate potential profit (accounts for exchange and tx fees)


## Install

```
# Install dependencies
pip3 install -r requirements.txt

# Setup AWS SES (if needed)

# Set environment variables (see below)
export GDAX_KEY='<your-key>'
...

# Start rate fetching service
python3 manage.py chasqui &

# Start account balance tracking service
python3 manage.py medici &

# Start web interface
python3 manage.py runserver 8080

# Take a look at http://localhost:8080
```

### Environment variables

#### Notifications

Email addresses that should be used for the notification service. The emails are send using AWS SES so make sure the addresses are validated accordingly. You should also ensure that your AWS SES credentials are stored in `~/.aws/credentials`.

- `NOTIFICATION_SENDER`
- `NOTIFICATION_RECIPIENT`

#### GDAX

API credentials in order to fetch rates from GDAX. Simply register for an API account and you're good to go.

- `GDAX_KEY`
- `GDAX_BASE64_SECRET`
- `GDAX_PASSPHRASE`

#### Fidor

Credentials of the Fidor bank account that is associated with the bitcoin.de account. Allows for regular updates of the currently available balance that can be used for arbitrage.

It should be noted that Fidor also has an API service. Unfortunately, the API is not for free.
- `FIDOR_EMAIL`
- `FIDOR_PASSWORD`

## Screenshots

### Live rates
<img src="https://user-images.githubusercontent.com/5159563/35456280-35872aa2-02d5-11e8-95aa-b1f5c4c222af.png">

### Lifetime plots
<img src="https://user-images.githubusercontent.com/5159563/35456279-356aaa1c-02d5-11e8-8ebc-01cb1baa9f82.png">

### Email notifications
<img src="https://user-images.githubusercontent.com/5159563/35456278-354d69c0-02d5-11e8-888e-9d5a623a9b6e.png">

### Logging & heart beat
<img src="https://user-images.githubusercontent.com/5159563/35456281-35a2d626-02d5-11e8-95fd-48b7c2fc76d3.png">

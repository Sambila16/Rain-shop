# Rain Shop

A web system for a shop that sells water, soft drinks, sweets and snacks. It handles products and stock, daily sales, regular customers and monthly profit reports, and it has a public homepage with a photo slideshow.

Built with Django (Python) and SQLite. No other software is needed.

## What it does

- **Homepage:** a public landing page with an automatic photo slideshow and a sign-in button.
- **Products:** add items with a picture, category, unit (bottle, crate, carton and so on), stock, buying price, selling price and expiry date.
- **Sell:** record a sale with payment method and customer location. Stock goes down automatically.
- **Customers:** keep a list of regular customers with phone numbers and locations.
- **Dashboard:** today's sales, low-stock items and items close to expiry.
- **Reports:** monthly sales and profit, split into capital and new profit.
- **Users:** the owner (staff) can open every page. Shopkeepers can only use the Sell page.

## Requirements

- Python 3.10 or newer (from python.org; tick "Add Python to PATH" when installing on Windows)

## First-time setup

Open a terminal in the project folder (the one that contains `manage.py`) and run these commands in order.

1. Create a virtual environment and activate it.
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - macOS or Linux: `python3 -m venv venv` then `source venv/bin/activate`
2. Install the requirements: `pip install -r requirements.txt`
3. Create the database: `python manage.py migrate`
4. Add the starting categories: `python manage.py seed`
5. Create the owner account: `python manage.py createsuperuser`
   (type a username, press Enter to skip the email, then choose a password; it stays invisible while you type)
6. Start the site: `python manage.py runserver`
7. Open http://127.0.0.1:8000 in your browser.

## Starting it again later

Open a terminal in the project folder, activate the virtual environment (step 1), then run `python manage.py runserver`. Stop the server with `Ctrl + C`.

## Using the shop

1. Sign in with the owner account.
2. Open **Admin** to set up categories and units, and to create shopkeeper accounts.
3. Open **Products** and add your items with prices and stock.
4. Shopkeepers sign in and use **Sell** for each sale.
5. At the end of the month, open **Reports**.

Django's built-in admin is also available at http://127.0.0.1:8000/django-admin/ for the owner account.

## Changing the homepage photos

The slideshow photos are in `shop/static/img/` (the main photo) and `shop/static/img/slides/`. To change a photo, replace the file or edit its path in `shop/templates/index.html`. Photos that are taller than wide work best. The caption on each slide is in the same file.

## Project layout

- `coolshop/`: project settings and main URLs
- `shop/models.py`: products, categories, units, customers and sales
- `shop/views.py`: the pages and their logic
- `shop/templates/`: the HTML pages
- `shop/static/`: styles, logo and photos
- `db.sqlite3`: your data (created by `migrate`; back this file up regularly)

## Before putting it online

The settings are for development. Before deploying, change `SECRET_KEY`, set `DEBUG = False`, set `ALLOWED_HOSTS` to your domain, and serve static and media files from your host.

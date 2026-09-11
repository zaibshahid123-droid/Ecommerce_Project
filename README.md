# Mongo CRUD (Django + MongoDB)

A minimal Django project that does basic **Create / Read / Update / Delete**
on an `Item` collection stored in **MongoDB**, using
[MongoEngine](https://mongoengine.org/) as the ODM.

- Django's built-in auth/admin/sessions still use SQLite (they expect a
  relational DB) — that's normal and doesn't touch your Mongo data.
- The actual `items` app talks to MongoDB directly via MongoEngine.

## Project layout

```
mongo_crud_project/
├── manage.py
├── requirements.txt
├── mongo_crud_project/      # Django project settings/urls
│   ├── settings.py          # MongoEngine connection lives at the bottom
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── items/                   # The CRUD app
    ├── models.py            # MongoEngine Document (Item)
    ├── views.py             # list / create / update / delete views
    ├── urls.py
    └── templates/items/     # Simple server-rendered HTML
```

## Quick start on Windows 10

Double-click **`run_windows.bat`** in this folder. It will:
1. Create a `venv` virtual environment (first run only)
2. Install everything in `requirements.txt`
3. Run Django's `migrate` (for the SQLite auth/admin tables)
4. Remind you to have MongoDB running, then start the server and open
   `http://127.0.0.1:8000/` in your browser automatically

Requirements: Python 3.10+ installed and on PATH, and MongoDB reachable
(local `mongod`, Docker, or Atlas — see step 3 below).

## 1. Open in PyCharm

1. `File > Open...` and select the `mongo_crud_project` folder.
2. PyCharm should detect it as a Django project. If prompted, set the
   Django project root to this folder and settings module to
   `mongo_crud_project.settings`.

## 2. Create a virtual environment & install dependencies

In PyCharm's terminal (or Settings > Project > Python Interpreter > Add):

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Have MongoDB running

- Local install: make sure `mongod` is running on `localhost:27017`
  (default), **or**
- Use Docker: `docker run -d -p 27017:27017 --name mongo mongo:7`, **or**
- Use MongoDB Atlas and grab your connection string.

By default the app connects to:

```
mongodb://localhost:27017/mongo_crud_db
```

To point at a different DB (e.g. Atlas), set an environment variable
before running the server:

```bash
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/mydb"
```

(In PyCharm: Run/Debug Configurations > Environment variables.)

## 4. Run migrations (for Django's own auth/admin tables in SQLite)

```bash
python manage.py migrate
```

(This does **not** create anything in MongoDB — MongoEngine is schemaless
and creates the `items` collection automatically on first insert.)

## 5. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

## 6. Run the server

```bash
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** — you'll see the item list, with
links to create, edit, and delete items, all stored in MongoDB.

A ready-made "Run Server" PyCharm run configuration is included under
`.idea/runConfigurations/`.

## CRUD routes

| Action | URL                  | View            |
|--------|----------------------|------------------|
| List   | `/`                   | `item_list`      |
| Create | `/create/`            | `item_create`    |
| Update | `/<id>/update/`       | `item_update`    |
| Delete | `/<id>/delete/`       | `item_delete`    |

## Notes / next steps

- This uses plain HTML forms (no Django REST Framework) for simplicity.
  If you want a JSON API instead, swap the views for DRF + a MongoEngine
  serializer library (e.g. `django-rest-framework-mongoengine`).
- Add validation, pagination, or search as needed — `Item.objects` is a
  standard MongoEngine `QuerySet`, so `.filter(name__icontains="...")`
  etc. all work.

## Shopping cart & orders

The app is now a full storefront, not just a back-office CRUD:

- **Accounts**: signup now asks "customer" (auto-approved, can shop
  immediately) vs "staff" (needs owner approval, same as before).
  Owner accounts are still created manually (`createsuperuser` +
  setting `profile.role = 'owner'` / `is_approved = True` in the admin).
- **Special deals**: every item has an optional `discount_percent`
  (set from the item form). Items with a discount show a sale badge,
  strikethrough price, and the deal price everywhere (menu, cart,
  checkout, orders). `/?deals=1` shows only items on sale.
- **Cart**: `/cart/` — add from the menu with a quantity picker,
  change quantity or remove items on the cart page, stock is
  re-checked live (can't add/keep more than what's in stock). Stored
  per-user in a `carts` Mongo collection so it survives logout/login.
- **Checkout**: `/checkout/` — collects delivery details and payment
  method (Cash on Delivery / Card — no real payment gateway is wired
  up), re-validates stock, creates an `Order`, decrements item stock,
  and empties the cart.
- **Orders**: customers see their own history at `/orders/`; owners
  and employees see every order and can update its status
  (Pending → Processing → Shipped → Delivered, or Cancelled) at
  `/manage/orders/`.

### Migration

A new migration (`0003_profile_customer_role.py`) adds the `customer`
role to `Profile`. Run it the same way as before:

```bash
python manage.py migrate
```

### Security note

`settings.py` has a real MongoDB Atlas connection string (with
username/password) hardcoded as the fallback default for `MONGO_URI`.
Since this project has now been shared outside your machine, it's
worth rotating that database user's password in Atlas and setting
`MONGO_URI` as an actual environment variable instead of leaving
credentials in source.

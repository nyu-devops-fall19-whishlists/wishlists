# Wishlists
An API to allow management of wishlists for an e-commerce website. It will support create, read, update, delete, list, query, and an action.

A list of items a person wants to buy from a store.  A person can have multiple wish lists.

URL | Operation | Description
-- | -- | --
POST /wishlists | CREATE | Create new Wishlist
POST /wishlists/`<id>`/items | CREATE | Add item to Wishlist
DELETE /wishlists/`<id>` | DELETE | Delete Wishlist
DELETE /wishlists/`<id>`/items/`<itemid>` | DELETE | Delete item from Wishlist
PUT /wishlists/`<id>` | UPDATE | Rename wishlist
GET /wishlists/`<id>`/items | READ | List items in wishlist [ordered chronologically]
GET /wishlists | LIST | Show all wishlists
GET /wishlists?q=querytext | QUERY | Search for a wishlist
GET /wishlists/`<id>`?q=querytext | QUERY | Search for items in wishlist
PUT /wishlists/`<id>`/items/`<itemid>`/add-to-cart | ACTION | Move an item from wishlist to the shopping cart

To execute the service run:

```
vagrant up --provision
vagrant ssh
cd /service
FLASK_APP=service:app flask run -h 0.0.0.0
```

Then open a browser session to http://0.0.0.0:5000/

# Wishlists
An API to allow management of wishlists for an e-commerce website. It will support create, read, update, delete, list, query, and an action.

A list of items a person wants to buy from a store.  A person can have multiple wish lists.

URL | Operation | Description
-- | -- | --
POST /wishlists | CREATE | Create new Wishlist
POST /wishlists/`<id>`/item | CREATE | Add item to Wishlist
DELETE /wishlists/`<id>` | DELETE | Delete Wishlist
DELETE / wishlists/`<id>`/items/`<itemid>` | DELETE | Delete item from Wishlist
PUT /wishlists/`<id>`/update | UPDATE | Rename wishlist
PUT /wishlists/`<id>`/items/`<itemid>` | ACTION | Move an item from wishlist   to the shopping cart
GET /wishlists/`<id>` | READ | List items in wishlist [ordered   chronologically]
GET /wishlists | LIST | Show all wishlists
GET /wishlists?q=querytext | QUERY | Search for a wishlist
GET /wishlist/`<id>`?q=querytext | QUERY | Search for items in   wishlist

# Wishlists
An API to allow management of wishlists for an e-commerce website. It will support create, read, update, delete, list, query, and an action.

A list of items a person wants to buy from a store.  A person can have multiple wish lists.

URL | Operation | Description
-- | -- | --
POST /wishlists | CREATE | Create new Wishlist
POST /wishlist/`<id>`/items | CREATE | Add item to Wishlist
DELETE /wishlist/`<id>` | DELETE | Delete Wishlist
DELETE / wishlist/`<id>`/item/`<itemid>` | DELETE | Delete item from Wishlist
PUT /wishlist/`<id>`/update | UPDATE | Rename wishlist
PUT /wishlist/`<id>`/item/`<itemid>` | ACTION | Move an item from wishlist   to the shopping cart
GET /wishlist/`<id>`/items | READ | List items in wishlist [ordered   chronologically]
GET /wishlists | LIST | Show all wishlists
GET /wishlists?q=querytext | QUERY | Search for a wishlist
GET /wishlist/`<id>`?q=querytext | QUERY | Search for items in   wishlist
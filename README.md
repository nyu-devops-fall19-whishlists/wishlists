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

## Prerequisite Installation using Vagrant VM

The easiest way to use this lab is with **Vagrant** and **VirtualBox**. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

```bash
    git clone https://github.com/nyu-devops-fall19-wishlists/wishlists.git
    cd wishlists
    vagrant up
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
```

## Alternate install using local Python

If you have Python 3 installed on your computer you can make a virtual environment and run the code locally with:

```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    FLASK_APP=service:app flask run
```

## Manually running the Tests

Run the tests using `nose`

```bash
    nosetests
```

**Nose** is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red. It also has `--with-coverage` specified so that code coverage is included in the tests.

The Code Coverage tool runs with `nosetests` so to see how well your test cases exercise your code just run the report:

```bash
    coverage report -m
```

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases.

To run the service use `flask run` (Press Ctrl+C to exit):

```bash
    FLASK_APP=service:app flask run -h 0.0.0.0
```

You must pass the parameters `-h 0.0.0.0` to have it listed on all network adapters to that the post can be forwarded by `vagrant` to your host computer so that you can open the web page in a local browser at: http://localhost:5000

When you are done, you can exit and shut down the vm with:

```bash
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
    vagrant destroy
```

This repo is part of the DevOps course CSCI-GA.2820-001/002 at NYU taught by John Rofrano.
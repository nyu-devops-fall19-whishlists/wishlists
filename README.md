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

## Prerequisite Installation using Vagrant

Vagrant and VirtualBox are required to execute this service. if you don't have this software, the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

```sh
    git clone https://github.com/nyu-devops-fall19-wishlists/wishlists.git
    cd wishlists
    vagrant up --provision
```

Once the VM is up you can use it with:

```sh
    vagrant ssh
    cd /vagrant/service
    FLASK_APP=service:app flask run -h 0.0.0.0
```


Note that we need to bind the host IP address with `-h 0.0.0.0` so that the forwarded ports work correctly in **Vagrant**. If you were running this locally on your own computer you would not need this extra parameter.

You should now be able to see the service running in your browser by going to
[http://localhost:5000](http://localhost:5000). You will see a message about the
service which looks something like this:

```
  {"name":"Wishlist REST API Service","version":"1.0"}
```

When you are done, you can use `Ctrl+C` within the VM to stop the server.

## Testing

Run the tests suite with:

```sh
    nosetests
```

You should see all of the tests passing with a code coverage report at the end. this is controlled by the `setup.cfg` file in the repo.

## Shutdown

When you are done, you can use the `exit` command to get out of the virtual machine just as if it were a remote server and shut down the vm with the following:

```sh
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with from your computer to free up disk space with:

```sh
    vagrant destroy
```

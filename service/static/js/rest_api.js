$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        // $("#wishlist_id_c").val(res.responseJSON.);
        document.getElementById("wishlist_id_c").innerHTML = res.id;
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_id_u").val("");
        $("#wishlist_name_u").val("");
        $("#wishlist_name_c").val("");
        $("#customer_id_c").val("");
        $("#wishlist_id_d").val("");
        $("#wishlist_name_s").val("");
        $("#customer_id_s").val("");
        $("#wishlist_id_s").val("");
        document.getElementById("wishlist_id_c").innerHTML = "";
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    var default_search_result = "";
    var default_search_result_product = "";

    $(document).ready(function() {
        default_search_result = $("#search_results").html();
        default_search_result_product = $("#search_results-p").html();
    });

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#wishlist_name_c").val();
        var customer_id = $("#customer_id_c").val();

        var data = {
            "name": name,
            "customer_id": Number(customer_id)
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {

        var wishlist_id = $("#wishlist_id_u").val();
        var name = $("#wishlist_name_u").val();

        var data = {
            "name": name
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/wishlists/" + wishlist_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        var wishlist_id = $("#wishlist_id_d").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/wishlists/" + wishlist_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        clear_form_data()
        $("#search_results").html(default_search_result)
    });

    // ****************************************
    // Search for a Wishlist
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#wishlist_name_s").val();
        var wishlist_id = $("#wishlist_id_s").val();
        var customer_id = $("#customer_id_s").val();

        var queryString = ""

        if (wishlist_id) {
            queryString += '?id=' + wishlist_id
        }
        if (name) {
            if (queryString.length > 0) {
                queryString += '&name=' + name
            } else {
                queryString += '?name=' + name
            }
        }
        if (customer_id) {
            if (queryString.length > 0) {
                queryString += '&customer_id=' + customer_id
            } else {
                queryString += '?customer_id=' + customer_id
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists" + queryString,
            contentType: "application/json"
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Wishlist ID</th>'
            header += '<th style="width:40%">Wishlist Name</th>'
            header += '<th style="width:40%">Customer ID</th>'
            $("#search_results").append(header);
            var firstWishlist = "";
            for(var i = 0; i < res.length; i++) {
                var wishlist = res[i];
                var row = "<tr><td>"+wishlist.id+"</td><td>"+wishlist.name+"</td><td>"+wishlist.customer_id+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstWishlist = wishlist;
                }
            }

            $("#search_results").append('</table>');

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create a Wishlist Item
    // ****************************************

    $("#create-btn-p").click(function () {

        var wishlist_id = $("#wishlist_id_cp").val();
        var product_id = $("#product_id_cp").val();
        var product_name = $("#product_name_cp").val();

        var data = {
            "product_id": Number(product_id),
            "product_name": product_name
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/wishlists/"+wishlist_id+"/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete a Wishlist Product
    // ****************************************

    $("#delete-btn-p").click(function () {

        var wishlist_id = $("#wishlist_id_dp").val();
        var product_id = $("#product_id_dp").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/wishlists/" + wishlist_id + "/items/" + product_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Update a Wishlist Product
    // ****************************************

    $("#update-btn-p").click(function () {

        var wishlist_id = $("#wishlist_id_up").val();
        var product_id = $("#product_id_up").val();
        var product_name = $("#product_name_up").val();

        var data = {
            "product_name": product_name
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/wishlists/" + wishlist_id + "/items/" + product_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Search for a Wishlist Product
    // ****************************************

    $("#search-btn-p").click(function () {

        var product_name = $("#product_name_sp").val();
        var wishlist_id = $("#wishlist_id_sp").val();
        var product_id = $("#product_id_sp").val();

        var queryString = ""

        if (wishlist_id) {
            queryString += '?wishlist_id=' + wishlist_id
        }
        if (product_name) {
            if (queryString.length > 0) {
                queryString += '&product_name=' + product_name
            } else {
                queryString += '?product_name=' + product_name
            }
        }
        if (product_id) {
            if (queryString.length > 0) {
                queryString += '&product_id=' + product_id
            } else {
                queryString += '?product_id=' + product_id
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists/" + wishlist_id + "/items" + queryString,
            contentType: "application/json"
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results-p").empty();
            $("#search_results-p").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Wishlist ID</th>'
            header += '<th style="width:40%">Product ID</th>'
            header += '<th style="width:40%">Product Name</th>'
            $("#search_results-p").append(header);
            var firstWishlistItem = "";
            for(var i = 0; i < res.length; i++) {
                var wishlistitem = res[i];
                var row = "<tr><td>"+wishlistitem.wishlist_id+"</td><td>"+wishlistitem.product_id+"</td><td>"+wishlistitem.product_name+"</td></tr>";
                $("#search_results-p").append(row);
                if (i == 0) {
                    firstWishlistItem = wishlistitem;
                }
            }

            $("#search_results-p").append('</table>');

            // copy the first result to the form
            if (firstWishlistItem != "") {
                update_form_data(firstWishlistItem)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the second form
    // ****************************************

    $("#clear-btn-p").click(function () {
        $("#wishlist_id_cp").val("");
        $("#product_id_cp").val("");
        $("#product_name_cp").val("");
        $("#wishlist_id_up").val("");
        $("#product_id_up").val("");
        $("#product_name_up").val("");
        $("#wishlist_id_dp").val("");
        $("#product_id_dp").val("");
        $("#wishlist_id_sp").val("");
        $("#product_id_sp").val("");
        $("#product_name_sp").val("");
        $("#search_results-p").html(default_search_result_product)
    });

    // ****************************************
    // Move to Cart
    // ****************************************

    $("#create-btn-action").click(function () {

        var wishlist_id = $("#wishlist_id_action").val();
        var product_id = $("#product_id_action").val();

        // var data = {
        //     "product_name": product_name
        // };

        var ajax = $.ajax({
                type: "PUT",
                url: "/wishlists/" + wishlist_id + "/items/" + product_id + "/add-to-cart",
                contentType: "application/json",
                data: ""
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})

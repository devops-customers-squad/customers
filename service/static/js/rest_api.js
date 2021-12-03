$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the customer form section with data from the response
    function update_customer_form_data(res) {
        $("#cust_id").val(res.id);
        $("#cust_first_name").val(res.first_name);
        $("#cust_last_name").val(res.last_name);
        $("#cust_username").val(res.username);
        $("#cust_password").val(res.password);
        if (res.locked) {
            $("#cust_locked").val("true");
        } else {
            $("#cust_locked").val("false");
        }
    }

    function update_address_form_data(res) {
        if (res != null && res.addresses.length != 0) {
            var address = res.addresses[0];
            $("#addr_id").val(address.address_id);
            $("#addr_street_address").val(address.street_address);
            $("#addr_city").val(address.city);
            $("#addr_state").val(address.state);
            $("#addr_country").val(address.country);
            $("#addr_zip").val(address.zipcode);
        }
    }

    function update_address_form(res) {
        if (res != null && res.length != 0) {
            $("#addr_id").val(res.address_id);
            $("#addr_street_address").val(res.street_address);
            $("#addr_city").val(res.city);
            $("#addr_state").val(res.state);
            $("#addr_country").val(res.country);
            $("#addr_zip").val(res.zipcode);
        }
    }
    /// Clears all form fields
    function clear_form_data() {
        $("#cust_id").val("");
        $("#cust_first_name").val("");
        $("#cust_last_name").val("");
        $("#cust_username").val("");
        $("#cust_password").val("");
        $("#cust_locked").val("");
        $("#customer_table tr").remove(); 
        $("#customer_table").append(create_customer_results_header());
        clear_address_data();
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function create_address_string(address) {
        return "address_id=" + address.address_id + ": " + address.street_address + ", " + address.city + ", " + address.state + ", " + address.zipcode + ", " + address.country
    }

    function create_customer_results_header() {
        var header = '<tr style="min-width:100%">'
        header += '<th style="width:10%">ID</th>'
        header += '<th style="width:10%">First Name</th>'
        header += '<th style="width:10%">Last Name</th>'
        header += '<th style="width:10%">Username</th>'
        header += '<th style="width:10%">Password</th>'
        header += '<th style="width:10%">Locked</th>'
        header += '<th style="width:40%">Addresses</th></tr>'
        return header
    }

    function add_single_customer(res) {
        $("#customer_search_results").empty();
        $("#customer_search_results").append('<table style="width:100%" class="table-striped" id="customer_table" cellpadding="10"></table>');
        var header = create_customer_results_header()
        $("#customer_table").append(header);
        add_customer_result(res);
    }
    
    function add_multiple_customers(res) {
        $("#customer_search_results").empty();
        $("#customer_search_results").append('<table style="width:100%" class="table-striped" id="customer_table" cellpadding="10"></table>');
        var header = create_customer_results_header()
        $("#customer_table").append(header);
        var first_customer = null;
        for (var i = 0; i < res.length; i++) {
            if (i == 0) {
                first_customer = res[i];
            }
            add_customer_result(res[i]);
        }
        return first_customer
    } 
    
    function add_customer_result(res) {
        var addresses = res.addresses;
        if (addresses.length == 0) {
            row = "<tr style='min-width:100%'><td>" + res.id + "</td><td>" + res.first_name + "</td><td>" + res.last_name + "</td><td>" + res.username + "</td><td>" + res.password + "</td><td>" + res.locked + "</td><td>" + "</td></tr>";
            $("#customer_table").append(row);
        }
        for(var i = 0; i < addresses.length; i++) {
            var address = addresses[i];
            var row; 
            if (i == 0) {
                row = "<tr style='min-width:100%'><td>" + res.id + "</td><td>" + res.first_name + "</td><td>" + res.last_name + "</td><td>" + res.username + "</td><td>" + res.password + "</td><td>" + res.locked + "</td><td>" + create_address_string(address) + "</td></tr>";
            } else {
                row = "<tr style='min-width:100%'><td>" + "</td><td>" + "</td><td>" + "</td><td>" + "</td><td>" + "</td><td>" + "</td><td>" + create_address_string(address) + "</td></tr>";
            }
            $("#customer_table").append(row);
        }
    }

    function create_address_results_header() {
        var header = '<tr style="min-width:100%">'
        header += '<th style="width:10%">Customer ID</th>'
        header += '<th style="width:10%">Address ID</th>'
        header += '<th style="width:20%">Street Address</th>'
        header += '<th style="width:15%">City</th>'
        header += '<th style="width:15%">States</th>'
        header += '<th style="width:15%">Zipcode</th>'
        header += '<th style="width:15%">Country</th></tr>'
        return header
    }

    function add_single_address(res) {
        $("#address_search_results").empty();
        $("#address_search_results").append('<table style="width:100%" class="table-striped" id="address_table" cellpadding="10"></table>');
        var header = create_address_results_header
        $("#address_table").append(header);
        add_address_result(res);
    }

    function add_address_result(res) {
        var row = "<tr style='min-width:100%'><td>" + res.customer_id + "</td><td>" + res.address_id + "</td><td>" + res.street_address + "</td><td>" 
        + res.city + "</td><td>" + res.state + "</td><td>" + res.zipcode + "</td><td>" + res.country + "</td></tr>";
        $("#address_table").append(row);
    }

    function add_multiple_addresses(res) {
        $("#address_search_results").empty();
        $("#address_search_results").append('<table style="width:100%" class="table-striped" id="address_table" cellpadding="10"></table>');
        var header = create_address_results_header
        $("#address_table").append(header);

        var first_address = null;
        for (var i = 0; i < res.length; i++) {
            if (i == 0) {
                first_address = res[i];
            }
            add_address_result(res[i]);
        }
        return first_address
    } 

    /// Clears address form fields
    function clear_address_data() {
        $("#addr_id").val("");
        $("#addr_street_address").val("");
        $("#addr_city").val("");
        $("#addr_state").val("");
        $("#addr_country").val("");
        $("#addr_zip").val(""); 
        $("#address_table tr").remove(); 
        $("#address_table").append(create_address_results_header());
    }
    

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#cust-create-btn").click(function () {
        var first_name = $("#cust_first_name").val();
        var last_name = $("#cust_last_name").val();
        var username = $("#cust_username").val();
        var password = $("#cust_password").val();

        var data = {
            "addresses": []
        };

        if (first_name != "") { data["first_name"] = first_name }
        if (last_name != "") { data["last_name"] = last_name }
        if (username != "") { data["username"] = username }
        if (password != "") { data["password"] = password }

        var street_address = $("#addr_street_address").val();
        var city = $("#addr_city").val();
        var state = $("#addr_state").val();
        var country = $("#addr_country").val();
        var zipcode = $("#addr_zip").val();

        if (street_address != "" || city != "" || state != "" || country != "" || zipcode != "") {
            var address = {}
            if (street_address != "") { address["street_address"] = street_address }
            if (city != "") { address["city"] = city }
            if (state != "") { address["state"] = state }
            if (country != "") { address["country"] = country }
            if (zipcode != "") { address["zipcode"] = zipcode }

            if (Object.keys(address).length !== 0) {
                data["addresses"].push(address);
            }
        }

        var ajax = $.ajax({
            type: "POST",
            url: "/api/customers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            clear_form_data()
            update_customer_form_data(res)
            update_address_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Lock a Customer Account
    // ****************************************

    $("#cust-lock-btn").click(function () {
        var customer_id = $("#cust_id").val();

        var ajax = $.ajax({
                type: "PUT",
                url: "/api/customers/" + customer_id + "/lock",
                contentType: "application/json"
            })

        ajax.done(function(res){
            clear_form_data()
            res.id = customer_id
            update_customer_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Unlock a Customer Account
    // ****************************************

    $("#cust-unlock-btn").click(function () {
        var customer_id = $("#cust_id").val();

        var ajax = $.ajax({
                type: "PUT",
                url: "/api/customers/" + customer_id + "/unlock",
                contentType: "application/json"
            })

        ajax.done(function(res){
            clear_form_data()
            res.id = customer_id
            update_customer_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update a Customer
    // ****************************************
    $("#cust-update-btn").click(function () {

        var customer_id = $("#cust_id").val();
        var first_name = $("#cust_first_name").val();
        var last_name = $("#cust_last_name").val();
        var username = $("#cust_username").val();
        var password = $("#cust_password").val();

        var data = {};

        if (first_name != "") { data["first_name"] = first_name }
        if (last_name != "") { data["last_name"] = last_name }
        if (username != "") { data["username"] = username }
        if (password != "") { data["password"] = password }

        var ajax = $.ajax({
                type: "PUT",
                url: "/api/customers/" + customer_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            clear_form_data()
            res.id = customer_id
            update_customer_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Customer
    // ****************************************
    $("#cust-retrieve-btn").click(function () {

        var customer_id = $("#cust_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/api/customers/" + customer_id,
            contentType: "application/json",
        })

        ajax.done(function(res){
            clear_form_data()
            add_single_customer(res)
            update_customer_form_data(res)
            update_address_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Customer
    // ****************************************
    $("#cust-delete-btn").click(function () {

        var cust_id = $("#cust_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/api/customers/" + cust_id,
            contentType: "application/json"
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************
    $("#cust-clear-btn").click(function () {
        clear_form_data()
    });

    // ****************************************
    // Search for a Customer
    // ****************************************
    $("#cust-search-btn").click(function () {
        var username = $("#cust_username").val();
        var first_name = $("#cust_first_name").val();
        var last_name = $("#cust_last_name").val();

        var queryString = ""

        if (username) {
            queryString += 'username=' + username
        }
        if (first_name) {
            if (queryString.length > 0) {
                queryString += '&first_name=' + first_name
            } else {
                queryString += 'first_name=' + first_name
            }
        }
        if (last_name) {
            if (queryString.length > 0) {
                queryString += '&last_name=' + last_name
            } else {
                queryString += 'last_name=' + last_name
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/api/customers?" + queryString,
            contentType: "application/json"
        })

        ajax.done(function(res){
            clear_form_data()
            var first_customer = add_multiple_customers(res)
            if (first_customer) {
                update_customer_form_data(first_customer)
                update_address_form_data(first_customer)
            }
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Query by username prefix
    // ****************************************
    $("#cust-query-btn").click(function () {
        var username = $("#cust_username").val();

        var queryString = "";

        if (username) {
            queryString += 'prefix_username=' + username;
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/api/customers?" + queryString,
            contentType: "application/json"
        })

        ajax.done(function(res){
            clear_form_data()
            var first_customer = add_multiple_customers(res)
            if (first_customer) {
                update_customer_form_data(first_customer)
                update_address_form_data(first_customer)
            }
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


// ************************************************************************************************************************
// Address Functions
// ************************************************************************************************************************

    // ****************************************
    // Create an Address
    // ****************************************
    $("#addr-create-btn").click(function () {

        var customer_id = $("#cust_id").val();
        var street_address = $("#addr_street_address").val();
        var city = $("#addr_city").val();
        var state = $("#addr_state").val();
        var country = $("#addr_country").val();
        var zipcode = $("#addr_zip").val();
        
        if (customer_id == "") {
            flash_message("Invalid request: missing Customer ID")
            return
        }

        var data = {};

        if (street_address != "") { data["street_address"] = street_address }
        if (city != "") { data["city"] = city }
        if (state != "") { data["state"] = state }
        if (country != "") { data["country"] = country }
        if (zipcode != "") { data["zipcode"] = zipcode }

        var ajax = $.ajax({
            type: "POST",
            url: "/api/customers/" + customer_id+"/addresses",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_address_form(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update an Address
    // ****************************************
    $("#addr-update-btn").click(function () {
        var customer_id = $("#cust_id").val();

        if (customer_id == "") {
            flash_message("Invalid request: missing Customer ID")
            return
        }

        var address_id = $("#addr_id").val();
        
        var street_address = $("#addr_street_address").val();
        var city = $("#addr_city").val();
        var state = $("#addr_state").val();
        var country = $("#addr_country").val();
        var zipcode = $("#addr_zip").val();

        var data = {};

        if (street_address != "") { data["street_address"] = street_address }
        if (city != "") { data["city"] = city }
        if (state != "") { data["state"] = state }
        if (country != "") { data["country"] = country }
        if (zipcode != "") { data["zipcode"] = zipcode }

        var ajax = $.ajax({
                type: "PUT",
                url: "/api/customers/" + customer_id+"/addresses/" +address_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            clear_address_data()
            res.id = customer_id
            update_address_form(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Address
    // ****************************************
    $("#addr-retrieve-btn").click(function () {

        var customer_id = $("#cust_id").val();

        if (customer_id == "") {
            flash_message("Invalid request: missing Customer ID")
            return
        }

        var address_id = $("#addr_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/api/customers/" + customer_id+"/addresses/" +address_id,
            contentType: "application/json",
        })

        clear_address_data()
        ajax.done(function(res){
            add_single_address(res)
            update_address_form(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Address
    // ****************************************
    $("#addr-delete-btn").click(function () {
        
        var customer_id = $("#cust_id").val();

        if (customer_id == "") {
            flash_message("Invalid request: missing Customer ID")
            return
        }

        var address_id = $("#addr_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/api/customers/" + customer_id+"/addresses/" +address_id,
            contentType: "application/json"
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Address has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // //RETRIEVE A CUSTOMER'S ADDRESSES
    // ****************************************
    $("#addr-search-btn").click(function () {

        var customer_id = $("#cust_id").val();

        if (customer_id == "") {
            flash_message("Invalid request: missing Customer ID")
            return
        }
        
        var street_address = $("#addr_street_address").val();
        var city = $("#addr_city").val();
        var state = $("#addr_state").val();
        var country = $("#addr_country").val();
        var zipcode = $("#addr_zip").val();

        var queryString = ""

        if (street_address) {
            queryString += 'street_address=' + street_address
        }
        if (city) {
            if (queryString.length > 0) {
                queryString += '&city=' + city
            } else {
                queryString += 'city=' + city
            }
        }
        if (state) {
            if (queryString.length > 0) {
                queryString += '&state=' + state
            } else {
                queryString += 'state=' + state
            }
        }
        
        if (zipcode) {
            if (queryString.length > 0) {
                queryString += '&zipcode=' + zipcode
            } else {
                queryString += 'zipcode=' + zipcode
            }
        }
        
        if (country) {
            if (queryString.length > 0) {
                queryString += '&country=' + country
            } else {
                queryString += 'country=' + country
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/api/customers/" + customer_id+"/addresses?"  + queryString,
            contentType: "application/json",
        })

        clear_address_data()
        ajax.done(function(res){
            console.log("HERE")
            var first_address = add_multiple_addresses(res)
            console.log("FIRST ADDRESS" + first_address)
            update_address_form(first_address)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the Address form
    // ****************************************
    $("#addr-clear-btn").click(function () {
        clear_address_data()
    });

})


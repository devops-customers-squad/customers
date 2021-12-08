# customers
[![build](https://github.com/devops-customers-squad/customers/actions/workflows/tdd.yml/badge.svg)](https://github.com/devops-customers-squad/customers/actions/workflows/tdd.yml)
[![codecov](https://codecov.io/gh/devops-customers-squad/customers/branch/main/graph/badge.svg?token=4E1ONO9584)](https://codecov.io/gh/devops-customers-squad/customers)
[![build](https://github.com/devops-customers-squad/customers/actions/workflows/bdd.yml/badge.svg)](https://github.com/devops-customers-squad/customers/actions/workflows/bdd.yml)

This repository contains the implementation of the customers RESTful Flask service to be used by the eCommerce site.

## Running the service
After cloning the repository and setting the current working directory to `customers`, from the command line run
```bash
    vagrant up
```

After the command finishes running, run
```bash
    vagrant ssh
```
followed by
```bash
    cd /vagrant
```

To start the service, from the command line run:
```bash
    honcho start
```

The app runs on `http://0.0.0.0:5000`

## Running the TDD tests
To run the TDD tests for the service, after executing the `vagrant ssh` and `cd /vagrant` commands, from the command line run
```bash
    nosetests
```

## Running the BDD tests
To run the BDD tests for the service, while the app is running on `http://0.0.0.0:5000` in one terminal, open a second terminal. In this second terminal, set the current working directory to `customers` and after executing the `vagrant ssh` and `cd /vagrant` commands, from the command line run
```bash
    behave
```

## Documentation
To view documentation for the available endpoints, while the app is running on `http://0.0.0.0:5000`, open a web browser and navigate to `http://0.0.0.0:5000/apidocs/`

## Service on the IBM Cloud
The URL for the service running on IBM Cloud in dev is `https://nyu-customer-service-fall2101-dev.us-south.cf.appdomain.cloud/`
The URL for the service running on IBM Cloud in prod is `https://nyu-customer-service-fall2101-prod.us-south.cf.appdomain.cloud/`

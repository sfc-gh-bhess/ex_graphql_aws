# ex_graphql_aws
Example for Snowflake Data API using GraphQL on AWS

This repository is an example of building a data API on data hosted
in Snowflake.

## GraphQL API for OAG Flight Schedule data
This example puts a simple data API to answer some basic questions of
the OAG Flight Schedule data in the Snowflake Marketplace.

The data is available in the Snowflake Marketplace [here](https://app.snowflake.com/marketplace/listing/GZ1M7Z2MQ39).

The GraphQL API for this data includes the following:
* `airportDaily` - this will show the daily departures and arrivals for the specified airport. 
  * It takes the following arguments:
    * `airport` - the 3-letter airport code to consider. Required.
    * `begin` - start date to include. Default is all the data.
    * `end` - end date to include. Default is all the data.
  * It returns an array of elements, each with the following fields:
    * `FLIGHT_DATE` - date of the statistics
    * `DEPCT` - number of departures
    * `ARRCT` - number of arrivals
* `airportDailyCarriers` - this will show the daily departures (or arrivals) for various 
  airline carriers for the specified airport. 
  * It takes the following arguments:
    * `airport_code` - the 3-letter airport code to consider. Required.
    * `deparr` - whether to consider departures (`DEPAPT`) or arrivals (`ARRAPT`). Default is `DEPAPT`.
    * `begin` - start date to include. Default is all the data.
    * `end` - end date to include. Default is all the data.
  * It returns an array of elements, each with the following fields:
    * `FLIGHT_DATE` - date of the statistics
    * `CARRIER` - airline carrier code
    * `CT` - number of flights
* `busyAirports` - this will list the top airpots in terms of flight departures (or arrivals). 
  * It can be customized with the following optional parameters:
    * `deparr` - whether to consider departures (`DEPAPT`) or arrivals (`ARRAPT`). Default is `DEPAPT`.
    * `nrows` - how many airports to show. Default is `20`.
    * `begin` - start date to include. Default is all the data.
    * `end` - end date to include. Default is all the data.
  * It returns an array of elements, each with the following fields:
    * `APT` - airport code
    * `CT` - number of flights
    * `dailies` - array of elements like the return of the `airportDaily` call. This field can also be parameterized by `begin` and `end`

The GraphQL definition of the API is as follows:
```
type AirportDaily {
  FLIGHT_DATE: AWSDate
  DEPCT: Int
  ARRCT: Int
}

type AirportDailyCarriers {
  FLIGHT_DATE: AWSDate
  CARRIER: String
  CT: Int
}

type BusyAirports {
  APT: String
  CT: Int
  dailies(begin: String, end: String): [AirportDaily!]
}

type Query {
  busyAirports(
    begin: String,
    end: String,
    deparr: String,
    nrows: Int
  ): [BusyAirports]!
  airportDaily(
    airport: String!, 
    begin: String, 
    end: String
  ): [AirportDaily]!
  airportDailyCarriers(
    airport: String!,
    begin: String,
    end: String,
    deparr: String
  ): [AirportDailyCarriers]!
}

schema {
  query: Query
}
```

## Snowflake Setup for Example
To deploy this example you will need to get the OAG Flight Schedule data imported into your
Snowflake account. It is advised to create a role to access this data, and create a user (and password)
that the example will use to access this data, and grant that user the role. This user/password
will be used by the AWS Lambda functions to access Snowflake.

To deploy the API via AWS SAM you will need to provide the following information about 
your Snowflake setup:
* Snowflake account identifier
* Snowflake username - who has access to the OAG data share in your account
* Snowflake password
* Snowflake warehouse to use
* Name of the database in your Snowflake account that houses the imported OAG data share.

## AWS Stack for Example
This repo is a SAM application and can be deployed using the AWS Serverless Application
Model (see [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) 
for more information).

The stack will deploy the following resources:
* AWS Lambda layer for the Snowflake Snowpark Python package
* AWS Lambda function to find the busy airports
* AWS Lambda function to calculate the number of daily flights from/to a given airport
* AWS Lambda function to calculate the number of daily flights for a number of carriers from/to a given airport.
* AWS Lambda function to provide simple username/password authentication to protect the API
* Permissions to allow AppSync to call the Lambda functions.
* AppSync API, schema, data sources, and resolvers

To build and deploy the stack, you will need to have installed and configured AWS SAM. 
See the AWS SAM documentation for more informaiton.

To build the stack, run:
```
make build
```

To deploy the stack, run:
```
make deploy
```

and answer the interactive questions. In addition to the Snowflake information, you
will need to provide a "prefix", which is a string that will be prepended to all
resources created by the SAM stack, and a password to protect the GraphQL API.

The URL for the API will be an output from the `make deploy` command.

## Testing the API

### Example Queries
In the following examples, `APIURL` is the output from the stack, and `WEBPASSWORD` 
is the password to protect the API.

1. Show the 20 busiest airports based on departures using the full data set:
```
curl -X POST -H "Content-Type:application/graphql" -H "Authorization:WEBPASSWORD" -d '{"query": "query {busyAirports {APT CT}} "}' APIURL 
```

2. Show the 10 busiest airports based on arrivals in the date range of July 1-5, 2022:
```
curl -X POST -H "Content-Type:application/graphql" -H "Authorization:WEBPASSWORD" -d '{"query": "query {busyAirports(nrows:10, begin:\"2022-07-01\", end:\"2022-07-05\") {APT CT}} "}' APIURL 
```

3. Show the daily departures and arrivals for `BOS` in the date range of July 1-5, 2022:
```
curl -X POST -H "Content-Type:application/graphql" -H "Authorization:WEBPASSWORD" -d '{"query": "query {airportDaily(airport:\"BOS\", begin:\"2022-07-01\", end:\"2022-07-05\") {FLIGHT_DATE DEPCT ARRCT}} "}' APIURL 
```

4. Show the daily arrivals for select carriers for `BOS` in the date range of July 1-5, 2022:
```
curl -X POST -H "Content-Type:application/graphql" -H "Authorization:WEBPASSWORD" -d '{"query": "query {airportDailyCarriers(airport:\"BOS\", begin:\"2022-07-01\", end:\"2022-07-05\", deparr:\"ARRAPT\") {FLIGHT_DATE CARRIER CT}}"}' APIURL 
```

5. Show the 5 busiest airports based on arrivals in the date range of July 1-5, 2022, and include their daily 
arrival count in that range
```
curl -X POST -H "Content-Type:application/graphql" -H "Authorization:WEBPASSWORD" -d '{"query": "query {busyAirports(nrows:5, begin:\"2022-07-01\", end:\"2022-07-05\") {APT CT dailies(begin:\"2022-07-01\", end:\"2022-07-05\") {FLIGHT_DATE ARRCT}}} "}' APIURL 
```


## Beyond This Example
While this example is fully functional, it does have some simplifications that might not
be sufficient for production. This repository is provided as an example and it is intended 
that you will modify and enhance as suits your needs. Here is a list of some areas you 
may consider to make more production-ready:
* The API is protected with simple username/password authentication. That authentication
  is integrated into Amazon API Gateway, but API Gateway provides other options for securing
  the API, such as Amazon Cognito. Username/password is the simplest form of protection, and
  production-ready solutions should look at more rigorous options, such as Cognito. 
* This example has AWS Lambda connect to Snowflake using username/password authentication.
  This is a simple way to connect, and was concise for this example. However, in production
  you would likely want to use [keypair](https://docs.snowflake.com/en/user-guide/key-pair-auth.html)
  authentication. Keypair authentication supports rotating credentials with zero downtime,
  which is important for production applications.
* You will want to make sure that your API connects to Snowflake as an application user
  and is granted narrow permissions via Snowflake RBAC. Connecting as a user with `ACCOUNTADMIN`, 
  for example, while being convenient is a high security risk.

#!/bin/bash

echo "Setting up internal datasets";

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "ccod",
	"title": "UK companies that own property in England and Wales",
    "version": "v1",
    "url": null,
	"description": "Download data about UK companies that own land or property in England and Wales. This data was originally called Commercial and corporate data (CCOD).",
	"licence_id": "ccod",
    "state": "active",
    "type": "licenced",
    "private": false,
    "external": false
}'


curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "ocod",
	"title": "Overseas companies that own property in England and Wales",
    "version": "v1",
    "url": null,
	"description": "Download data about non-UK companies that own land or property in England and Wales. This dataset was originally called Overseas companies ownership data (OCOD).",
	"licence_id": "ocod",
    "state": "active",
    "type": "licenced",
    "private": false,
    "external": false
}'

echo "Setting up external datasets";

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "ar",
	"title": "1862 Act Register",
    "version": "v1",
    "url": "https://www.gov.uk/guidance/1862-act-register",
	"description": "Download historical data about people and properties recorded on the 1862 Act Register. This was the first land register that HM Land Registry created and was the government’s first attempt to record property ownership information. It showed the owner name and property they owned.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": true
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "ppd",
	"title": "Price Paid Data",
    "version": "v1",
    "url": "https://www.gov.uk/government/collections/price-paid-data",
	"description": "Download property price data for the latest property sale prices in England and Wales.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": true
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "hpi",
	"title": "UK House Price Index: reports",
    "version": "v1",
    "url": "https://www.gov.uk/government/collections/uk-house-price-index-reports",
	"description": "Access reports for the UK House Price Index (UKHPI) for England, Scotland, Wales and Northern Ireland. The UKHPI shows changes in the value of residential properties.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": true
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "td",
	"title": "Transaction Data",
    "version": "v1",
    "url": "https://www.gov.uk/guidance/hm-land-registry-transaction-data",
	"description": "Download data about how many applications we completed in the previous month. The data shows applications for: first registrations, leases, transfers of part, dealings, official copies and searches.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": true
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "rfi",
	"title": "Request for information (requisition) data",
    "version": "v1",
    "url": null,
	"description": "View or download data about the 500 customers that send the most applications to us. It shows the number and type of applications we receive and complete. It also shows how many requests for information we send to those customers.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": false
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "ips",
	"title": "INSPIRE Index Polygons spatial data",
    "version": "v1",
	"url": "https://www.gov.uk/guidance/inspire-index-polygons-spatial-data",
	"description": "View or download HM Land Registry INSPIRE Index Polygons (data shown as shapes on a map) showing the indicative position of registered freehold properties in England and Wales. You will need a Geographical Information System (GIS) to view downloaded polygons.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": true
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "gpd",
	"title": "Geospatial Data Catalogue",
    "version": "v1",
	"url": "https://www.gov.uk/government/publications/geospatial-commission-data-catalogue-hm-land-registry",
	"description": "View or download a catalogue containing information about some of the electronic data held by HM Land Registry, based on datasets which are “linked to location” through title registrations.",
    "licence_id": null,
    "state": "active",
    "type": "open",
    "private": false,
    "external": true
}'

# PRIVATE DATASET
curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "nps",
	"title": "National Polygon Service",
    "version": "v1",
    "url": null,
	"description": "This data includes (where available) polygons, title number, estate interest, class of title, date of creation, date of update and Unique Property Reference Number (UPRN)",
    "licence_id": "nps",
    "state": "active",
    "type": "restricted",
    "private": true,
    "external": false
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "nps_sample",
	"title": "National Polygon Service Sample",
    "version": "v1",
    "url": null,
	"description": "This data includes (where available) polygons, title number, estate interest, class of title, date of creation, date of update and Unique Property Reference Number (UPRN)",
	"licence_id": "nps_sample",
    "state": "active",
    "type": "licenced",
    "private": false,
    "external": false
}'

curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "dad",
	"title": "Daily Applications",
    "version": "v1",
    "url": null,
	"description": "Daily Applications",
    "licence_id": "dad",
    "state": "active",
    "type": "confidential",
    "private": true,
    "external": false
}'

#FREEMIUM DATASET
curl -X POST \
  http://localhost:8080/v1/datasets \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"name": "res_cov",
	"title": "Restrictive Covenants",
    "version": "v1",
    "url": null,
	"description": "Download data about all registered land and property in England and Wales that have restrictive covenants.",
    "licence_id": null,
    "state": "active",
    "type": "freemium",
    "private": true,
    "external": false
}'


echo "Setting up licence data";

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "ccod",
	"status": "active",
    "title": "Licence for the supply of Commercial and Corporate Ownership Data",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/ccod/licence/view",
	"last_updated": "2019-01-06",
	"created": "2019-01-06",
	"dataset_name": "ccod"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "ocod",
	"status": "active",
    "title": "Licence for the supply of Overseas Company Ownership Data",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/ocod/licence/view",
	"last_updated": "2019-01-09",
	"created": "2019-01-09",
	"dataset_name": "ocod"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "nps_sample",
	"status": "active",
    "title": "Licence for the supply of National Polygon Sample Data",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/nps_sample/licence/view",
	"last_updated": "2019-07-15",
	"created": "2019-07-15",
	"dataset_name": "nps_sample"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "res_cov_direct",
	"status": "active",
    "title": "Direct Use",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/res_cov_direct/licence/view",
	"last_updated": "2020-02-13",
	"created": "2020-02-13",
	"dataset_name": "res_cov"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "res_cov_exploration",
	"status": "active",
    "title": "Exploration",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/res_cov_exploration/licence/view",
	"last_updated": "2020-02-13",
	"created": "2020-02-13",
	"dataset_name": "res_cov"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "res_cov_commercial",
	"status": "active",
    "title": "Commercial",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/res_cov_commercial/licence/view",
	"last_updated": "2020-02-13",
	"created": "2020-02-13",
	"dataset_name": "res_cov"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "dad",
	"status": "active",
    "title": "Daily Applications",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/dad/licence/view",
	"last_updated": "2020-01-01",
	"created": "2020-01-01",
	"dataset_name": "dad"
}'

curl -X POST \
  http://localhost:8080/v1/licence \
  -s \
  -S \
  --output /dev/null \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
	"licence_id": "nps",
	"status": "active",
    "title": "Licence for the supply of National Polygon Service Data",
    "url": "https://use-land-property-data.landregistry.gov.uk/datasets/nps/licence/view",
	"last_updated": "2019-07-15",
	"created": "2019-07-15",
	"dataset_name": "nps"
}'

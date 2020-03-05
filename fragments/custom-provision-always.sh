echo 'Populating default data for ulapd-api'

until curl -s localhost:8080 >> /dev/null
do
    sleep 1
    echo "Waiting for ulapd-api"
done

# Populate DB with default data (e.g. datasets)
docker exec ulapd-api bash /tmp/resources/scripts/load_default_data.sh

echo 'Finished populating default data for ulapd-api'
trap ctrl_c INT

function ctrl_c() {
        echo "SHUTTING DOWN POSTGRES"
        pg_ctl -D /usr/local/var/postgres stop
}

# Init python dependencies
pip3 install -r requirements.txt

# Init DB
brew install postgres
echo 'STARTING POSTGRES IN BACKGROUND'
pg_ctl -D /usr/local/var/postgres start
psql postgres -c 'CREATE DATABASE pollr;'
psql -d pollr -f db/init.sql

python3 server.py

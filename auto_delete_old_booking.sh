# /bin/sh

export username="root";
export password="askmydad";
export payload="USE testdb; DELETE FROM access WHERE checkout_at <= NOW();";
export cmd="mysql -u $username --password=$password ";

$cmd << EOL;
$payload;
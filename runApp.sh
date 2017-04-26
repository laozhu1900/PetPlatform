
uwsgi --http :5000 --module main --callable app --master --processes 4 --threads 16 -R 10000 -d uwsgi.log
while :
do 
	clear; 
	echo "select 'pobranych z linkami do YT',count(*) FROM tracks WHERE yt_id_available='YES' union select 'pobrano',count(*)  from tracks union select 'do pobrania', sum(performers.tracks_no) FROM performers " | mysql -t -u biala -pmewa tekstowo;
	sleep 5; 
done

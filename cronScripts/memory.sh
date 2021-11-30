while [ 1 ]
do
	date >>memUsage.txt
	docker ps -a >>memUsage.txt
	echo --------------------------------- >>memUsage.txt
	docker logs moriarty_tomcat | tail -100 &>>memUsage.txt
	echo --------------------------------- >>memUsage.txt
	for i in 1 2 3 4 5 6
	do
		awk '/^Mem/ {print $3}' <(free -m) >>memUsage.txt
		sleep 300
	done
done

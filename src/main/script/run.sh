 #!/bin/bash
 
 docker run  -d --rm  --log-driver=journald --log-opt tag="{{.ImageName}}/{{.Name}}"  --name=opendata-crawler  opendata-crawler:1.0.0
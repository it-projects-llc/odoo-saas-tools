Web server
==========

All requests to domains you are use must be redirected to localhost:8069 with preserving value for header HOST. Check possible configurations below.


Nginx
-----

    server {
        listen 80 default_server;

        proxy_set_header Host $host;
        
        proxy_set_header X-Real-IP       $remote_addr;
        
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        proxy_set_header X-Forwarded-Proto $scheme;

        location /longpolling {
            proxy_pass http://127.0.0.1:8072;
        }

        location / {
            proxy_pass http://127.0.0.1:8069;
        }
    }

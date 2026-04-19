server {
	server_tokens off;
	server_name lega-vps.mooo.com;
	listen 7443 ssl http2 proxy_protocol;
	listen [::]:7443 ssl http2 proxy_protocol;
	index index.html index.htm index.php index.nginx-debian.html;
	root /var/www/html/;
	ssl_protocols TLSv1.2 TLSv1.3;
	ssl_ciphers HIGH:!aNULL:!eNULL:!MD5:!DES:!RC4:!ADH:!SSLv3:!EXP:!PSK:!DSS;
	ssl_certificate /etc/letsencrypt/live/lega-vps.mooo.com/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/lega-vps.mooo.com/privkey.pem;
	if ($host !~* ^(.+\.)?lega-vps.mooo.com$ ){return 444;}
	if ($scheme ~* https) {set $safe 1;}
	if ($ssl_server_name !~* ^(.+\.)?lega-vps.mooo.com$ ) {set $safe "${safe}0"; }
	if ($safe = 10){return 444;}
	if ($request_uri ~ "(\"|'|`|~|,|:|--|;|%|\$|&&|\?\?|0x00|0X00|\||\|\{|\}|\[|\]|<|>|\.\.\.|\.\.\/|\/\/\/)"){set $hack 1;}
	error_page 400 401 402 403 500 501 502 503 504 =404 /404;
	proxy_intercept_errors on;
	#X-UI Admin Panel
	location /p3tCIJ5Vgq/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade websocket;
        proxy_set_header Connection Upgrade;		
        proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;

        proxy_pass https://127.0.0.1:45211;
		break;
	}
        location /p3tCIJ5Vgq {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade websocket;
        proxy_set_header Connection Upgrade;		
        proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;

        proxy_pass https://127.0.0.1:45211;
		break;
	}
	include /etc/nginx/snippets/includes.conf;

}

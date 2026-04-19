import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gibert Lega | IT Portfolio</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#050505;--txt:#fff;--a1:#00f2fe;--a2:#4facfe}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:var(--bg);color:var(--txt);min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;position:relative;overflow:hidden}
.blob{position:fixed;width:600px;height:600px;background:radial-gradient(circle,var(--a2) 0%,transparent 70%);opacity:.1;filter:blur(80px);border-radius:50%}
.b1{top:-200px;left:-200px;animation:mv 20s infinite alternate}
.b2{bottom:-200px;right:-200px;animation:mv 20s infinite alternate-reverse}
@keyframes mv{to{transform:translate(150px,150px)}}
.hero{position:relative;z-index:1;padding:2rem}
h1{font-size:clamp(2.5rem,8vw,5rem);font-weight:600;margin-bottom:1.5rem}
.g{background:linear-gradient(45deg,var(--a1),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
p{font-size:1.2rem;opacity:.6;max-width:500px;margin:0 auto 2.5rem}
.btn{border:1px solid rgba(255,255,255,.2);color:#fff;padding:.9rem 2.5rem;border-radius:50px;text-decoration:none;backdrop-filter:blur(10px);transition:.3s;display:inline-block}
.btn:hover{background:rgba(255,255,255,.1);transform:translateY(-3px)}
footer{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);font-size:.8rem;opacity:.3}
</style>
</head>
<body>
<div class="blob b1"></div><div class="blob b2"></div>
<div class="hero">
<h1>Digital <span class="g">Architect</span></h1>
<p>IT Infrastructure &amp; Network Security Solutions Specialist.</p>
<a href="#" class="btn">Get in touch</a>
</div>
<footer>&copy; 2026 Gibert Lega. Engineering the future.</footer>
</body>
</html>"""

def run(client, cmd):
    print(f">>> {cmd}")
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print("OUT:", out)
    if err: print("ERR:", err)
    return out

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connecting to {HOST}...")
client.connect(HOST, username=USER, password=PASS, timeout=15)
print("Connected!")

# Check nginx is running
run(client, "systemctl is-active nginx")

# Write HTML via SFTP (most reliable method - no shell quoting issues)
sftp = client.open_sftp()
print("Uploading index.html via SFTP...")
with sftp.open('/var/www/html/index.html', 'w') as f:
    f.write(HTML)
sftp.close()
print("File uploaded!")

# Set permissions
run(client, "chown www-data:www-data /var/www/html/index.html")
run(client, "chmod 644 /var/www/html/index.html")

# Check nginx config without restarting
run(client, "nginx -t")

# Reload (not restart - safer, doesn't drop connections)
run(client, "nginx -s reload")

# Verify file exists
run(client, "ls -la /var/www/html/index.html")
run(client, "head -3 /var/www/html/index.html")

client.close()
print("\nDone! Check: https://lega-vps.mooo.com/")

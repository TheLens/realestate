from fabric.api import local

def deploy():
	local("./deploy.sh")

def js():
	local("aws s3 cp static/js/lens.js s3://lensnola/land-records/js/lens.js --acl public-read")

def css():
	local("aws s3 cp static/css/lens.css s3://lensnola/land-records/css/lens.css --acl public-read")
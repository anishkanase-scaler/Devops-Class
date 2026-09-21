from httpd:latest
copy index.html /usr/local/apache2/htdocs/


# You do not need a CMD here. The httpd:2.4 image 
# already has a default command/entrypoint that starts 
# Apache when the container starts. So don't add something
#  like CMD ["apache2"] or CMD ["httpd"] unnecessarily.
# Docker will read the Dockerfile, take the httpd:2.4 base image, 
# and copy your index.html into Apache's web-root directory: /usr/local/apache2/htdocs/


# Apache is different from your previous Java program. Your Java program was your own code, 
# so you had to create HttpServer, 
# call server.start(), and make sure it kept running.



# Use the official Nginx image as a parent image
FROM nginx:alpine

# Copy the search.htmx file to the Nginx HTML directory
COPY search.htmx /usr/share/nginx/html/index.html

# Copy a custom Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]

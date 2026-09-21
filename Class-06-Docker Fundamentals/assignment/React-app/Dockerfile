FROM node:20  
# Create my Docker image starting from an image that already has Node.js 20 installed. So our container gets Node and npm without us installing them manually.

WORKDIR /app

COPY package*.json .        
# Mac project                         Docker image
# package.json       ─────────────→  /app/package.json
# package-lock.json  ─────────────→  /app/package-lock.json
# We can directly do copy . . but seperating package files gives Docker a useful caching advantage.


RUN npm install 
# After getting all packages, docker will install everything from this info inside it. React, React DOM, Vite, ESLint, etc. inside the Docker image.
# Docker has its own node_modueles other than Mac, Mac has its own. 

COPY . . 
# everything rest is copied in /app of container 

EXPOSE 5173
# can be removed, its just a documentation. 

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# npm run dev starts Vite, and Vite needs to accept connections coming through Docker's network. --host 0.0.0.0 tells Vite to listen on all network interfaces inside the container instead of only listening locally inside the container (127.0.0.1). But we want it to listen to Docker's all network interfaces as well, so we do 0.0.0.0

# CMD → starts Vite
# --host 0.0.0.0 → makes Vite reachable through Docker networking
# -p → connects your Mac's port to Vite's container port
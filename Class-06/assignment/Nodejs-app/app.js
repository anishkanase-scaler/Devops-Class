const http = require("http")
http.createServer((req, res) => {
    res.end("Hello from NodeJS!!")
}).listen(3000);
# GSA Scrape


## Docker Commands

### Build the Docker Image
```bash
docker build -t gsascrape .
```

### Run the Docker Container with volume in cwd
```bash
docker run -v $(pwd):/app gsascrape  
```

### Remove the Docker Container
```bash
docker rm gsascrape
```




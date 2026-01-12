# airdb-aqi

## Development

### Prerequisites

Before running the application, ensure you have the `airdb.db` SQLite database file in your project root directory:

### Build and Run

Build the Docker image:

```bash
docker build -f Dockerfile.dev -t aqi-dev . --no-cache
```

Run the container:

> **Warning**: This command mounts your local ./app directory into the container.
**Any changes made inside the container—including edits, moves, or deletions—will affect your local files as well.**
There is no safety buffer: deleting a file in the container deletes it on your machine.

```bash
docker run -p 8002:8000 \
  --name aqi-container \
  -v $(pwd)/app:/code/app \
  -v $(pwd)/airdb.db:/mnt/aqi-app/airdb.db \
  --rm aqi-dev
```

The backend will now be available at: http://127.0.0.1:8002

To enter the running container for debugging:

```bash
docker exec -it aqi-container /bin/bash
```

### Database

The application expects the SQLite database at `/mnt/aqi-app/airdb.db` inside the container. The docker run command above mounts your local `airdb.db` file to this location automatically.

#### aqi table schema

```sql
CREATE TABLE aqi (
	sitename TEXT NOT NULL, 
	datacreationdate DATETIME NOT NULL, 
	so2 FLOAT, 
	co FLOAT, 
	o3 FLOAT, 
	pm10 FLOAT, 
	"pm2.5" FLOAT, 
	no2 FLOAT, 
	nox FLOAT, 
	"no" FLOAT, 
	PRIMARY KEY (sitename, datacreationdate)
);
```

### API Usage

####  Endpoint: GET /aqi/get

**Parameters:**
- `addr` (required): Site address
- `date` (required): Date in `yyyy-mm-dd` format
- `period` (required): Time range in days (e.g., `5` queries 5 days from the specified date)

**Example request:**

```bash
curl -G "http://127.0.0.1:8002/aqi/get" \
  --data-urlencode "addr=高雄市鼓山區蓮海路70號" \
  --data-urlencode "date=2024-04-13" \
  --data-urlencode "period=5"
```
**Example response:**

```json
{
	"so2": 0.87,
	"co": 0.33,
	"o3": 27.62,
	"pm10": 56.52,
	"pm2.5": 20.23,
	"no2": 11.17,
	"nox": 12.57,
	"no": 1.54
}
```

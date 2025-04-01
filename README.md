# RecommendationSystem
Assignment for my Systems Programming course

## Prerequisites
- Python 3.x
- pip (Python package manager)
- docker
- docker-compose

## Setup
1. **Clone the repository:**

   ```bash
   git clone https://github.com/PanayiotisPerdios/RecommendationSystem.git
   cd RecommendationSystem
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    
## Usage
1. **Docker-compose**
   Start the PostgreSQL container database
   ```bash
   docker-compose up -d
3. **Run the Flask application:**
   ```bash
   python run.py
4. **API Endpoints:**
   - **POST /recommend:** returns a dummy recommendation
       
   Example request body:
   ```json
   {
   "user_id": "552e8400-e29b-41d4-a716-446655440000",
   "favorite_sport": "football"
   }
   ```
   - **GET /populate:** populates container database with dummy data
5. **Docker-compose**
   ```bash
   docker-compose down
   ```
   **Important: once the container is down it wipes all data**

## Testing
The project includes basic unit tests

To run tests, use:
   ```bash
    python -m unittest discover
   ```


       

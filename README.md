# RecommendationSystem
Assignment for my Systems Programming course

## Technologies Implemented
- Endpoints for schema mapping/renaming and event recommendation
- Multi-Tenant postgresql database architecture
- Strategy pattern with function registry
- Kafka Messaging broker (processing and storing in database)
- Schema Validation
- Testing
  
## Frameworks/Libraries
- Python Flask: for the endpoints
- Marshmallow: for schema validation
- Sqlalchemy: for interacting with database with python
- Confluent_kafka: kafka library for python
- Unittest: for testing

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
2. **Build containers:**
   ```bash
   docker-compose build
   ```
   or if you want to build dummy producers, use:
   ```bash
   docker-compose --profile dummy build
   ```
4. **Create and Start containers:**
    ```bash
    docker-compose up -d
    ```
    or if you want to up dummy producers, use:
    ```bash
    docker-compose --profile dummy up -d
    ```
    
## Containers/Services used

   ```bash
   recommendation_db #postgres db server
   recommendation_app #main app
   recommendation_kafka #Kafka broker
   recommendation_zookeeper #Kafka manager
   recommendation_kafka_ui #Kafka ui
   recommendation_producer_events #dummy producer for events
   recommendation_producer_coupons #dummy producer for coupons
   recommendation_producer_users #dummy producer for users
   recommendation_consumer_events #consumer for events
   recommendation_consumer_coupons #consumer for coupons
   recommendation_consumer_users #consumer for users
   ```
## Kafka UI
   ```bash
   http://localhost:8080/
   ```
## Closing services
   1. **Stopping services:**
   ```bash
   docker-compose down
   ```
   **Important: once the recommendation_db is down it wipes all data**
   
   2. **Wiping services for rebuild**
   ```bash
   docker-compose down --volumes --remove-orphans
   ```

## Testing

To run tests, use:
   ```bash
    coverage run -m unittest discover
   ```
To see test coverage percentege, use:
   ```bash
    coverage report
   ```

## Project Structure
**Routes/Endpoints:** under `routes.py`
 - **POST /config:** sends a configuration for the recommendations schemas
       
   Example request body:
   ```json
   {
      "recommender_type": "inference",
      "recommendation_schema": {
         "user_id": {"type": "int", "source_field": "id"},
         "bet": {"type": "float", "source_field": "stake"},
         "time": {"type": "float", "source_field": "timestamp"},
         "events": {"type": "list", "source_field": "recommended_events"}
      }
   }
   ```
   - **GET /recommend/{int:user_id}:** returns a recommendation based on the config sent (configuration is required)
       
   Example response body:
   ```json
   {
      "bet": 25.51,
      "events": [
           {
               "away_team": "TEAM6848261046101",
               "country": "BRAZIL",
               "home_team": "TEAM5859262905367",
               "league": "MAJOR LEAGUE SOCCER",
               "odd": 2.69,
               "sport": "FOOTBALL"
           },
           {
               "away_team": "TEAM4842566732191",
               "country": "GERMANY",
               "home_team": "TEAM6848261046101",
               "league": "MAJOR LEAGUE SOCCER",
               "odd": 2.41,
               "sport": "FOOTBALL"
           },
           {
               "away_team": "TEAM6368865321517",
               "country": "AUSTRALIA",
               "home_team": "TEAM7194064693806",
               "league": "MAJOR LEAGUE SOCCER",
               "odd": 2.13,
               "sport": "FOOTBALL"
           }
       ],
       "time": "2025-06-01T11:28:20.507522",
       "user_id": 31
   }
   ```
   - **GET /purchase/{int:user_id}:** creates dummy coupon purchases purely for testing
       
   Example response body:
   ```json
   {
      "coupon_ids": [
        406823,
        487793,
        179162
    ],
    "message": "Coupons created successfully"
   }
   ```
**Business Logic:**

**Algorithmic Structure**:
  
   Under `services.py` four different recommendation algorithms have been implemented and stored in a function registry using the Strategy pattern, allowing seamless usage of each algorithm
   - `static`: sends the same 3 event recommendation to all users
   - `dynamic`: based on the user's favorite sport field sends recommendation that equal his favorite sport
   - `inference`: it finds the most frequent (league, sport) tuple from the user's previously played coupons and returns events based on it. If the desired number of events isn't met, the remaining events are filled with random choices to            ensure results are always returned
   - `inference_score`: it uses a weighted scoring system to rank events and recommend those with the highest scores. The process works as follows:
        - it first retrieves the user's previously played coupons and extracts the top 2 most frequent values for each relevant field: (sport, league, country, home team, and away team)
        - then, for every available event, a score is calculated by comparing the event's attributes against:
             - the user’s favorite sport and country
             - the top 2 most frequent values derived from the user’s past coupon history
        - each field contributes differently to the final score (coupon fields like league or teams may have higher weights than country or sport or user's favorite sport and country)
        - after scoring all events, the list is sorted in descending order of score. The top n events (defined by event_limit) are selected as recommendations
        - if no prior data or matching events exist, the remaining events are filled with random choices to ensure results are always returned
   - `recommendation_generator`: it serves as an interface for generating recommendations in a consistent format, regardless of which algorithm is used
   - `recommender_registry`: used by the `recommendation_generator` to select the appropriate algorithm, implementing the Strategy Pattern

**Database Structure:**

 The database is a Multi-Tenant system, meaning each client/casino has isolated data. The way it works is as follows:
 - a master database called `recommendation_system` acts as a catalog, storing the `casino_id` for all casinos using the schema defined in `db_models_master.py`
 - dynamically created casino databases using the function `create_db_per_casino()` each named `casino_<random_int>`, with their own tables defined by `db_models_shared.py`
     
**Storing Objects in Database:**

  The functions responsible for storing these objects are: `create_casinos()` `create_user_profile()` `create_users()` `create_teams()` `create_events()` `create_purchased_coupons()`, the process each one follows is outlined below:
  - each dictionary is validated using its corresponding schema from `schemas.py`
  - the data is then mapped to an SQLAlchemy object using either `db_models_shared.py` or `db_models_master.py`, and stored in the database
  - it’s important to note that in a Multi-Tenant system, we must maintain the correct database session or context at all times to determine which database to store our data in, this is why we use the `get_casino_db_session()` under `utils.py`

**Dummy Data:**

The initialization of dummy data occurs at the start of the app's execution (`run.py`) with the function `populate_db()` under `services.py` using functions to generate dummy dictionary data such as `generate_dummy_users()` `generate_dummy_casinos()` `generate_dummy_events()` `generate_dummy_teams()`

## Complete Architecture
![Alt Text](./assets/architecture.png)

       

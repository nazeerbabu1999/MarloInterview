from app import db, scheduler
from app.models import GroupData
import requests
import datetime
import logging
import atexit

def fetch_and_store_api_data():
    """
    Fetch and store API data if today's data is not already in the database.
    """
    try:
        today_date = datetime.datetime.now().date()

        # Check if today's data already exists in the database
        with db.session.no_autoflush:
            existing_data = GroupData.query.filter(
                db.func.date(GroupData.fetched_at) == today_date
            ).first()

        if existing_data:
            logging.info("Today's data is already in the database. Skipping fetch.")
            return  # Data exists, skip the fetch

        # Fetch data from the API
        api_url = "https://12af-14-97-224-214.ngrok-free.app/index"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            api_data = response.json()

            # Handle list response
            if isinstance(api_data, list):
                for index, data in enumerate(api_data):
                    group_entry = GroupData(
                        group_type=data.group,
                        data=data,
                        fetched_at=datetime.datetime.now()
                    )
                    db.session.add(group_entry)

            # Handle dictionary response
            elif isinstance(api_data, dict):
                for group, data in api_data.items():
                    group_entry = GroupData(
                        group_type=group,
                        data=data,
                        fetched_at=datetime.datetime.now()
                    )
                    db.session.add(group_entry)

            else:
                logging.error(f"Unexpected API response format: {type(api_data)}")
                return

            try:
                db.session.commit()
                logging.info("Successfully stored today's data.")
            except Exception as commit_error:
                db.session.rollback()
                logging.error(f"Error committing data: {commit_error}")
        else:
            logging.error(f"Failed to fetch data from API. Status code: {response.status_code}")

    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in fetch_and_store_api_data: {e}")


def start_scheduler():
    """
    Start the scheduler and ensure today's data is fetched at app initialization.
    """
    # Check if scheduler is already running to prevent multiple starts
    if not scheduler.running:
        # Remove any existing jobs to prevent duplicates
        scheduler.remove_all_jobs()

        # Ensure today's data is fetched during initialization
        logging.info("Checking and fetching today's data during scheduler startup...")
        fetch_and_store_api_data()

        # Add job to run daily at midnight
        scheduler.add_job(
            fetch_and_store_api_data,
            'cron',
            hour=0,  # Midnight
            minute=0,
            id='daily_api_fetch'
        )

        # Start the scheduler
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    return scheduler


# Optional: Shutdown hook
def shutdown_scheduler():
    """
    Gracefully shutdown the scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()

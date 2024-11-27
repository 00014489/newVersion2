import logging
from tgBot.youLink.links import download_audio_from_youtube, get_audio_duration
import data.connection as dataPostgres
import asyncio
import time


def process_url():
    logging.info("Starting the process_url function.")
    while True:  # Loop indefinitely
        try:
            # Retrieve URLs with status TRUE
            urls = dataPostgres.get_url_ids_status_true()
            if not urls:
                logging.info("No URLs to process. Waiting...")
                time.sleep(10)  # Wait before retrying
                continue

            for url in urls:
                try:
                    # logging.info("we are here before processing")
                    logging.info(f"Processing URL: {url}")
                    download_audio_from_youtube(url)  # Download audio
                    dataPostgres.update_order_list_false(url)  # Update status to FALSE
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}")
                finally:
                    time.sleep(5)  # Add a delay between processing each URL
        except Exception as e:
            logging.error(f"Error in the main loop: {e}")
            time.sleep(10)  # Wait before restarting the loop if an error occurs

async def process_duration():
    logging.info("Starting duration process.")
    while True:
        # Get links from the database where the duration is 0
        links = await dataPostgres.get_url_duration_0()
        logging.info(f"{links}")

        if links:
            for link in links:
                try:
                    
                    logging.info(f"Processing link: {link}")
                    duration = await get_audio_duration(link)
                    await dataPostgres.update_links_duration(link, duration)
                    logging.info(f"Updated duration for link: {link}")
                except Exception as e:
                    logging.error(f"Error processing link {link}: {e}")
                await asyncio.sleep(1)  # Add a small delay to prevent hitting the DB too hard
        else:
            logging.info("No URLs with duration 0 found. Sleeping for 5 seconds...")
            await asyncio.sleep(5)  # Sleep for 5 seconds before checking again


async def shutdown():
    logging.info("Shutting down gracefully...")
    # Here you can add any cleanup code, like closing DB connections or stopping services
    await asyncio.sleep(1)

async def main():
    try:
        logging.info("Bot started.")
        
        # Run the synchronous process_url function in a separate thread
        task1 = asyncio.create_task(asyncio.to_thread(process_url))  # Convert sync to async
        
        # Create an asynchronous task for process_duration
        task2 = asyncio.create_task(process_duration())
        
        # Wait for both tasks to finish
        await asyncio.gather(task1, task2)
    
    except asyncio.CancelledError:
        logging.info("Task has been cancelled.")
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        await shutdown()  # Ensure cleanup happens no matter how the program exits


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")

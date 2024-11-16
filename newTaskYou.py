import logging
from tgBot.youLink.links import download_audio_from_youtube
import data.connection as dataPostgres
import asyncio


async def process_url():
    logging.info("Starting the process_url function.")
    while True:  # Loop indefinitely
        urls = await dataPostgres.get_url_ids_status_true()
        if not urls:
            logging.info("No URLs to process. Waiting...")
            await asyncio.sleep(10)  # Wait before retrying
            continue

        for url in urls:
            try:
                logging.info(f"Processing URL: {url}")
                await download_audio_from_youtube(url)
                await dataPostgres.update_order_list_false(url)
            except Exception as e:
                logging.error(f"Error processing URL {url}: {e}")
            finally:
                await asyncio.sleep(5)  # Add a delay between processing each URL


async def main():
    try:
        await process_url()  # Run the process_url loop
    except asyncio.CancelledError:
        logging.info("Task has been cancelled.")
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")

from wordpress.async_wp_lib import WordPressLib
import asyncio
from utils import writeline_to_log_async
from datetime import datetime
from math import ceil




wp_lib = WordPressLib()
category_id = None

async def main():
    await writeline_to_log_async(f"Started running program at {datetime.now()}")

    global category_id
    category_id = await wp_lib.get_category_id('俄州亚太联盟公众号文章列表')
    print(f'category id: {category_id}')

    await reset_progress()



    await wp_lib.close_session()


async def reset_progress():
    print("Resetting progress")
    await asyncio.gather(delete_all_posts(), delete_all_images()) 

async def delete_all_posts():
    print("Deleting posts")
    post_ids_to_delete = set()
    num_posts = await wp_lib.get_number_posts(category_id)
    num_pages = ceil(int(num_posts)/100.0) #per_page = 100
    post_res = await asyncio.gather(*(wp_lib.get_posts(i, category_id) for i in range(1, num_pages+1)))
    posts = [post for sublist in post_res for post in sublist]
    print(f'Number posts: {len(posts)}')
    for post in posts:
        post_ids_to_delete.add(post['id'])
    await asyncio.gather(*(wp_lib.delete_post(post_id) for post_id in post_ids_to_delete))
    print("Done deleting posts")


async def delete_all_images():
    print("Deleting images")
    image_ids_to_delete = set()
    num_images = await wp_lib.get_number_images("wx_")
    num_pages = ceil(int(num_images)/100.0) #since get_images has per_page = 100
    #result of gather is an aggregate list of returned values
    image_res = await asyncio.gather(*(wp_lib.get_images(i, "wx_") for i in range(1, num_pages+1)))
    images = [image for sublist in image_res for image in sublist]
    print(f'Number images: {len(images)}')
    for image in images:
        image_ids_to_delete.add(image['id'])
    await asyncio.gather(*(wp_lib.delete_image(image_id) for image_id in image_ids_to_delete))
    print("Done deleting images")


if __name__ == '__main__':
    #error with asyncio.run() upon exiting: https://stackoverflow.com/questions/60218252/python-asyncio-aiohttp-runtimeerror-event-loop-is-closed
    #asyncio.run(main())

    #this syntax doesn't give error.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

import asyncio
import datetime
import aiohttp
from more_itertools import chunked
from models import migrate_orm, close_orm, Session_async, SwapiPeople
from settings import URL_ASYNC
MAX_CHUNK = 5


async def get_json(http_session, url_link):
    async with http_session.get(url_link) as response:
        return None if response.status == 404 else await response.json()


async def make_str_from_list_links(http_session, field, attr, links):
    links = [links] if isinstance(links, str) else links
    if links:
        return ', '.join(json[field] for json in await asyncio.gather(*[get_json(http_session, link)
                                                                        for link in links]))
    else:
        return ''


async def make_people_dict(http_session, people_id, json_data):
    if json_data is None:
        people_data = dict(id=people_id, birth_year='', eye_color='', films='', gender='',
                           hair_color='', height='', homeworld='', mass='', name='', skin_color='',
                           species='', starships='', vehicles='')
    else:
        list_ref_fields = \
            await asyncio.gather(*[make_str_from_list_links(http_session, field, attr, json_data[attr])
                                   for field, attr in
                                   zip(['name', 'title', 'name', 'name', 'name'],
                                       ['homeworld', 'films', 'species', 'starships', 'vehicles'])])
        people_data = dict(id=people_id, birth_year=json_data['birth_year'],
                           eye_color=json_data['eye_color'], films=list_ref_fields[1],
                           gender=json_data['gender'], hair_color=json_data['hair_color'],
                           height=json_data['height'], homeworld=list_ref_fields[0],
                           mass=json_data['mass'], name=json_data['name'],
                           skin_color=json_data['skin_color'], species=list_ref_fields[2],
                           starships=list_ref_fields[3], vehicles=list_ref_fields[4])
    return people_data


async def get_people(http_session, people_id):
    return await make_people_dict(http_session, people_id,
                                  await get_json(http_session, f'{URL_ASYNC}/{people_id}/'))


async def set_number_people(http_session):
    json_data = await get_json(http_session, f'{URL_ASYNC}/')
    return json_data['count']


async def insert_people(json_list):
    async with Session_async() as session:
        session.add_all([SwapiPeople(**json_data) for json_data in json_list])
        await session.commit()


async def main():
    await migrate_orm()
    async with aiohttp.ClientSession() as http_session:
        for chunk_i in chunked(range(1, await set_number_people(http_session)+1), MAX_CHUNK):
            task = asyncio.create_task(insert_people(await asyncio.gather(*[get_people(http_session, i)
                                                                            for i in chunk_i])))
    main_task = asyncio.current_task()
    tasks = asyncio.all_tasks()
    tasks.remove(main_task)
    await asyncio.gather(*tasks)
    await close_orm()

start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)

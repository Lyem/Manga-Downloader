import asyncio

# Image Downloader
async def setup(driver):
    url_extension = 'https://update.greasyfork.org/scripts/472453/CloudFlare%20Challenge.user.js'
    pagina = await driver.get(url_extension, new_tab=True)

    await asyncio.sleep(1)

    await pagina
    
    btn = await pagina.find('confirm')
    await btn.click()
    
    await pagina.close()

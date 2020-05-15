const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({
        width: 1920,
        height: 1080
    });
    await page.goto('https://www.ubs.com/hk/tc/wealth-management/our-approach/marketnews.html');
    await page.waitFor(2000);

    while (await page.$('div.sdactivitystream__moreContainer') !== null) {
        const anchor = await page.$('div.sdactivitystream__moreContainer button');
        await anchor.click();
        await page.waitForResponse('https://www.ubs.com/bin/ubs/caas/v1/searchContentAbstracts');
        await page.waitFor(1000);
    }

    async function getHrefs(page, selector) {
        return await page.$$eval(selector, anchors => [].map.call(anchors, a => a.href));
    }

    const hrefs = await getHrefs(page, 'p.sdactivitystreamtile__txt a');

    fs.writeFileSync('ubs.json', JSON.stringify({ hrefs }), 'utf-8');

    await browser.close();
})();
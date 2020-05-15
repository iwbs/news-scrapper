const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({
        width: 1920,
        height: 1080
    });
    await page.goto('https://hk.allianzgi.com/zh-hk/retail/insights/insights-and-strategies');
    await page.waitForSelector('button.c-button.l-grid__column-medium-12');
    await page.waitFor(2000);

    const checkbox = await page.$('input#roleGateTnc');
    await checkbox.click();
    const button = await page.$('button.c-button.l-grid__column-medium-12');
    await button.click();
    if (await page.$('div.c-notification.c-notification--error.u-margin-bottom-2m') !== null) {
        if (checkbox) {
            await checkbox.click();
            await button.click();
        }
    }

    await page.waitFor(1000);

    while (await page.$('div.show-more-center') !== null) {
        const anchor = await page.$('div.show-more-center a');
        await anchor.click();
        await page.waitForResponse('https://hk.allianzgi.com/api/sitecore/ArticleFeature/InsightSearchResults');
        await page.waitFor(1000);
    }

    async function getHrefs(page, selector) {
        return await page.$$eval(selector, anchors => [].map.call(anchors, a => a.href));
    }

    const hrefs = await getHrefs(page, 'div.l-grid__row.align-items-stretch.js-list-view-container div.c-agi-tile__content a.c-link.c-link--block.c-link--icon');

    fs.writeFileSync('allianz.json', JSON.stringify({ hrefs }), 'utf-8');

    await browser.close();
})();
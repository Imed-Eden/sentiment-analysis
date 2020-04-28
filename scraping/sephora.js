// Importing Node library "puppeteer"
const puppeteer = require('puppeteer');

// My function getallurl allows to get all the links (href) of the products displayed in Sephora pages
const getAllUrl = async (browser, urls) => {
  var content = [];
  var results = [];
  // Looping over pages containing interesting products such as men's frangrance, women's frangrance and gifts etc.
  for (let i = 0; i < urls.length; i++) {
    // Opening a new page to access the url
    const page = await browser.newPage()
    // Access the URLs after opening the empty page
    try {
      const response = await page.goto(urls[i],{waitUntil:"networkidle2",timeout:60000})
    } catch(err) {
      console.log(err);
    }
    // Waiting to load the page
    await page.waitFor('body');
    // Calling the function autoScroll to scroll down until the end of the page is reached
    await autoScroll(page);
    // Getting the maximux number of pages (from paginator) to loop over for one of the main theme like men products or women products
    const number_pages =await page.evaluate(() => {
      let pages = parseFloat((document.querySelectorAll('body > div.css-o44is > div.css-138ub37 > div > div > div > div.css-1vuaplw > div > main > div.css-111ktzd > div > div.css-104c6qu > div.css-6su6fj > nav > ul'))[0].children[(document.querySelectorAll('body > div.css-o44is > div.css-138ub37 > div > div > div > div.css-1vuaplw > div > main > div.css-111ktzd > div > div.css-104c6qu > div.css-6su6fj > nav > ul'))[0].childElementCount - 2 ].innerText)
      return pages
    });
    // Close the page after finishing getting the number of iterations  
    page.close()
    // Making sure it is closed first
    await page.close()
    // Looping over pages for each product and brand
    for (let j = 1; j <= number_pages ; j++) {
      const page = await browser.newPage()
      try {
        const response = await page.goto(urls[i]+"?currentPage="+j,{waitUntil:"networkidle2",timeout:60000})
      } catch(err) {
        console.log(err);
      }
      await page.waitFor('body')
      await autoScroll(page)
      // Getting the url of each product (href, a)
      content = await page.evaluate(() => {
        let product_brand = [...document.querySelectorAll('a[data-comp="ProductItem "], a[data-comp="LazyLoad ProductItem "]')];
        return product_brand.map((temp) => temp.href);
      });
      // Adding each product's URL to the list
      results = results.concat(content)
   }
  console.log(urls[i])
  }
  return results
}

// getDataFromUrl is a function that retrieve all the information from each product URL that the function getAllUrl returns
const getDataFromUrl = async (browser, urls) => {
 var results = "";
 // Looping over every single product in order to get the necessary information such as price, brand, product, reviews, comments etc.
 for (let i = 0; i < urls.length; i++) {
   const page = await browser.newPage()
   await page.setViewport({width: 1280, height: 700});
   const url = urls[i];
   try {
     await page.goto(url, {timeout: 18000000}, {waitUntil: 'domcontentloaded'});
   } catch(err) {                                                                                                                                                                console.log(err);
   }
   await page.waitFor('body');
   await autoScroll(page);
   brand = await page.$eval('span[class="css-euydo4"]', el => el.innerText)
   product = await page.$eval('span[class="css-0"]', el => el.innerText)
   price = parseFloat((await page.$eval('span[data-at="price"]', el => el.innerText)).slice(1, (await page.$eval('span[data-at="price"]', el => el.innerText)).length))
   number_reviews  = parseFloat(await page.$eval('span[data-at="number_of_reviews"]', el => el.innerText))
   number_likes = await page.$eval('span[data-at="product_love_count"]', el => el.innerText)
   if (number_likes.includes("K")) {
     number_likes = (parseFloat(number_likes)*1000)
   } else {
     number_likes = (parseFloat(number_likes))
   }
   await page.evaluate(() => {
     while(document.querySelectorAll('button[class="css-frqcui "]').length == 1)
       {document.querySelectorAll('button[class="css-frqcui "]')[0].click()}
   });
   let comments = await page.evaluate(() => {
     let divs = [...document.querySelectorAll('div[data-comp="Ellipsis Box "]')];
     return divs.map((div) => div.textContent.trim());
   });
   if(number_reviews > 1) {
     if (await page.$('#ratings-reviews > div.css-fkgzyo > div.css-lwkmfb > div.css-1d8vnp2 > div > div > div.css-1r36mik') !== null) {
       mark = await page.$eval('#ratings-reviews > div.css-fkgzyo > div.css-lwkmfb > div.css-1d8vnp2 > div > div > div.css-1r36mik' , el => el.innerText)
     } else {
       mark = "4.0 / 5 stars"
     }
   } else {
     mark = ""
   }
   if(await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol' , el => el.childNodes.length) == 3) {
     gender = await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol > li:nth-child(2) > a', el => el.innerText)
     type = await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol > li:nth-child(3) > a', el => el.innerText)
     family = await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol > li:nth-child(1) > a', el => el.innerText)
   } else if (await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol' , el => el.childNodes.length) == 2) {
     type = await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol > li:nth-child(2) > a', el => el.innerText)
     family = await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol > li:nth-child(1) > a', el => el.innerText)
     gender = "both"
   } else if (await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol' , el => el.childNodes.length) == 1) {
     type = "Cologne"
     family = "Fragrance"
     gender = await page.$eval('body > div.css-o44is > div.css-138ub37 > main > div:nth-child(2) > div:nth-child(1) > div > nav > ol > li:nth-child(1) > a', el => el.innerText)
   }

   results = {brand, product, price, number_reviews, number_likes, comments, mark, type, family, gender}
   page.close()
   await page.close();
 }
 browser.close()
 return {results}
}


async function autoScroll(page){
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight){
                    clearInterval(timer);                                                                                                                                                       resolve();
                }                                                                                                                                                                       }, 100);
        });
    });
}

const scrap = async () => {
  const browser = await puppeteer.launch({
    args: [
           //'--proxy-server=198.255.114.82:3128',
           '--no-sandbox',
           '--disable-setuid-sandbox'
    ]
  });
  //urls = ["https://www.sephora.com/shop/fragrances-for-men", "https://www.sephora.com/shop/fragrances-for-women", "https://www.sephora.com/shop/fragrance-value-sets-gifts"]

  urls =["https://www.sephora.com/shop/fragrance-value-sets-gifts"]
  const urlList = await getAllUrl(browser, urls)
  console.log(urlList)
  const results = getDataFromUrl(browser, urlList)
  console.log(results)
  return results
}

// 5 - Appel la fonction `scrap()`, affichage les résulats et catch les erreurs
scrap()
  .then(value => {
    console.log(value)
  })
  .catch(e => console.log(`error: ${e}`))

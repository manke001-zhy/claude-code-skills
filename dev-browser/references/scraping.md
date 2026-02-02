# Scraping Data with Dev Browser

When you need to scrape large datasets from websites, don't scroll the DOM and extract elements one by one. Instead, intercept the network requests that the site makes to fetch its own data, then replay those requests with pagination.

## Why This Approach

- **Faster**: Network requests are much quicker than DOM scrolling and parsing
- **More reliable**: Sites often change their HTML structure but keep their APIs stable
- **Less brittle**: You don't have to worry about dynamic class names or complex selectors
- **Complete data**: APIs typically return structured data that's easier to work with

## General Approach

1. Start the dev-browser server
2. Navigate to the target page
3. Intercept network requests to find the API endpoint
4. Examine the request structure and response format
5. Write a script to replay the request with pagination
6. Extract and save the data

## Example: Scraping a News Site

### Step 1: Capture Network Traffic

```bash
cd skills/dev-browser && npx tsx <<'EOF'
import { connect, waitForPageLoad } from "@/client.js";

const client = await connect();
const page = await client.page("news-scrape");

// Enable network request logging
page.on('request', request => {
  const url = request.url();
  if (url.includes('api') || url.includes('data')) {
    console.log('API Request:', url);
    console.log('Method:', request.method());
    console.log('Headers:', request.headers());
  }
});

page.on('response', async response => {
  const url = response.url();
  if (url.includes('api') || url.includes('data')) {
    console.log('API Response:', url);
    console.log('Status:', response.status());
    try {
      const body = await response.text();
      console.log('Body preview:', body.slice(0, 200));
    } catch (e) {
      console.log('Could not read body');
    }
  }
});

await page.goto("https://example-news-site.com");
await waitForPageLoad(page);

// Wait a bit to capture initial requests
await new Promise(resolve => setTimeout(resolve, 5000));

await client.disconnect();
EOF
```

### Step 2: Identify the API Endpoint

Once you've found the API endpoint, examine its structure:

```bash
cd skills/dev-browser && npx tsx <<'EOF'
import { connect, waitForPageLoad } from "@/client.js";

const client = await connect();
const page = await client.page("news-examine");

// Make the API request directly
const response = await page.request.get({
  url: 'https://example-news-site.com/api/articles?page=1&limit=20',
  headers: {
    'Accept': 'application/json',
  }
});

const data = await response.json();
console.log('Response structure:', JSON.stringify(data, null, 2));

await client.disconnect();
EOF
```

### Step 3: Write the Scraping Script

Now write a script that paginates through all the data:

```bash
cd skills/dev-browser && npx tsx <<'EOF'
import { connect } from "@/client.js";
import fs from 'fs';

const client = await connect();
const page = await client.page("news-scrape-all");

const allArticles = [];
let page_num = 1;
let hasMore = true;

while (hasMore) {
  console.log(`Fetching page ${page_num}...`);

  const response = await page.request.get({
    url: `https://example-news-site.com/api/articles?page=${page_num}&limit=20`,
    headers: {
      'Accept': 'application/json',
    }
  });

  const data = await response.json();

  if (data.articles.length === 0) {
    hasMore = false;
  } else {
    allArticles.push(...data.articles);
    page_num++;
  }

  // Be polite - add a small delay
  await new Promise(resolve => setTimeout(resolve, 500));
}

// Save the data
fs.writeFileSync(
  'tmp/articles.json',
  JSON.stringify(allArticles, null, 2)
);

console.log(`Scraped ${allArticles.length} articles`);
await client.disconnect();
EOF
```

## Tips for Successful Scraping

1. **Respect rate limits**: Add delays between requests
2. **Handle errors**: Wrap requests in try/catch and retry failed requests
3. **Check authentication**: Some APIs require cookies or tokens - capture these from the browser's authenticated session
4. **Validate data**: Check that the response structure hasn't changed
5. **Save incrementally**: Save data after each page in case of failures

## Advanced: Using Page Route for Complex Authentication

If the API requires complex authentication:

```bash
cd skills/dev-browser && npx tsx <<'EOF'
import { connect, waitForPageLoad } from "@/client.js";

const client = await connect();
const page = await client.page("auth-scrape");

// First, log in through the UI
await page.goto("https://example.com/login");
await page.fill('input[name="email"]', 'user@example.com');
await page.fill('input[name="password"]', 'password');
await page.click('button[type="submit"]');
await waitForPageLoad(page);

// Now the page has authentication cookies
// You can make authenticated API requests
const response = await page.request.get({
  url: 'https://example.com/api/private-data',
});

const data = await response.json();
console.log(data);

await client.disconnect();
EOF
```

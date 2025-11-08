# IndexNow Auto Submitter

A Python script that automatically submits your sitemap URLs to IndexNow API, intelligently tracking submissions to avoid duplicate submissions. Only new URLs are submitted on subsequent runs.

## Features

- 🚀 Automatic sitemap parsing (supports sitemap indexes)
- 📊 Smart URL tracking - only submits new URLs
- 📝 Detailed logging with timestamps
- 🔄 Handles sitemap indexes and sub-sitemaps recursively
- ⚡ Bulk submission (up to 10,000 URLs per request)
- 🛡️ Comprehensive error handling
- 🔁 Automatic retry on rate limiting (429 errors)

## Prerequisites

- Python 3.6 or higher
- `requests` library

## Installation

1. Clone this repository:
```bash
git clone hhttps://github.com/gavirubihan/indexnow-auto-submit.git
cd indexnow-auto-submit
```

2. Install required dependencies:
```bash
pip install requests
```

## Configuration

1. Open `indexnow_submitter.py` and update the configuration section:

```python
API_KEY = "your-api-key-here"           # Your IndexNow API key
SITE_URL = "https://yourdomain.com"     # Your website URL
SITEMAP_URL = "https://yourdomain.com/sitemap.xml"  # Your sitemap URL
```

2. **Important**: Create a key file on your website root:
   - Create a file named `{YOUR_API_KEY}.txt` (e.g., `b56754fc06724b35b8e123483e5fbb9a.txt`)
   - or [Download IndexNow API Key](https://www.bing.com/indexnow/getstarted)
   - Place it at `https://yourdomain.com/{YOUR_API_KEY}.txt`
   - The file should contain only your API key

## Usage

Run the script:
```bash
python indexnow_submitter.py
```

### First Run
- Fetches all URLs from your sitemap
- Submits all URLs to IndexNow
- Creates `submitted_urls.txt` to track submitted URLs

### Subsequent Runs
- Compares sitemap URLs with previously submitted URLs
- Only submits NEW URLs that haven't been submitted before
- Updates the submission history

### Output Files

- `indexnow_log.txt` - Detailed log with timestamps
- `urls_to_submit.txt` - List of URLs from the current run
- `submitted_urls.txt` - Historical record of all submitted URLs

## How It Works

```
┌─────────────────────────────────────┐
│  1. Fetch URLs from Sitemap         │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  2. Load Submission History         │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  3. Identify New URLs               │
│     (Sitemap URLs - Submitted URLs) │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  4. Submit Only New URLs            │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  5. Update Submission History       │
└─────────────────────────────────────┘
```

## API Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200/202 | Success | URLs submitted successfully |
| 400 | Bad Request | Check payload format |
| 403 | Forbidden | Verify API key file exists |
| 422 | Unprocessable | URLs don't match host or key mismatch |
| 429 | Too Many Requests | Script will auto-retry after 5 minutes |

## Automation

### Linux/Mac (Cron)

Edit crontab:
```bash
crontab -e
```

Add this line to run daily at 2 AM:
```bash
0 2 * * * cd /path/to/indexnow-auto-submitter && /usr/bin/python3 indexnow_submitter.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily)
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\indexnow_submitter.py`
7. Start in: `C:\path\to\`

## Supported Search Engines

IndexNow is supported by:
- Microsoft Bing
- Yandex
- Seznam.cz
- Naver (and more)

## Troubleshooting

### Error 403: Invalid key
- Ensure `{API_KEY}.txt` exists at your domain root
- Verify the file contains only the API key (no extra spaces/newlines)
- Check file is publicly accessible

### No URLs found
- Verify sitemap URL is correct and accessible
- Check sitemap format is valid XML
- Ensure sitemap contains `<loc>` tags

### Request timeout
- Reduce number of URLs if submitting too many
- Check your internet connection
- Verify IndexNow endpoint is accessible

### Want to resubmit all URLs?
Simply delete `submitted_urls.txt` and run the script again.

## Example Log Output

```
============================================================
Starting IndexNow Submission Process (New URLs Only)
============================================================

Step 1: Fetching URLs from sitemap...
Fetching sitemap from https://neovise.me/sitemap.xml
Found 1250 URLs in sitemap.
Total URLs in sitemap: 1250

Step 2: Loading submission history...
Loaded 1200 previously submitted URLs

Step 3: Identifying new URLs...
Found 50 NEW URLs to submit

Step 4: Saving new URLs to urls_to_submit.txt...
Saved 50 URLs to urls_to_submit.txt

Step 5: Loading URLs from urls_to_submit.txt...
Loaded 50 URLs from urls_to_submit.txt

Step 6: Submitting new URLs to IndexNow...
Submitting 50 URLs to IndexNow...
SUCCESS: All 50 URLs submitted successfully (Status: 200).

Step 7: Updating submission history...
Added 50 URLs to submission history

============================================================
Submission Summary
============================================================
Total URLs in sitemap: 1250
Previously submitted: 1200
New URLs found: 50
Submission status: SUCCESS
New URLs file: urls_to_submit.txt
History file: submitted_urls.txt
============================================================
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is provided as-is. Always ensure you're complying with IndexNow's terms of service and your website's robots.txt policies.

## Acknowledgments

- [IndexNow Protocol](https://www.indexnow.org/)
- Built with Python and ❤️

## Support

If you find this tool helpful, please give it a ⭐ on GitHub!

For issues or questions, please open an issue on the GitHub repository.
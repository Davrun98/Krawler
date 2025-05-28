# Krawler
Developer challenge (FST2)

## Installation
1. Ensure that you have Python3 installed
2. Clone this repository
3. Run: `pip install -r requirements.txt` 


## Usage

Run the Krawler from the command line using:

```bash
python3 .\src\krawler.py -H <host> [-s <subdomain>] [-p <path>] [-l <depth>]  # windows

python3 src/krawler.py -H <host> [-s <subdomain>] [-p <path>] [-l <depth>]  # linux / mac
```

krawler can be run from inside the `src` directory but beware that it will then output the json files there instead of the root. 

### Required arguments
`-H`, `--host`
The root domain to crawl (e.g., example.com)

### Optional Arguments:
`-s`, `--subdomain`
The subdomain to use (default: www)

`-p`, `--path`
The path to crawl on the host (default: /)

`-l`, `--recursion-limit`
Maximum recursion depth (default: 5, set to -1 for unlimited)

### Examples
```bash
# Krawl www.example.com at root path with default recursion limit (5)
python3 src/krawler.py -H fuery.co.uk

# Krawl sub.domain.example.com with recursion limit 3
python3 src/krawler.py -s sub.domain -H example.com -l 3

# Krawl www.example.com/about with unlimited recursion
python3 src/krawler.py -s demo -H cyotek.com -p /about.php -l -1
```


## To Do:
- add pool throttling (stop it making infinite async items)
- fix "https://fuery.co.uk" duplicating "https://www.fuery.co.uk"

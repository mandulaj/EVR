EVR - ETH_VidRip
======
Simple Selenium scraper for automatically downloading Lecture Videos

**Warning**: may break with ETH Video Portal changes. Use at your own risk :D

## How to Use:
1. Install requirements
```bash
pip install -r requirements.txt
```
2. Fill in the `credentials.json` with your ETH Username and Password:
```json
{
    "username": "<username>",
    "password": "<password>"
}
```
3. Define set of tasks to download from the [ETH Video Portal](https://video.ethz.ch/lectures.html) in a `task.json` file.
    
    
`name` is the directory name to store the lecture under under 

`url` is the URL to the root of the Lecture in the Video Portal.

```json
[
    {"name": "2021_HPC", "url": "https://video.ethz.ch/lectures/d-infk/2021/autumn/263-2800-00L.html"},
    {"name": "2021_PAI", "url": "https://video.ethz.ch/lectures/d-infk/2021/autumn/263-5210-00L.html"}
]

```
4. Run the script
```bash
python main.py -t task.json
```
5. See `python main.py -h` for more help

## Session credentials
If a course has special credentials, you can add them to the to the JSON file:
```json
[
{"name": "2022_AML", "url": "https://video.ethz.ch/lectures/d-infk/2022/autumn/252-0535-00L.html", "username":"session_username", "password": "session_password"},
]
```
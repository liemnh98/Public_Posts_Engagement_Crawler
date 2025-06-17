# Social Post Interaction Extractor (Educational Use)

This is a Python script for extracting interaction metrics (like, comment, share) from a list of public social media post URLs using browser automation. It is designed for **personal or educational** use.

⚠️ **Disclaimer**: This tool is intended for educational purposes only. Scraping data from any platform without permission may violate their Terms of Service. Use responsibly and at your own risk.

---

## 📦 Requirements

- Python 3.9+
- Google Chrome browser
- Matching [ChromeDriver](https://sites.google.com/chromium.org/driver/)
- Windows OS (default)

---

## 🔧 Setup Instructions

### 1. Clone this repository
```bash
git clone https://github.com/liemnh98/Public_Posts_Engagement_Crawler.git
cd Public_Posts_Engagement_Crawler
```

### 2. Create and activate a virtual environment

#### On Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### On macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

---

## 📥 Input & Output

### Input File

Prepare a CSV file containing at least one column named `link_aired` with public post URLs.

Example:
```csv
link_aired
https://www.example.com/post/abc123
https://www.example.com/post/xyz456
```

Update this variable in the script if needed:

```python
input_path = 'data/input_demo.csv'
```

### Output File

The output will be a CSV file containing:
- link
- like_num
- comment_num
- share_num
- ldp (final resolved URL)
- success (boolean)

Adjust output location here:

```python
output_path = 'data/output_demo.csv'
```

---

## ▶️ Run the Script

Once everything is set:
```bash
python public_post_engagament_crawler.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Author

Built by **Liêm**, assisted by ChatGPT.

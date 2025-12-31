# Amazon Account Checker 

A Python tool to verify Amazon accounts using emails or phone numbers. This tool features a number generation system and a PyQt6 interface.

##  Key Features

- **Smart Number Generator**: Generates all possible phone numbers for a country in a random sequence without repetitions and with **zero memory usage**.
- **Dynamic Country Support**: Automatically retrieves valid number formats and ranges for any country.
- **Multi-threaded Engine**: Controlled concurrent processing with thread-safe logging and I/O.


##  Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Amazon-Email-Checker.git
   cd Amazon-Email-Checker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   python main.py
   ```

## Usage

### Phone Number Checking
1. Select the **Target Country** from the searchable dropdown.
2. (Optional) Provide one or more **Prefixes** separated by commas.
3. Set the **Number of Threads**.
4. Click **Generate Numbers**. The bot will calculate a unique sequence and start checking.

### Email List Checking
1. Click **Browse Email List** and select your `.txt` file.
2. The bot will process the list using the specified thread count.


<div align="center">
  <video src="https://github.com/Chuny2/Amazon-Email-Checker/raw/main/docs/video.mp4" width="100%" controls></video>
  <br>
  <em>(If the video doesn't play, <a href="docs/video.mp4">click here to download</a>)</em>
</div>

##  Disclaimer

Be aware that using this tool may violate Amazon's terms of service, and it is your responsibility to use it appropriately.

---


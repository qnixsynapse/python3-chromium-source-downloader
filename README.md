# python3-chromium-source-downloader
A python3 scriptlet that lets you download the lastest(stable/beta/dev) chromium source


# Requirements
* python3
* python3-tqdm(for a fancy progress bar)

# Usage
Make the script executable and use the following syntax

downloadsource.py <directory to download> <options>
  
  
  * < Directory to download> : Any directory to where the chromium source is to be downloaded. 
    Example: `downloadsource.py /home/Download` will download the source in /home/Download directory
    
  * <options> : There are 5 options
     * --beta : This downloads the latest beta source
     * --stable : This downloads the latest stable source
     * --dev : This downloads the latest developer source
     * --tests : This downloads additional data for running tests
     * --version : Downloads a specific version of Chromium source
  
  
  This is the original scriptlet taken from src.fedoraproject.org/rpms/chromium and re written in python3. 

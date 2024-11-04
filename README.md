Zotero PDF Sync Script

This Python script copies all PDF files saved in the Zotero storage folder to a designated folder on my Desktop. The Desktop folder is then automatically synced to iCloud, allowing easy access to my PDFs from the cloud.

How It Works

The script watches for new, modified, or deleted PDFs in Zotero's storage directory and keeps a synchronized copy in the specified iCloud-synced destination folder. Any changes in the Zotero storage are reflected in the destination folder, ensuring that the cloud folder always has the latest version of each PDF.

Scheduling with Cron

To automate the script, I use cron to run it every hour at minute 32. Here’s how to set it up:

Open the cron editor:
bash
Copier le code
crontab -e
Add the following line to schedule the script:
bash
Copier le code
32 * * * * /Users/ambroisewarnery/.rye/shims/python3 /Users/ambroisewarnery/Scripts/duplicateZotero2.py >/dev/null 2>&1
This command tells the system to run the script at 32 minutes past every hour, using the .rye Python interpreter specified in the path.

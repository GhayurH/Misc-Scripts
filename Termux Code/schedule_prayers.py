import csv
import subprocess
from datetime import datetime, timedelta

# Convert time (hh:mm:ss) to cron time format (minute, hour)
def time_to_cron(time_str):
    # Handle both HH:MM:SS and HH:MM formats
    if len(time_str.split(":")) == 2:
        time_str += ":00"  # Add seconds if missing
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return time_obj.minute, time_obj.hour

# Function to remove existing prayer-related cron jobs before adding new ones
def remove_old_prayer_cron_jobs():
    # Filter out lines related to prayer notifications and overwrite crontab
    subprocess.run('(crontab -l | grep -v "termux-notification --id") | crontab -', shell=True)

# Function to create a cron job for a given time and message
def create_cron_job(minute, hour, day, month, message, notification_id):
    cron_time = f"{minute} {hour} {day} {month} *"
    # Escape quotes for the shell command
    cron_command = f'termux-notification --id {notification_id} --title \\"Prayer Reminder\\" --content \\"{message}\\"'
    cron_job = f'{cron_time} {cron_command}'
    
    # Use subprocess to add the cron job via the crontab command
    subprocess.run(f'(crontab -l ; echo "{cron_job}") | crontab -', shell=True)

# Read the CSV and schedule notifications for Fajr, Dhuhr, and Maghrib
def schedule_prayer_notifications(csv_file):
    remove_old_prayer_cron_jobs()  # Clean up old cron jobs first

    today = datetime.now()
    end_date = today + timedelta(days=30)
    
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Ensure the date is in the correct format
            date_str = row['Date']
            if len(date_str.split()) == 2 and len(date_str.split()[1].split(":")) == 2:
                date_str += ":00"  # Add seconds to the time if missing

            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            
            # Ignore past dates
            if date_obj == today:
                continue
            
            # Schedule notifications only for the next 30 days
            if date_obj > end_date:
                continue

            day = date_obj.day
            month = date_obj.month

            # Fajr
            fajr_minute, fajr_hour = time_to_cron(row['Fajr'])
            # 10 minutes before Fajr
            fajr_before = datetime.strptime(row['Fajr'], "%H:%M:%S") - timedelta(minutes=10)
            create_cron_job(fajr_before.minute, fajr_before.hour, day, month, "10 minutes to Fajr", 1)
            # At Fajr
            create_cron_job(fajr_minute, fajr_hour, day, month, "It's time for Fajr", 1)

            # Dhuhr
            dhuhr_minute, dhuhr_hour = time_to_cron(row['Dhuhr'])
            # 10 minutes before Dhuhr
            dhuhr_before = datetime.strptime(row['Dhuhr'], "%H:%M:%S") - timedelta(minutes=10)
            create_cron_job(dhuhr_before.minute, dhuhr_before.hour, day, month, "10 minutes to Dhuhr", 2)
            # At Dhuhr
            create_cron_job(dhuhr_minute, dhuhr_hour, day, month, "It's time for Dhuhr", 2)

            # Maghrib
            maghrib_minute, maghrib_hour = time_to_cron(row['Maghrib'])
            # 10 minutes before Maghrib
            maghrib_before = datetime.strptime(row['Maghrib'], "%H:%M:%S") - timedelta(minutes=10)
            create_cron_job(maghrib_before.minute, maghrib_before.hour, day, month, "10 minutes to Maghrib", 3)
            # At Maghrib
            create_cron_job(maghrib_minute, maghrib_hour, day, month, "It's time for Maghrib", 3)

    # Schedule reminder for the last day to re-run the script
    if (end_date - today).days == 30:  # This checks if we are at the end of the 30-day period
        reminder_message = "Please re-run the prayer schedule script tonight."
        create_cron_job(0, 9, end_date.day, end_date.month, reminder_message, 4)  # Reminder at 09:00 AM

# Call the function to schedule the prayer notifications
schedule_prayer_notifications('prayer_times.csv')
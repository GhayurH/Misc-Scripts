import csv
import subprocess
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(filename='prayer_schedule.log', level=logging.DEBUG)

# Get the full path to termux-notification
termux_notification_path = os.popen('which termux-notification').read().strip()

# Convert time (hh:mm:ss) to cron time format (minute, hour)
def time_to_cron(time_str):
    time_obj = parse_time_string(time_str)
    return time_obj.minute, time_obj.hour

# Function to remove existing prayer-related cron jobs before adding new ones
def remove_old_prayer_cron_jobs():
    subprocess.run('(crontab -l | grep -v "termux-notification --id") | crontab -', shell=True)

# Function to create a cron job for a given time and message
def create_cron_job(minute, hour, day, month, message, notification_id):
    cron_time = f"{minute} {hour} {day} {month} *"
    cron_command = (
        f'{termux_notification_path} --id {notification_id} '
        f'--title "Prayer Reminder" --content "{message}" '
        f'>> /storage/emulated/0/termux_cron.log 2>&1'
    )
    cron_job = f'{cron_time} {cron_command}'

    subprocess.run(f'(crontab -l ; echo "{cron_job}") | crontab -', shell=True)

# Function to parse time strings
def parse_time_string(time_str):
    if len(time_str.strip()) == 0:
        raise ValueError("Empty time string")
    if len(time_str.split(":")) == 2:
        time_str += ":00"
    return datetime.strptime(time_str, "%H:%M:%S")

# Read the CSV and schedule notifications for Fajr, Dhuhr, and Maghrib
def schedule_prayer_notifications(csv_file):
    try:
        remove_old_prayer_cron_jobs()  # Clean up old cron jobs first

        today = datetime.now()
        end_date = today + timedelta(days=30)

        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                date_str = row['Date']
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                # Ignore past dates
                if date_obj.date() < today.date():
                    continue

                # Schedule notifications only for the next 30 days
                if date_obj > end_date:
                    continue

                day = date_obj.day
                month = date_obj.month

                # Fajr
                fajr_time = parse_time_string(row['Fajr'])
                fajr_datetime = datetime.combine(date_obj.date(), fajr_time.time())
                fajr_before = fajr_datetime - timedelta(minutes=10)
                create_cron_job(fajr_before.minute, fajr_before.hour, day, month, "10 minutes to Fajr", 1)
                create_cron_job(fajr_time.minute, fajr_time.hour, day, month, "It's time for Fajr", 1)

                # Dhuhr
                dhuhr_time = parse_time_string(row['Dhuhr'])
                dhuhr_datetime = datetime.combine(date_obj.date(), dhuhr_time.time())
                dhuhr_before = dhuhr_datetime - timedelta(minutes=10)
                create_cron_job(dhuhr_before.minute, dhuhr_before.hour, day, month, "10 minutes to Dhuhr", 2)
                create_cron_job(dhuhr_time.minute, dhuhr_time.hour, day, month, "It's time for Dhuhr", 2)

                # Maghrib
                maghrib_time = parse_time_string(row['Maghrib'])
                maghrib_datetime = datetime.combine(date_obj.date(), maghrib_time.time())
                maghrib_before = maghrib_datetime - timedelta(minutes=10)
                create_cron_job(maghrib_before.minute, maghrib_before.hour, day, month, "10 minutes to Maghrib", 3)
                create_cron_job(maghrib_time.minute, maghrib_time.hour, day, month, "It's time for Maghrib", 3)

        # Schedule reminder for the last day to re-run the script
        reminder_message = "Please re-run the prayer schedule script tonight."
        create_cron_job(0, 9, end_date.day, end_date.month, reminder_message, 4)  # Reminder at 09:00 AM

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

# Call the function to schedule the prayer notifications
schedule_prayer_notifications('prayer_times.csv')
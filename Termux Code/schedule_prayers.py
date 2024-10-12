import csv
import subprocess
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(filename='prayer_schedule.log', level=logging.DEBUG)

# Get the full path to termux-notification
termux_notification_path = os.popen('which termux-notification').read().strip()

# Function to parse date strings
def parse_date_string(date_str):
    date_str = date_str.strip()
    if not date_str:
        raise ValueError("Empty date string")
    date_formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d"]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date '{date_str}' is not in a recognized format.")

# Function to parse time strings
def parse_time_string(time_str):
    time_str = time_str.strip()
    if not time_str:
        raise ValueError("Empty time string")
    time_formats = ["%H:%M:%S", "%H:%M"]
    for fmt in time_formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Time '{time_str}' is not in a recognized format.")

# Function to create a cron job line
def create_cron_job_line(minute, hour, day, month, message, notification_id):
    cron_time = f"{minute} {hour} {day} {month} *"
    cron_command = (
        f'{termux_notification_path} --id {notification_id} '
        f'--title "Prayer Reminder" --content "{message}" '
        f'>> /storage/emulated/0/termux_cron.log 2>&1'
    )
    cron_job = f'{cron_time} {cron_command}'
    return cron_job

# Read the CSV and schedule notifications for Fajr, Dhuhr, and Maghrib
def schedule_prayer_notifications(csv_file):
    try:
        today = datetime.now().date()
        end_date = today + timedelta(days=30)

        # Read existing crontab
        result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            current_crontab = ''
        else:
            current_crontab = result.stdout

        # Remove old prayer-related cron jobs
        new_crontab_lines = [
            line for line in current_crontab.split('\n')
            if 'termux-notification --id' not in line
        ]

        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                date_str = row['Date']
                try:
                    date_obj = parse_date_string(date_str)
                except ValueError as e:
                    logging.error(f"Skipping row due to date parsing error: {e}")
                    continue

                # Ignore past dates
                if date_obj < today:
                    continue

                # Schedule notifications only for the next 30 days
                if date_obj > end_date:
                    continue

                day = date_obj.day
                month = date_obj.month

                # Fajr
                try:
                    fajr_time = parse_time_string(row['Fajr'])
                    fajr_datetime = datetime.combine(date_obj, fajr_time)
                    fajr_before = fajr_datetime - timedelta(minutes=10)
                    new_crontab_lines.append(
                        create_cron_job_line(
                            fajr_before.minute, fajr_before.hour, day, month,
                            "10 minutes to Fajr", 1
                        )
                    )
                    new_crontab_lines.append(
                        create_cron_job_line(
                            fajr_time.minute, fajr_time.hour, day, month,
                            "It's time for Fajr", 1
                        )
                    )
                except Exception as e:
                    logging.error(f"Error scheduling Fajr for {date_str}: {e}")

                # Dhuhr
                try:
                    dhuhr_time = parse_time_string(row['Dhuhr'])
                    dhuhr_datetime = datetime.combine(date_obj, dhuhr_time)
                    dhuhr_before = dhuhr_datetime - timedelta(minutes=10)
                    new_crontab_lines.append(
                        create_cron_job_line(
                            dhuhr_before.minute, dhuhr_before.hour, day, month,
                            "10 minutes to Dhuhr", 2
                        )
                    )
                    new_crontab_lines.append(
                        create_cron_job_line(
                            dhuhr_time.minute, dhuhr_time.hour, day, month,
                            "It's time for Dhuhr", 2
                        )
                    )
                except Exception as e:
                    logging.error(f"Error scheduling Dhuhr for {date_str}: {e}")

                # Maghrib
                try:
                    maghrib_time = parse_time_string(row['Maghrib'])
                    maghrib_datetime = datetime.combine(date_obj, maghrib_time)
                    maghrib_before = maghrib_datetime - timedelta(minutes=10)
                    new_crontab_lines.append(
                        create_cron_job_line(
                            maghrib_before.minute, maghrib_before.hour, day, month,
                            "10 minutes to Maghrib", 3
                        )
                    )
                    new_crontab_lines.append(
                        create_cron_job_line(
                            maghrib_time.minute, maghrib_time.hour, day, month,
                            "It's time for Maghrib", 3
                        )
                    )
                except Exception as e:
                    logging.error(f"Error scheduling Maghrib for {date_str}: {e}")

        # Schedule reminder for the last day to re-run the script
        reminder_message = "Please re-run the prayer schedule script tonight."
        new_crontab_lines.append(
            create_cron_job_line(
                0, 21, end_date.day, end_date.month, reminder_message, 4
            )
        )

        # Combine all lines
        new_crontab = '\n'.join(new_crontab_lines) + '\n'

        # Set the new crontab
        subprocess.run(['crontab', '-'], input=new_crontab, text=True)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

# Call the function to schedule the prayer notifications
schedule_prayer_notifications('prayer_times.csv')
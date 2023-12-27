import boto3
import requests
from icalendar import Calendar, Event

def filter_ics_calendar(ics_content, keywords, retain_filtered_items, require_exact_match):
    cal = Calendar.from_ical(ics_content)
    new_cal = Calendar()

    for k, v in cal.items():
        if k not in ('VEVENT',):
            new_cal.add(k, v)

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            if summary:
                if require_exact_match:
                    match_condition = any(keyword == summary for keyword in keywords)
                else:
                    match_condition = any(keyword in summary for keyword in keywords)
                
                if (match_condition and retain_filtered_items) or (not match_condition and not retain_filtered_items):
                    new_cal.add_component(component)
                    
    return new_cal.to_ical()

def lambda_handler(event, context):
    BUCKET_NAME = event["s3_bucket_name"]
    SOURCE_ICS_URL = event["source_ics_url"]
    EXCLUSION_KEYWORDS_CONTAINING = event.get('exclude_title_keywords_containing', [])
    INCLUSION_KEYWORDS_CONTAINING = event.get('include_title_keywords_containing', [])
    EXCLUSION_KEYWORDS_EXACT = event.get('exclude_title_keywords_exactly_equal_to', [])
    INCLUSION_KEYWORDS_EXACT = event.get('include_title_keywords_exactly_equal_to', [])
    CALENDAR_EXPORT_NAME = event["save_export_as"]

    response = requests.get(SOURCE_ICS_URL) # Fetch the original ICS
    ics_file = response.text

    # if inclusions list is empty -> will ignore include all remnant events after exclusion

    if EXCLUSION_KEYWORDS_CONTAINING != []:
        ics_file = filter_ics_calendar(ics_file,EXCLUSION_KEYWORDS_CONTAINING,False,False)
    if EXCLUSION_KEYWORDS_EXACT != []:
        ics_file = filter_ics_calendar(ics_file,EXCLUSION_KEYWORDS_EXACT,False,True)

    if INCLUSION_KEYWORDS_CONTAINING != []:
        ics_file = filter_ics_calendar(ics_file,INCLUSION_KEYWORDS_CONTAINING,True,False)
    if INCLUSION_KEYWORDS_EXACT != []:
        ics_file = filter_ics_calendar(ics_file,INCLUSION_KEYWORDS_EXACT,True,True)

    s3 = boto3.client('s3') # Upload to S3
    s3.put_object(Body=ics_file, Bucket=BUCKET_NAME, Key=CALENDAR_EXPORT_NAME, ContentType='text/calendar')

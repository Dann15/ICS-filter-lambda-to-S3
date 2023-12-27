# ICS-filter-lambda-to-S3

This script will take a URL to an ICS file, filter it via exclusion/inclusion keyword criteria defined in AWS Lambda Context, and uploads the filtered ICS onto an AWS S3 bucket. I wrote this code so that I could color-code my medical school's ICS calendar by splitting it into multiple calendars, based on the type of event. I have AWS EventBridge running once every 24 hours, filtering out a dynamic ICS, and putting it back into my calendar program. Works like a charm.

I've put this code on here for reference sake; my apologies for the sparse documentation.

Below is an example of an AWS Lambda function context that filters the `source_ics_url` into `a-super-duper-fresh-calendar.ics`.

```
{
  "s3_bucket_name": "my-calendar-bucket",
  "source_ics_url": "https://example.org/messy-calendar.ics",
  "exclude_title_keywords_exactly_equal_to": [
    "Not fun dinner",
  ],
  "exclude_title_keywords_containing": [
    "Hello World"
  ],
  "include_title_keywords_exactly_equal_to": [],
  "include_title_keywords_containing": [
    "Evening"
  ],
  "save_export_as": "a-super-duper-fresh-calendar.ics"
}
```
```e.g. "Not fun dinner Evening" will be included.```

```e.g. "Hello World" will be excluded.```

```e.g. "Hello Worlds" will be excluded.```

```e.g. "Hello World Evening" will be excluded.```

```e.g. "Evening" will be included.```

```e.g. "Evenings" will be included.```

```e.g. "stuff" will be not be included.``` (I say 'not included' because it doesn't match inclusion criteria)

Filter flows from...
`EXCLUSION CONTAINING -> EXCLUSION EXACT -> INCLUSION CONTAINING -> INCLUSION EXACT`

Exclusion occurs prior to inclusion. If an include/exclude json variable is empty, it will simply skip it. Inclusion will only keep items that fit the criteria. Inclusion can be tricky, because inclusion containing & inclusion exact will not append on each other. Inclusion Exact will essentially override Inclusion Containing.

Everything will be particular to your use-case.

This code hasn't been rigorously tested, but has definitely undergone plenty of tweaks and use by my peers. Hope this helps someone out.

To run this, ensure that you install all pip packages within the working directory then upload the Zip file to AWS Lambda and test!

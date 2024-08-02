def update_jobs_with_summaries(summarized_jobs):
    import os

    import boto3

    print("Initializing DynamoDB resource for updating jobs with summaries")
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1",
    )
    table = dynamodb.Table("jobs")

    for job in summarized_jobs:
        try:
            response = table.update_item(
                Key={"id": job.job_id},
                UpdateExpression="SET team_information = :ti, product_information = :pi, "
                "technology_stack = :ts, key_responsibilities = :kr, "
                "requirements = :req, exceptional_perks = :ep",
                ExpressionAttributeValues={
                    ":ti": job.team_information,
                    ":pi": job.product_information,
                    ":ts": job.technology_stack,
                    ":kr": job.key_responsibilities,
                    ":req": job.requirements,
                    ":ep": job.exceptional_perks,
                },
                ReturnValues="UPDATED_NEW",
            )
            print(f"Successfully updated job {job.job_id} with summary information")
        except Exception as e:
            print(f"Error updating job {job.job_id}: {str(e)}")

    print("Finished updating jobs with summary information")

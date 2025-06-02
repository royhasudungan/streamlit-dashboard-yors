def preprocess_data(df_jobs, df_skills, df_skills_job):
    # Drop duplicate rows
    df_jobs = df_jobs.drop_duplicates(subset=['job_id'])
    df_skills = df_skills.drop_duplicates(subset=['skill_id'])
    df_skills_job = df_skills_job.drop_duplicates(subset=['job_id', 'skill_id'])

    # Drop rows with missing IDs (job_id or skill_id) yang penting buat join
    df_jobs = df_jobs.dropna(subset=['job_id', 'job_title_short'])
    df_skills = df_skills.dropna(subset=['skill_id', 'skills'])
    df_skills_job = df_skills_job.dropna(subset=['job_id', 'skill_id'])

    # Pastikan tipe data ID konsisten (string)
    df_jobs['job_id'] = df_jobs['job_id'].astype(str)
    df_skills['skill_id'] = df_skills['skill_id'].astype(str)
    df_skills_job['job_id'] = df_skills_job['job_id'].astype(str)
    df_skills_job['skill_id'] = df_skills_job['skill_id'].astype(str)

    # strip spasi di skill names dan job titles supaya rapih
    df_jobs['job_title_short'] = df_jobs['job_title_short'].str.strip()
    df_skills['skills'] = df_skills['skills'].str.strip()

    return df_jobs, df_skills, df_skills_job


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

def create_view_model_top_skills(df_jobs, df_skills, df_skills_job):
    # Merge skills_job_dim dengan skills_dim untuk dapat nama skill
    df_skills_job = df_skills_job.merge(df_skills, on='skill_id', how='left')

    # Merge df_jobs dengan skills_job_dim untuk dapat job_title_short + skill
    df_merged = df_skills_job.merge(df_jobs[['job_id', 'job_title_short']], on='job_id', how='left')

    # Hitung frekuensi skill per job_title_short
    df_summary = (
        df_merged
        .groupby(['job_title_short', 'skills'])
        .size()
        .reset_index(name='count')
    )

    # Simpan ke CSV
    df_summary.to_csv('job_title_skill_count.csv', index=False)
    return df_summary


📂 Current App Structure (Django Templates + Django backend + PostgreSQL)

1. core
- settings.py
- urls.py

2. accounts

Handles authentication and basic user management.

Views (accounts/views.py):
- home_view — landing page
- signup_view — user registration using Django's built-in User model
- login_view
- logout_view
- password_reset — not yet implemented

Templates: templates/accounts/

3. uploads

Handles file upload and validation.

Views (uploads/views.py):
- upload_view — accepts the following file types: csv, xlsx, xls, fastq, fastq.gz, fq, fq.gz, fasta, fna, fa, gbk, gb, genbank

Business logic (uploads/utils.py):
- calculate_md5 — computes MD5 hash of an uploaded file for deduplication or integrity checks
- get_file_extension — extracts and normalises the file extension
- human_readable_size — converts raw byte count to a human-readable string (e.g. "2.4 MB")
- validate_file — checks extension and any other constraints before the file is saved

Templates: templates/uploads/
Template tag (uploads/templatetags/file_filters.py): formats raw file size into human-readable strings for templates.

4. projects

Handles project creation, pipeline execution via Celery, and result display.

Views (projects/views.py):
- create_project — renders the project creation form (GET) and processes pipeline selection (POST). Delegates input validation to the appropriate handler in utils.py, then creates the ProjectRun record and attaches files.
- project_detail — fetches a ProjectRun and its associated result (if finished) and renders the detail page.
- run_project_celery — resets a project to QUEUED and dispatches the appropriate Celery task. Guards against re-queuing a project that is already actively running. Uses transaction.on_commit so the task is only dispatched after the database state is committed.

Tasks (projects/tasks.py):
Celery tasks are kept in a dedicated tasks.py so Celery's autodiscovery finds them automatically (no manual registration needed).
- run_timepoint — runs the Timepoint analysis end-to-end: marks the project RUNNING, builds the config from the stored fields, calls run_analysis_from_config, saves the result to TimepointResult, and marks the project SUCCESS or FAILED. Slack notifications are sent at start, success, and failure.
- run_sequence — placeholder, not yet implemented. Currently marks the project FAILED with a clear error message so the UI reflects the correct state instead of silently hanging.

Business logic helpers (projects/utils.py):
- handle_timepoint — validates Timepoint POST data: checks that the file exists and belongs to the user, that it is a CSV, and that none of the required column-mapping fields are blank. Returns (cleaned_data, error).
- handle_sequence — validates Sequence POST data: checks that a reference file and 1–2 read files are provided and accessible. Extension validation is stubbed out and ready to be filled in when the pipeline is implemented. Returns (cleaned_data, error).
- get_user_files — returns a queryset of uploaded files for the given user (superusers see all files).
- get_user_file — returns a single uploaded file, enforcing user ownership for non-superusers. Used inside the validators above and anywhere a single file needs to be fetched safely.
- is_stuck — returns True if a QUEUED project has not been picked up within 5 minutes, or a RUNNING project has been running for more than 4 hours. Used by run_project_celery to decide whether a re-run should be allowed.
- send_slack_notification — low-level helper that POSTs a message to the Slack webhook URL set in SLACK_WEBHOOK_URL.
- notify_slack — builds a human-readable status message for a project run (starting / success / failed) and calls send_slack_notification.

Templates: templates/projects/

5. dashboard

Central hub for file and project management. All views here render dashboard templates or redirect back to the dashboard, so they live here regardless of which models they touch.

Views (dashboard/views.py):
- dashboard_view — main dashboard page. Lists the user's uploaded files with search, sort, and pagination. Displays all their projects with file names attached. Computes summary stats (total file count, total storage used). Marks which files are "locked" (attached to a project and therefore not deletable). Superusers see all files and projects across all users.
- delete_file_view — deletes a file if it is not attached to any project. Deletion triggers a post_delete signal that also removes the file from disk. Returns an error message if the file is in use. Superusers can delete any file; regular users can only delete their own.
- download_file_view — streams a file back to the browser as an attachment. Superusers can download any file; regular users can only download their own.
- delete_project_view — deletes a project and its associated results (cascades to TimepointResult). Blocked if the project is actively running (unless it is stuck). Only superuser can delete the projects. normal users cannot delete any project.

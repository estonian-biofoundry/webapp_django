📂 Current App Structure

1. accounts
   Handles authentication and basic user management
   Views:
   home_view (landing page)
   signup_view
   login_view
   logout_view

Templates: templates/accounts/

2. uploads
   Handles file upload logic and business logic
   Views:
   upload_view
   Business logic (uploads/utils.py): calculate_md5(file_obj) & filesize, validate_file(file_obj, max_size, allowed_types)

Templates: templates/uploads/
Template tag (uploads/templatetags/file_filters.py): formatting file size:

3. dashboard
   User dashboard & file listing
   Views:
   dashboard_view (lists uploaded files, pagination, stats)

Template: templates/dashboard/

✅ Achievements So Far

Fully functional File model: Fields: upload_id, user, file, original_filename, file_size, status, uploaded_at, md5

CRUD-based file upload with Django ORM (no ModelForm required)

MD5 calculation & file validation (size + optional allowed types)

Pagination of user files using Django Paginator

Template tags for formatting file size (|filesize)

Base template (base.html) with consistent navigation

Dashboard shows user files, pagination, and file stats

Business logic separated into utils.py for reusability

Solid understanding of views, templates, and QuerySets

🚀 Near-Term Goals / Roadmap

1. Dashboard Improvements
   Display file count & total storage used
   Sorting files by upload date, size, or filename
   Delete files (DB row + physical file)
   Optional: secure file download endpoint (owner-only)

2. Uploads Enhancements
   Handle large files (chunked or async uploads)
   Streaming upload/download
   Optional: switch storage backend to S3

3. Signals & Cleanup
   Use Django signals to delete physical files when a File row is deleted
   Optional: signal to update dashboard stats automatically

4. Projects & Pipelines (Future)
   Create projects app (organize files & samples)
   Integrate pipelines with Celery for background processing
   Update project status (processing, finished, failed)
   Optional: email notifications on pipeline completion

5. Front-End / API Considerations
   Current templates are Django-based
   Later: switch to React/Vue + Django REST Framework
   Template tags like |filesize won’t be needed in API-driven frontend

6. Miscellaneous / Nice-to-have
   File versioning / history
   Dashboard filters & search
   Sorting & pagination combined
   File preview (images, PDFs)

🔧 Recommended Next Steps (Order)
Implement file deletion fully (DB + filesystem) using signals
Improve dashboard: stats, sorting, counts
Implement secure file download endpoint (owner-only)
Prepare for chunked / async uploads
Plan projects app and pipeline integration
Frontend/API improvements (React, Vue, DRF)

# Instructions for Tradecore Setup on Windows

Run these commands in your Windows terminal:

1. **Make Migrations:**
   ```cmd
   python manage.py makemigrations
   ```

2. **Apply Migrations:**
   ```cmd
   python manage.py migrate
   ```

3. **Run the Custom Management Command to Setup Admin:**
   ```cmd
   python manage.py setup_admin
   ```

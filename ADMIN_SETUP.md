# SQL Classroom Admin Panel

This document describes the admin panel functionality that has been added to the SQL Classroom application.

## Features

The admin panel provides comprehensive monitoring and management capabilities for the entire SQL Classroom application:

### 📊 Dashboard
- **System Overview**: Real-time statistics on users, sections, assignments, and submissions
- **User Analytics**: Breakdown by role (students, teachers, admins)
- **Database Metrics**: Size, table count, and connection status
- **Recent Activity**: Track new users and submissions in the last 7 days

### 👥 User Management
- **View All Users**: Paginated list with search and filtering by role
- **User Details**: Comprehensive view of individual user information
- **Role Management**: Change user roles (student ↔ teacher ↔ admin)
- **User Activity**: View enrollments, sections, and submissions

### 🏫 Section Management
- **Section Overview**: List all sections with teacher and enrollment information
- **Section Details**: View section-specific information and statistics
- **Search & Filter**: Find sections by name, description, or teacher

### 🗄️ Database Management
- **Database Statistics**: Table sizes, row counts, and storage usage
- **Activity Monitoring**: Recent submissions and database operations
- **Connection Status**: Real-time database health monitoring
- **Maintenance Tools**: Cleanup, backup, and performance analysis tools

### 🖥️ System Information
- **Environment Details**: Flask environment, debug mode, Python version
- **Health Checks**: Database connectivity and application status
- **System Actions**: Test connections, clear cache, view logs

## Admin Account Setup

### Method 1: Quick Setup (Recommended)
Run the setup script to automatically create admin functionality:

```bash
python setup_admin.py
```

This will create a default admin account:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@sqlclassroom.local`

### Method 2: Custom Admin Account
Create a custom admin account interactively:

```bash
python create_admin.py
```

### Method 3: Command Line Admin Creation
Create an admin account with command line arguments:

```bash
python create_admin.py username email password firstname lastname
```

### Method 4: List Existing Admins
View all existing admin accounts:

```bash
python create_admin.py --list
```

## Security Considerations

### 🔒 Important Security Notes

1. **Change Default Password**: If using the default admin account, change the password immediately after first login
2. **Secure Email**: Use a real email address for admin accounts to receive notifications
3. **Limited Access**: Admin accounts have full system access - create them sparingly
4. **Regular Audits**: Periodically review admin accounts and remove unused ones
5. **Production Environment**: Ensure debug mode is disabled in production

### 🛡️ Admin Protections

- **Role Verification**: All admin routes require admin authentication
- **Last Admin Protection**: Cannot remove the last admin account
- **Session Security**: Admin sessions use enhanced security headers
- **Audit Logging**: Admin actions are logged for security tracking

## Accessing the Admin Panel

1. **Login**: Use your admin credentials at `/login`
2. **Navigation**: Click "Admin Panel" in the navigation bar (only visible to admins)
3. **Direct Access**: Navigate directly to `/admin/dashboard`

## Admin Panel URLs

- **Dashboard**: `/admin/dashboard`
- **User Management**: `/admin/users`
- **Section Management**: `/admin/sections`
- **Database Management**: `/admin/database`
- **System Information**: `/admin/system`

## User Role Management

### Role Hierarchy
1. **Admin**: Full system access, can manage all users and data
2. **Teacher**: Can create sections, assignments, and manage students
3. **Student**: Can join sections and submit assignments

### Changing User Roles
1. Navigate to User Management
2. Click on a user to view details
3. Select new role from dropdown
4. Click "Update Role"

**Note**: You cannot remove the last admin to prevent system lockout.

## Database Management Features

### Monitoring
- Real-time database size tracking
- Table-by-table storage analysis
- Recent activity monitoring
- Connection health checks

### Maintenance (Future Features)
- Database cleanup tools
- Backup creation
- Performance optimization
- Index analysis

## Troubleshooting

### Common Issues

1. **Cannot Access Admin Panel**
   - Verify your account has admin role
   - Check if you're logged in
   - Ensure the admin blueprint is registered

2. **Setup Script Fails**
   - Check database connection
   - Verify all dependencies are installed
   - Ensure you're in the correct directory

3. **Database Connection Errors**
   - Verify database credentials in environment variables
   - Check if database server is running
   - Review connection string format

### Getting Help

1. Check the system information page for environment details
2. Review application logs for error messages
3. Verify database connectivity in the admin panel
4. Ensure all required packages are installed

## Development Notes

### File Structure
```
app/
├── routes/
│   └── admin.py           # Admin routes and logic
├── templates/
│   └── admin/             # Admin templates
│       ├── dashboard.html
│       ├── users.html
│       ├── user_detail.html
│       ├── sections.html
│       ├── database.html
│       └── system.html
└── models/
    └── user.py            # Updated with admin role support

create_admin.py            # Admin account creation script
setup_admin.py            # Quick setup script
migrations/
└── add_admin_role.py      # Database migration for admin support
```

### Extending Admin Features

To add new admin features:

1. Add routes to `app/routes/admin.py`
2. Create corresponding templates in `app/templates/admin/`
3. Update navigation in templates as needed
4. Use `@admin_required` decorator for protection

### API Endpoints

The admin panel includes API endpoints for real-time data:
- `/admin/api/stats` - Real-time system statistics

## Future Enhancements

Planned admin panel improvements:

- **Email Notifications**: Admin alerts for system events
- **Advanced Analytics**: Detailed usage reports and charts
- **Backup Management**: Automated backup scheduling
- **Log Viewer**: Built-in log file viewer
- **Performance Monitoring**: Real-time performance metrics
- **User Import/Export**: Bulk user management tools
- **System Configuration**: Web-based app configuration
- **Plugin Management**: Admin-installable extensions

## Support

For issues or questions regarding the admin panel:

1. Check this documentation first
2. Review the troubleshooting section
3. Check application logs in the system information panel
4. Verify your admin account permissions

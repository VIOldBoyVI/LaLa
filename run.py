#!/usr/bin/env python3
"""
Unified launcher for LaLaGame application
Automatically chooses between SQLite (default) and MySQL (when configured) versions
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Main function to launch the appropriate version of the application"""
    # Try to load environment variables
    load_dotenv()
    
    # Check if MySQL environment variables are configured
    mysql_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    mysql_configured = all(os.getenv(var) for var in mysql_vars)
    
    if mysql_configured:
        print("MySQL configuration detected. Launching MySQL version...")
        try:
            from app_mysql import app, init_db
            print("Initializing database...")
            init_db()
            print("Starting server...")
            app.run(
                host=os.getenv('FLASK_HOST', '0.0.0.0'),
                port=int(os.getenv('FLASK_PORT', 5555)),
                debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
            )
        except ImportError as e:
            print(f"Error importing MySQL version: {e}")
            print("Falling back to SQLite version...")
            # Continue to SQLite version
            mysql_configured = False
        except Exception as e:
            print(f"Error starting MySQL version: {e}")
            sys.exit(1)
    
    if not mysql_configured:
        print("Launching SQLite version (default)...")
        try:
            from app import app, init_db
            print("Initializing database...")
            init_db()
            print("Starting server...")
            app.run(
                host='0.0.0.0',
                port=5555,
                debug=False  # More secure for production
            )
        except ImportError as e:
            print(f"Error importing SQLite version: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error starting SQLite version: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
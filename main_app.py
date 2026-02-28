"""
Main Application - Interactive Behavioral Authentication System
"""

from user_manager import UserManager 
import sys 

class AuthenticationApp :
    """Main application for behavioral authentication system"""

    def __init__ (self ):
        self .manager =UserManager ()

    def display_menu (self ):
        """Display main menu"""
        print ("\n"+"="*60 )
        print ("🔐 AI-Based Behavioral Authentication System")
        print ("="*60 )
        print ("1. Create New User")
        print ("2. Enroll User (Create Behavioral Profile)")
        print ("3. Authenticate User (Login)")
        print ("4. List All Users")
        print ("5. Delete User")
        print ("6. View User Info")
        print ("7. Exit")
        print ("="*60 )

    def run (self ):
        """Run the application"""
        print ("\n🚀 Behavioral Authentication System Started")

        while True :
            self .display_menu ()
            choice =input ("\nSelect option (1-7): ").strip ()

            if choice =="1":
                self .create_user ()
            elif choice =="2":
                self .enroll_user ()
            elif choice =="3":
                self .authenticate_user ()
            elif choice =="4":
                self .list_users ()
            elif choice =="5":
                self .delete_user ()
            elif choice =="6":
                self .view_user_info ()
            elif choice =="7":
                print ("\n👋 Goodbye!")
                sys .exit (0 )
            else :
                print ("❌ Invalid option. Please try again.")

    def create_user (self ):
        """Create a new user"""
        username =input ("\nEnter username: ").strip ()
        if not username :
            print ("❌ Username cannot be empty")
            return 

        if self .manager .user_exists (username ):
            print (f"❌ User '{username }' already exists")
            return 

        self .manager .create_user (username )

    def enroll_user (self ):
        """Enroll a user with behavioral data"""
        username =input ("\nEnter username to enroll: ").strip ()

        if not self .manager .user_exists (username ):
            print (f"❌ User '{username }' not found. Please create user first.")
            return 

        try :
            num_sessions =int (input ("Number of sessions (default 5): ")or "5")
            session_duration =int (input ("Session duration in seconds (default 30): ")or "30")
        except ValueError :
            print ("❌ Invalid input")
            return 

        self .manager .enroll_user (username ,num_sessions ,session_duration )

    def authenticate_user (self ):
        """Authenticate a user"""
        username =input ("\nEnter username: ").strip ()

        if not self .manager .user_exists (username ):
            print (f"❌ User '{username }' not found")
            return 

        try :
            session_duration =int (input ("Session duration in seconds (default 30): ")or "30")
        except ValueError :
            print ("❌ Invalid input")
            return 

        is_authentic ,message =self .manager .authenticate_user (username ,session_duration )

    def list_users (self ):
        """List all users"""
        users =self .manager .list_users ()

        if not users :
            print ("\n📭 No users enrolled yet")
            return 

        print ("\n👥 Enrolled Users:")
        print ("-"*40 )
        for i ,user in enumerate (users ,1 ):
            print (f"{i }. {user }")
        print ("-"*40 )

    def delete_user (self ):
        """Delete a user"""
        username =input ("\nEnter username to delete: ").strip ()

        if not self .manager .user_exists (username ):
            print (f"❌ User '{username }' not found")
            return 

        confirm =input (f"Are you sure? (yes/no): ").strip ().lower ()
        if confirm !="yes":
            print ("❌ Deletion cancelled")
            return 

        self .manager .delete_user (username )

    def view_user_info (self ):
        """View user information"""
        username =input ("\nEnter username: ").strip ()

        info =self .manager .get_user_info (username )
        if info is None :
            print (f"❌ User '{username }' not found or not enrolled")
            return 

        print ("\n📋 User Information:")
        print ("-"*40 )
        for key ,value in info .items ():
            print (f"{key }: {value }")
        print ("-"*40 )

if __name__ =="__main__":
    app =AuthenticationApp ()
    app .run ()

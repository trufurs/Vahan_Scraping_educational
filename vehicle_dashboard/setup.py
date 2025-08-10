"""
Setup script for Vahan Vehicle Registration Dashboard
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def process_sample_data():
    """Process sample data"""
    try:
        subprocess.check_call([sys.executable, 'scripts/process_sample_data.py'])
        print("✅ Sample data processed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error processing data: {e}")
        return False
    return True

def main():
    print("🚗 Vahan Vehicle Registration Dashboard Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('dashboard.py'):
        print("❌ Please run this script from the vehicle_dashboard directory")
        return
    
    # Install requirements
    print("📦 Installing requirements...")
    if not install_requirements():
        return
    
    # Process sample data
    print("📊 Processing sample data...")
    if not process_sample_data():
        return
    
    print("\n🎉 Setup complete!")
    print("\nTo run the dashboard:")
    print("  streamlit run dashboard.py")
    print("\nOr double-click run_dashboard.bat")

if __name__ == "__main__":
    main()

try:
    import app as myapp
    print("[OK] app.py imported successfully")
    print("[OK] Flask app initialized:", myapp.app)
except Exception as e:
    print("[ERROR] Error importing app.py:")
    print(str(e))
    import traceback
    traceback.print_exc()

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal
import backend.app.models as m


def reset_demo_data():
    """
    Safely resets demo data while strictly preserving non-demo verified records.
    """
    db = SessionLocal()
    try:
        print("[*] Clearing only demo records (is_demo = True)...")
        # Delete demo applications, students, notifications, etc.
        db.query(m.Application).filter(m.Application.is_demo == True).delete()
        db.query(m.ResultRecord).filter(m.ResultRecord.is_demo == True).delete()
        db.query(m.TimetableEntry).filter(m.TimetableEntry.is_demo == True).delete()
        db.query(m.ExaminationEntry).filter(m.ExaminationEntry.is_demo == True).delete()
        db.query(m.Notification).filter(m.Notification.is_demo == True).delete()
        db.query(m.User).filter(m.User.is_demo == True).delete()

        db.commit()
        print("[+] Demo data reset successfully. Verified production records preserved.")
    except Exception as e:
        db.rollback()
        print(f"[-] Reset failed: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_demo_data()

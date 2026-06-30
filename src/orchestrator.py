import argparse
import sys
import time
from datetime import datetime, timedelta
import os

# Add parent directory to sys.path to allow running from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.database as db
import src.generator as gen
import src.publisher as pub

def show_queue():
    items = db.get_all_items()
    if not items:
        print("The content queue is currently empty.")
        return
        
    print(f"\n{'='*80}")
    print(f"{'ID':<4} | {'TYPE':<22} | {'STATUS':<10} | {'SCHEDULED TIME (UTC)':<20}")
    print(f"{'-'*80}")
    for item in items:
        item_id, item_type, status, scheduled_time, created_at, published_at, error_msg = item
        status_str = status.upper()
        if error_msg:
            status_str = "FAILED"
        print(f"{item_id:<4} | {item_type:<22} | {status_str:<10} | {scheduled_time[:19]:<20}")
    print(f"{'='*80}\n")

def run_scheduler_loop():
    print("Starting content automation scheduler loop...")
    print("Press Ctrl+C to stop.")
    db.init_db()
    
    # Auto-refill on start if queue is empty
    pending = [x for x in db.get_all_items() if x[2] == 'pending']
    if not pending:
        print("Queue is empty on startup. Triggering auto-refill...")
        gen.generate_daily_content()
        
    try:
        while True:
            now = datetime.utcnow()
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')} UTC] Checking queue status...")
            
            # 1. Publish due items
            pub.publish_due_items()
            
            # 2. Check if we need to auto-refill queue
            # Auto-refill if there is no pending content scheduled for the next 24 hours
            tomorrow = (now + timedelta(days=1)).isoformat()
            all_items = db.get_all_items()
            pending_soon = [
                x for x in all_items 
                if x[2] == 'pending' and x[3] <= tomorrow
            ]
            
            if len(pending_soon) == 0:
                print("Queue is running low on content. Refilling for tomorrow...")
                gen.generate_daily_content()
                
            # Sleep for 60 seconds before next check
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler loop stopped by user. Exiting.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Digital Product System Content Orchestrator CLI")
    
    parser.add_argument("--generate", action="store_true", help="Generate daily content package and queue it.")
    parser.add_argument("--publish", action="store_true", help="Publish due scheduled items immediately.")
    parser.add_argument("--queue-list", action="store_true", help="List all content queue items.")
    parser.add_argument("--scheduler", action="store_true", help="Run the continuous scheduler background loop.")
    parser.add_argument("--webhook-server", action="store_true", help="Run the FastAPI webhook server for Gumroad/Stripe sales.")
    
    args = parser.parse_args()
    
    # If no arguments passed, print help
    if not any([args.generate, args.publish, args.queue_list, args.scheduler, args.webhook_server]):
        parser.print_help()
        sys.exit(0)
        
    if args.generate:
        print("--- GENERATING DAILY CONTENT PACKAGE ---")
        success = gen.generate_daily_content()
        if success:
            print("Generation completed successfully!")
        else:
            print("Generation failed.")
            
    if args.publish:
        print("--- PUBLISHING DUE ITEMS ---")
        pub.publish_due_items()
        print("Publish run completed.")
        
    if args.queue_list:
        print("--- CURRENT CONTENT QUEUE ---")
        show_queue()
        
    if args.scheduler:
        run_scheduler_loop()

    if args.webhook_server:
        print("--- STARTING WEBHOOK SERVER ---")
        import src.webhook_server as ws
        ws.run_server()

if __name__ == "__main__":
    main()

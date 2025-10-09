from .db_utils import delete_metadata

def execute_command(action: str, params: dict | None):
    if action == "delete_image":
        image_id = params.get("image_id") if params else None
        if image_id and delete_metadata(image_id):
            return "Image deleted successfully"
        return "Image not found or invalid ID"
    
    elif action == "clear_database":
        # Example extra command: wipe all entries (use cautiously!)
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM images")
        conn.commit()
        conn.close()
        # Also delete image files if desired
        for file in os.listdir("images"):
            os.remove(os.path.join("images", file))
        return "Database cleared"
    
    else:
        return "Unknown command"

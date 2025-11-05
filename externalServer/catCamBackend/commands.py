import os
import sqlite3
from typing import Optional

from . import db_utils


def _stub_classify_image(filepath: str) -> tuple[str, float]:
    """Fallback classifier used when no ML library is wired in.
    Returns a (label, confidence) tuple. This is deterministic and cheap.
    """
    # Simple heuristic: classify by filename contents
    name = os.path.basename(filepath).lower()
    if "cat" in name:
        return "cat", 0.95
    if "dog" in name:
        return "dog", 0.9
    return "unknown", 0.5


def classify_image(image_id: int, classifier: Optional[callable] = None) -> dict:
    """Classify a single image by image_id and update DB entry.

    Returns a dict with the updated metadata or an error message.
    """
    meta = db_utils.get_metadata_by_id(image_id)
    if not meta:
        return {"error": "image not found"}

    filename = meta["filename"]
    filepath = os.path.join(db_utils.IMAGES_DIR, filename)
    if not os.path.exists(filepath):
        return {"error": "image file missing"}

    classifier = classifier or _stub_classify_image
    label, confidence = classifier(filepath)

    updated = db_utils.update_metadata(
        image_id,
        classification=label,
        classified=True,
        confidence=float(confidence)
    )
    if not updated:
        return {"error": "failed to update metadata"}

    return db_utils.get_metadata_by_id(image_id)


def classify_all(classifier: Optional[callable] = None) -> dict:
    """Classify every image in the DB that has not yet been classified.

    Returns a summary dict: { total entries: <total entries>, classified: <num processed>, errors: [..] }
    """
    classifier = classifier or _stub_classify_image
    # Query only images that are not yet classified
    unclassified = db_utils.query_images(classified=False)
    classified = db_utils.query_images(classified=True)
    results = {"total entries": len(unclassified)+len(classified), "unclassified": len(unclassified), "classified": len(classified), "errors": []}
    for item in unclassified:
        image_id = item.get("id")
        try:
            res = classify_image(image_id, classifier=classifier)
            if "error" in res:
                results["errors"].append({"id": image_id, "error": res["error"]})
            else:   
                results["unclassified"] -= 1
                results["classified"] += 1
        except Exception as e:
            results["errors"].append({"id": image_id, "error": str(e)})
    return results


def execute_command(action: str, params: dict | None = None):
    action = (action or "").lower()

    if action == "delete_image":
        image_id = params.get("image_id") if params else None
        if not image_id:
            return {"error": "image_id required"}
        ok = db_utils.delete_metadata(int(image_id))
        return {"ok": ok}

    if action == "clear_database":
        # remove DB file and images folder contents (use cautiously)
        # Clear DB table if DB exists
        try:
            conn = sqlite3.connect(db_utils.DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM images")
            conn.commit()
            conn.close()
        except Exception:
            pass

        # delete image files
        try:
            for fn in os.listdir(db_utils.IMAGES_DIR):
                os.remove(os.path.join(db_utils.IMAGES_DIR, fn))
        except FileNotFoundError:
            pass
        return {"ok": True}

    if action == "init_db":
        db_utils.init_db()
        return {"ok": True}

    if action == "insert_metadata":
        if params and "filename" in params:
            image_id = db_utils.insert_metadata(
                filename=params["filename"],
                cameraId=params.get("cameraId"),
                file_type=params.get("file_type"),
                classification=params.get("classification"),
                classified=params.get("classified", False),
                confidence=params.get("confidence")
            )
            return {"id": image_id}
        return {"error": "filename required"}

    if action == "classify_image":
        image_id = params.get("image_id") if params else None
        if not image_id:
            return {"error": "image_id required"}
        return classify_image(int(image_id))

    if action == "classify_all":
        return classify_all()

    if action == "get_image":
        image_id = params.get("image_id") if params else None
        if not image_id:
            return {"error": "image_id required"}
        meta = db_utils.get_metadata_by_id(int(image_id))
        if not meta:
            return {"error": "image not found"}
        path = db_utils.get_image_path_by_id(int(image_id))
        return {"metadata": meta, "path": path}

    if action == "get_images":
        # params can include: classified (bool), cameraId (int), since (str), before (str), limit (int)
        classified = params.get("classified") if params else None
        cameraId = params.get("cameraId") if params else None
        since = params.get("since") if params else None
        before = params.get("before") if params else None
        limit = params.get("limit") if params else None
        imgs = db_utils.query_images(classified=classified, cameraId=cameraId, since=since, before=before, limit=limit)
        # attach path
        for img in imgs:
            img["path"] = os.path.join(db_utils.IMAGES_DIR, img["filename"]) if img.get("filename") else None
        return {"images": imgs}

    return {"error": "unknown command"}



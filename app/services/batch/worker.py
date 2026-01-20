def process_batch(db, batch, files):
    results = []

    for f in files:
        results.append({
            "file_id": str(f.file_id),
            "status": "success"
        })
        batch.processed_files += 1

    batch.status = "completed"
    batch.results = results
    db.commit()

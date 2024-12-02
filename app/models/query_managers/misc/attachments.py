def get_attachments_cypher():
    return '''
    match (a:Attachment {entity_id: $entity_id})
    return 
            a.entity_id as entity_id, 
            a.filename as filename, 
            a.blob_url as blob_url, 
            a.attachment_type as attachment_type,
            a.attachment_category as attachment_category, 
            a.created_by as created_by, 
            a.created_at as created_at,
            a.uploaded_by as uploaded_by, 
            a.uploaded_at as uploaded_at
    '''


def merge_attachments():
    return '''
    MERGE (a:Attachment {entity_id: $entity_id, filename: $filename}) 
    SET 
        a.blob_url = $blob_url, 
        a.attachment_category = $attachment_category,
        a.attachment_type = $attachment_type, 
        a.created_at = COALESCE(a.created_at, datetime()),  
        a.created_by = COALESCE(a.created_by, $rms_user),  
        a.uploaded_by = $rms_user,
        a.uploaded_at = datetime()
    '''

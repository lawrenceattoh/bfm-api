# Notes only need to be created and not deleted/ edited.
# New label for notes and a slim schema.
# Helps async


def get_notes_query():
    return '''
    match (n:Note {entity_id: $entity_id, node_label:$node_label})
    return n.note as note, 
           n.created_by as created_by, 
           n.created_at as created_at
    '''


def create_note_query():
    return f'''
    create (n:Note)
    set n.note = $note, 
        n.entity_id = $entity_id, 
        n.node_label = $node_label,
        n.created_at = datetime(), 
        n.created_by = $rms_user 
    return 
        n.note as note, 
        n.created_by as created_by, 
        n.created_at as created_at
        
    '''

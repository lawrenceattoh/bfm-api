from app.models._query_manager import AbstractQueryManager


class WriterQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='w', _id='WRI', label='Writer')

    _read_one = 'match (w:Writer {id: $params.id})'

    # _read_all = 'match (w: Writer {is_deleted:False})'
    # _delete = ('match (wri: Writer) set wri.name = "DELETED_" + wri.name, '
    #            'wri.is_deleted =True, '
    #            'wri.deleted_at = datetime(), '
    #            'wri.updated_at = datetime(), '
    #            'updated_by = $rms_user')
    @property
    def _search(self):
        return '''where 
               (tolower(w.name) contains tolower($params.name) or $params.name is null) and 
               (w.ipi = $params.ipi or $params.ipi is null)'''

    # _read_all_count = 'return count(distinct w.id)'

    _create = (
        'with case when $params.ipi is null then \'223336\' else $params.ipi end as ipi '
        'with ipi '
        'merge (w:Writer {name: $params.name, ipi: ipi})')
    _create_id = ('with w '
                  'call custom.addNodeId(w, \'WRI\') yield node as _w '
                  'with w ')
    _set = ('set '
            'w.is_deleted = false,'
            'w.created_by = case when w.created_by is null then $rms_user else w.created_by end,'
            'w.created_at = case when w.created_at is null then datetime() else w.created_at end,'
            'w.updated_by = case when w.updated_by is null then $rms_user else w.updated_by end,'
            'w.updated_at = case when w.updated_at is null then datetime() else w.updated_at end,'
            'w.create_method = \'user generated\','
            'w.status = \'unvalidated\'')

    _update = ('w += $params.node_params,'
               'w.updated_at = datetime(), '
               'w.updated_by = $rms_user')

    def _return(self):
        return ('return '
                'w.id as id,'
                'w.alias as alias, '
                'w.name as name,'
                'w.ipi as ipi,') + self.add_base_params('w')

from app.models._query_manager import AbstractQueryManager


class PublisherQueryManager(AbstractQueryManager):
    _read_all_count = 'return count(distinct (p.id))'

    _order_key = 'blah'
    _read_one = 'match (p:Publisher {id: $params.id})'
    _read_all = 'match (p: Publisher {is_deleted:False})'

    _search = ('where '
               '(tolower(p.name) contains tolower($params.name) or $params.name is null) and '
               '(p.ipi = $params.ipi or $params.ipi is null)')

    _create = (
        'with case when $params.ipi is null then \'223336\' else $params.ipi end as ipi '
        'with ipi '
        'merge (w:Writer {name: $params.name, ipi: ipi})')
    _create_id = ('with w '
                  'call custom.addNodeId(w, \'PUB\') yield node as _w '
                  'with w ')
    _delete = ('match (p:Publisher {id: $params.id) '
               'set '
               'p.name="DELETED_"+ p.name, '
               'p.deleted_at = datetime(). '
               'p.updated_at = datetime(). '
               'p.updated_by = $rms_user ')
    _set = ('set '
            'p.is_deleted = false,'
            'p.created_by = case when p.created_by is null then $rms_user else p.created_by end,'
            'p.created_at = case when p.created_at is null then datetime() else p.created_at end,'
            'p.updated_by = case when p.updated_by is null then $rms_user else p.updated_by end,'
            'p.updated_at = case when p.updated_at is null then datetime() else p.updated_at end,'
            'p.create_method = \'user generated\','
            'p.status = \'unvalidated\'')

    _update = ('p += $params.node_params,'
               'p.updated_at = datetime(), '
               'p.updated_by = $rms_user')

    def _return(self):
        return ('return '
                'p.id as id,'
                'p.name as name,'
                'p.ipi as ipi,') + self.add_base_params('p')

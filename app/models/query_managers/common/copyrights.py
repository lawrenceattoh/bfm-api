from app.models._query_manager import AbstractQueryManager


class Copyright(AbstractQueryManager):
    _read_all_count = 'return count(distinct id(c))'

    _read_one = 'match (c:Copyright {name: $params.rights_type})'
    _read_all = 'match (c:Copyright {is_deleted: False})'
    _search = ''
    _create = 'merge (c:Copyright {type: $params.rights_type})'
    _create_id = ''
    _set = ('set '
            'c.is_deleted = false,'
            'c.created_by = case when c.created_by is null then $rms_user else c.created_by end,'
            'c.created_at = case when c.created_at is null then datetime() else c.created_at end,'
            'c.updated_by = case when c.updated_by is null then $rms_user else c.updated_by end,'
            'c.updated_at = case when c.updated_at is null then datetime() else c.updated_at end')
    _update = ''
    _delete = ''

    def _return(self):
        return 'return c.type' + self.add_base_params('c')  # TODO: Add attached works/ tracks

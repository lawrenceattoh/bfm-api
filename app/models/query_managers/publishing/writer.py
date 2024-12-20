from app.models._query_manager import AbstractQueryManager


class WriterQueryManager(AbstractQueryManager):

    @property
    def _search(self):
        return '''
        where 
               (tolower(wri.name) contains tolower($params.name) or $params.name is null) and 
               (wri.ipi = $params.ipi or $params.ipi is null)
        with wri
        where (
            case 
                when $params.work_id is not null 
                then exists((wri)-[:WRITTEN_BY]-(:Work {id: $params.work_id}))
                else true 
            end)
               '''

    _create = (
        'with case when $params.ipi is null then \'223336\' else $params.ipi end as ipi '
        'with ipi '
        'merge (w:Writer {name: $params.name, ipi: ipi})')

    def _return(self):
        return ('return '
                'wri.id as id,'
                'wri.alias as alias, '
                'wri.name as name,'
                'wri.ipi as ipi,') + self.add_base_params('wri')

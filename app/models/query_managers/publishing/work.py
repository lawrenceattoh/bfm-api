from app.models._query_manager import AbstractQueryManager


class WorkQueryManager(AbstractQueryManager):
    _create = (
        'with case when $params.iswc is null then \'223336\' else $params.iswc end as iswc '
        'merge (wrk: Work {name: $params.name, _shadow_iswc: iswc, _deal: $params.deal_id}) '
        'on create set '
        'wrk.iswc = case when $params.iswc <> \'\' then $params.iswc else null end '
        # 'wrk.reversion_date = case when $params.reversion_date <> \'\' then $params.reversion_date else null end, '
        # 'wrk.territories = case when $params.territories <> \'\' then $params.territories else null end'
    )

    _search = (
        'WITH wrk '
        'where ((tolower(wrk.name) contains tolower($params.name)) or $params.name is null) OR'
        '(wrk.iswc = $params.iswc) '
        'with wrk '
        'MATCH (wrk)-[:WRITTEN_BY]-(w: Writer)'
        'WHERE ('
        '    ($params.writer_id IS NULL AND $params.writer_name IS NULL) OR '
        '    ($params.writer_id IS NOT NULL AND w.id = $params.writer_id) OR '
        '    ($params.writer_name IS NOT NULL AND toLower(w.name) CONTAINS toLower($params.writer_name))'
        ')'
    )

    _with_relations = '''
    call (*) {
        unwind $params.rights as right
        match (d: Deal {id: right.deal_id})
        optional match (r: Right {id: right.right_id})
        with wrk, r, right
        
        foreach (_ in case when r is not null then [1] else [] end |
            set r += right, 
                r.updated_by = $rms_user,
                r.updated_at = datetime()
            )
        with *
        match (r)-[old:PART_OF]-()
        delete old
        merge (r)-[:PART_OF]-(d)
        return r
        }
        
    call (*) { 
        unwind $params.rights as right
        match (d: Deal {id: right.deal_id})
        optional match (r: Right {id: right.right_id})
        with wrk, r, right
        foreach (_ in case when r is null then [1] else [] end |
            create (nr:Right)
            set nr += right, 
            nr.created_by = $rms_user,
            nr.created_at = datetime(), 
            nr.is_deleted = false, 
            nr.updated_by = $rms_user,
            nr.updated_at = datetime()
            )
            merge (nr)-[:PART_OF]-(d)
            
        return collect(nr) as new_rights
        }
        unwind new_rights as nr
            call custom.addNodeId(nr, 'RGT') yield node as _nr
            merge (wrk)-[:SHARE_OWNERSHIP]-(nr)
        
    '''

    def _return(self):
        return (
            # 'with wrk '
            # 'optional match (wrk)-[:WRITTEN_BY]-(w:Writer)'
            # 'optional match (wrk)-[:SHARE_OWNERSHIP]-(r:Right)'
            # 'optional match (r)-[:BOUGHT_IN]-(d:Deal) '
            'with distinct *'
            
            'return '
            'wrk.id as id,'
            'wrk.name as name,'
            'wrk.iswc as iswc,'
            # 'collect(distinct {writer_id: w.id, writer_name: w.name, ipi: w.ipi}) as writers,'
            # 'collect(distinct {deal_id: d.id, '
            # '                   right_id: r.id, '
            # '                   right_type: r.right_type,'
            # '                   perf_share: r.perf_share, '
            # '                   is_controlled: r.is_controlled, '
            # '                   licensee: r.licensee, '
            # '                   territories: r.territories,'
            # '                    mech_share: r.mech_share}) as rights,'
        ) + self.add_base_params('wrk')

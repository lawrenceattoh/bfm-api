from app.models._query_manager import AbstractQueryManager


class WorkQueryManager(AbstractQueryManager):
    _order_key = 'wrk.name'

    _create = (
        'with case when $params.iswc is null then \'223336\' else $params.iswc end as iswc '
        'merge (wrk: Work {name: $params.name, _shadow_iswc: iswc, _deal: $params.deal_id}) '
        'on create set '
        'wrk.iswc = case when $params.iswc <> \'\' then $params.iswc else null end, '
        'wrk.reversion_date = case when $params.reversion_date <> \'\' then $params.reversion_date else null end, '
        'wrk.territories = case when $params.territories <> \'\' then $params.territories else null end'
    )

    _create_links = (
        'with wrk '
        'match (d: Deal {id: $params.deal_id}) '
        'merge (d)-[:PURCHASED_ASSET]->(wrk) '
        'merge (wrk)<-[:ROYALTY_SHARE]-(ip:IpChain) '
        'with wrk, d, ip '
        'match (wri: Writer {id: $params.writer_id}) '
        'foreach (_ in case when $params.right_type = \'publisher_share\' then [1] else [] end | '
        '    merge (p:Publisher {name: \'BELLA FIGURA MUSIC\', ipi: \'1133481777\'})-[ps:PUBLISHER_SHARE]->(ip) '
        '    set ps.perf_share = tofloat($params.ownership_pcnt), '
        '    ps.is_controlled = $params.is_controlled, '
        '    ps.deal_id = d.id, '
        '    ip.mechanical_share = case when $params.is_controlled then tofloat($params.ownership_pcnt) * 2 else ip.mechanical_share end '
        ') '
        'foreach (_ in case when $params.right_type = \'writer_share\' then [1] else [] end | '
        '    merge (wri)-[ws:WRITER_SHARE]->(ip) '
        '    set ws.perf_share = tofloat($params.ownership_pcnt), '
        '    ws.deal_id = d.id '
        ')'
    )

    _search = (
        'WITH wrk '
        'OPTIONAL MATCH (wrk)-[:ROYALTY_SHARE]-(ip:IpChain)-[:WRITER_SHARE]-(w:Writer) '
        'WITH wrk, w '
        'WHERE ('
        '    ($params.writer_id IS NULL AND $params.writer_name IS NULL) OR '
        '    ($params.writer_id IS NOT NULL AND w.id = $params.writer_id) OR '
        '    ($params.writer_name IS NOT NULL AND toLower(w.name) CONTAINS toLower($params.writer_name))'
        ')'
    )

    _with_relations = '''
        with wrk 
        call {
            match (wrk)-[pa:PURCHASED_ASSET]-(existingDeal: Deal)
            optional match (newDeal:Deal {id: $params.deal_id})
            with 
                wrk, 
                pa, 
                case when newDeal.id = existingDeal.id 
                    or newDeal is null 
                then null 
                else newDeal 
                end as modDeal 
            foreach( _ in case when modDeal is not null then [1] else [] end | 
                delete pa 
                merge (wrk)-[:PURCHASED_ASSET]-(modDeal)
            )
            return null as _
        }

        with wrk 
        call {
            with wrk 
            match (wrk)-[existingRoyaltyShare:ROYALTY_SHARE]-(existingIp:IpChain)
            match (existingIp)-[existingWriterShare:WRITER_SHARE]-(existingWriter: Writer)
            optional match (newWriter: Writer {id: $params.writer_id})
            with wrk, 
                case when 
                    $params.writer_id = existingWriter.id
                    or $params.writer_id is null
                    then null 
                    else newWriter 
                end as modWriter, 
                existingIp,
                existingWriterShare

            foreach(_ in case when modWriter is not null then [1] else [] end |  
                delete existingWriterShare
                merge (existingIp)-[:WRITER_SHARE]-(modWriter)
                set ws.perf_share = tofloat($params.ownership_pcnt),
                    ws.deal_id = $params.deal_id
            )
            return null as _
        }

        with wrk 
        call {
            with wrk 
            match (wrk)-[existingRoyaltyShare:ROYALTY_SHARE]-(existingIp:IpChain)
            match (existingIp)-[existingPublisherShare:PUBLISHER_SHARE]-(existingPublisher:Publisher)
            where $params.right_type = 'publisher_share'
            set 
                existingPublisherShare.perf_share = case when 
                    $params.ownership_pcnt is not null 
                    then tofloat($params.ownership_pcnt)
                    else existingPublisherShare.perf_share
                end,
                existingPublisherShare.is_controlled = case when
                    $params.is_controlled is not null
                    then $params.is_controlled
                    else existingPublisherShare.is_controlled
                end,
                existingPublisherShare.deal_id = $params.deal_id,
                existingIp.mechanical_share = case when 
                    $params.is_controlled and $params.ownership_pcnt is not null
                    then tofloat($params.ownership_pcnt) * 2
                    else existingIp.mechanical_share
                end
            return null as _
        }
    '''

    def _return(self):
        return (
            'with distinct wrk '
            'optional match (wrk)-[:ROYALTY_SHARE]-(ip:IpChain)-[ws:WRITER_SHARE]-(w:Writer)'
            'optional match (wrk)-[:ROYALTY_SHARE]-(ip:IpChain)-[ps:PUBLISHER_SHARE]-(p:Publisher)'
            'return '
            'wrk.id as id,'
            'wrk.name as name,'
            'wrk.iswc as iswc,'
            'wrk.reversion_date as reversion_date, '
            'wrk.territory as territory, '
            'wrk.scope as scope,'
            'collect(distinct {id: w.id, name:w.name, share:ws.perf_share, ipi:w.ipi, internal_ip_ref: id(ip), deal_id: ws.deal_id}) as writers,'
            'collect(distinct {id: p.id, name:p.name, share:ps.perf_share, ipi:p.ipi, is_controlled: p.is_controlled, mechanical_share:ip.mechanical_share, internal_ip_ref:id(ip), deal_id:ps.deal_id}) as publishers,'
        ) + self.add_base_params('wrk')
